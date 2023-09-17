import os
import sys
print("Enter", file=sys.stderr)  # Temp
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

print("Importing", file=sys.stderr)  # Temp
from api.convert import conversion_formula
from api.tube_map import Map
print("Imported", file=sys.stderr)  # Temp

app = Flask(__name__, template_folder="templates", static_folder="static")

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

HTML_FILE = "index.html"  # looks in folder due to line above

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    # storage_uri=os.environ.get('REDIS_URI', "redis://localhost:6379"),  # TODO - sort cloud DB storage
    default_limits=["300 per day", "50 per hour", "20 per minute", "1 per second"],
    # strategy="fixed-window-elastic-expiry", TODO add back in
)


@app.route("/", methods=["GET", "POST"])
@limiter.limit("2 per second")
def index():
    try:
        print("1", file=sys.stderr)  # Temp
        tube_map_obj = Map()
        print("2", file=sys.stderr)  # Temp

        # Keys that match those in the HTML file:
        RESULT_KEY = "result"
        SELECTED_OPTION_KEY = "selected_option"
        STATION1_KEY = "station_1_option"
        STATION2_KEY = "station_2_option"

        tube_line_options = [line.name for line in tube_map_obj.lines.values()]

        if request.method == "POST":

            # TODO validate this is in the "options" dictionary and is a string with no tags
            tube_line_select = request.form.get("tube_line_selector")
            s1_select = request.form.get("station_1_selector")
            s2_select = request.form.get("station_2_selector")

            if not (tube_line_select and s1_select and s2_select):
                result = f"A: {tube_line_select}, B: {s1_select}, C: {s2_select}"

            path_between = tube_map_obj.stations_between(s1_select, s2_select, tube_line_select)
            minutes = tube_map_obj.get_time_of_path(path_between, tube_line_select)
            pm25_on_path = tube_map_obj.get_pm25_of_path(path_between, tube_line_select)
            result_tuple = conversion_formula(pm25_on_path, minutes)

            session[RESULT_KEY] = prettify_results(result_tuple)
            session[SELECTED_OPTION_KEY] = tube_line_select
            session[STATION1_KEY] = s1_select
            session[STATION2_KEY] = s2_select

            return redirect(url_for("index"))
        print("3", file=sys.stderr)  # Temp

        selected_line_option = session.pop(SELECTED_OPTION_KEY, None)  # was get
        selected_s1 = session.pop(STATION1_KEY, None)  # was get
        selected_s2 = session.pop(STATION2_KEY, None)  # was get
        result = session.pop(RESULT_KEY, None)
        print("4", file=sys.stderr)  # Temp

        if selected_line_option:
            line_id = tube_map_obj.line_name_to_id_lookup[selected_line_option]
            s1_options = list([s.name for s in tube_map_obj.lines[line_id].stations_on_line])
            s2_options = list([s.name for s in tube_map_obj.lines[line_id].stations_on_line])
        else:
            s1_options = []
            s2_options = []
        print("5", file=sys.stderr)  # Temp

        # These kwargs must match those found in the HTML file 
        return render_template(
            HTML_FILE,
            options=tube_line_options,
            s1_options=s1_options,
            s2_options=s2_options,
            result=result,
            selected_option=selected_line_option,
            s1_selected_option=selected_s1,
            s2_selected_option=selected_s2,
        )
    except Exception as e:
        print(e)


@app.route("/about")
def about():
    return "About"

@app.route('/get_stations', methods=['POST'])
def get_stations():
    tube_line = request.form['tube_line']
    tube_map_obj = Map()
    line_id = tube_map_obj.line_name_to_id_lookup[tube_line]
    station_set = tube_map_obj.lines[line_id].stations_on_line
    stations = [station.name for station in station_set]
    return jsonify(stations=stations)

def prettify_results(result_tuple):
    """ TODO

    Consider moving this straight into the HTML

    because

    Be cautious when using these methods to make sure you're not inadvertently
    making your application susceptible to Cross-Site Scripting (XSS) attacks by
    rendering user-generated or untrusted HTML content.
    """
    if any(r is None for r in result_tuple):
        return None

    result, cycle_result, urban_result, all_day_result, rod_result, extra_detail = result_tuple

    return_string = [f"<h2>{result:.2f} cigarettes smoked on this trip</h2>"]

    return_string.append(
        f"<p><strong>Cycling:</strong> if you'd cycled, that would have been {cycle_result:.2f}.</p>"
    )

    return_string.append("<p><strong>More stats if you live in London...</strong></p>")

    return_string.append(
        f"<p><strong>Staying home</strong> would have been {urban_result:.2f}. Learn more about air filtration [TODO - suggest some indoors better than others]</p>"
    )

    return_string.append(
        f"<p><strong>Your daily total</strong> is taken from {all_day_result:.2f} to {(rod_result + result):.2f} by this tube ride. "
        f"That's the price to pay for living in London!</p>"
    )

    return_string.append(
        f"<p><strong>Your weekly contribution</strong> from this commute is {result * 5. * 2.:.2f} cigarettes a week, "
        f"taking your weekly total cigarette smoking to {(rod_result + result/2) * 2 * 5 + all_day_result * 2:.2f}. "
        f"(Assuming taking this trip twice daily, 5 days a week, and not riding the tube at weekends</p>"
    )

    if extra_detail:
        return_string.append(f"<p>{extra_detail}</p>")

    return "<br>".join(return_string)
