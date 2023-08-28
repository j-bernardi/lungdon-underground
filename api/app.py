import os
from flask import Flask, request, render_template, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from api.convert import OPTIONS, conversion_formula, TYPE_KEY, TUBE_VAL

app = Flask(__name__, template_folder="templates")

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

HTML_FILE = "index.html"  # looks in folder due to line above


# TODO if putting online:
#   consider how to verify that the code being run is the version I put on github
#   E.g. how to prevent a HTML post request being sent with arbitrary parameters
#   that rewrites my function


limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # TODO consider whether exposing is security risk
    default_limits=["300 per day", "50 per hour", "20 per minute", "1 per second"],  # TODO not sure what this does as the limit must be set below also
)

"""
TODO resolve:
    /var/folders/d4/x1rdt1n9341fwyk1lglmnsg00000gn/T/zeit-fun-9bb421d64b15/flask_limiter/extension.py:308:
    UserWarning: Using the in-memory storage for tracking rate limits as no storage was explicitly specified.
    This is not recommended for production use.
    See: https://flask-limiter.readthedocs.io#configuring-a-storage-backend for documentation about configuring the storage backend.
"""


@app.route("/", methods=["GET", "POST"])
@limiter.limit("2 per second")
def index():

    RESULT_KEY = "result"  # This must match in the HTML file

    options = list(
        k for k in OPTIONS.keys() if OPTIONS[k][TYPE_KEY] == TUBE_VAL)

    if request.method == "POST":

        tube_line_select = request.form.get("tube_line_selector")
        minutes = request.form.get("minutes")

        if not (tube_line_select and minutes):
            result = f"Invalid A: {minutes} B: {tube_line_select}"

        result_tuple = conversion_formula(tube_line_select, minutes)

        session[RESULT_KEY] = prettify_results(result_tuple)

        return redirect(url_for(HTML_FILE.split(".")[0]))

    result = session.pop(RESULT_KEY, None)

    # These kwargs must match those found in the HTML file 
    return render_template(HTML_FILE, options=options, result=result)


@app.route("/about")
def about():
    return "About"


# TODO
def prettify_results(result_tuple):
    """ TODO

    Be cautious when using these methods to make sure you're not inadvertently
    making your application susceptible to Cross-Site Scripting (XSS) attacks by
    rendering user-generated or untrusted HTML content.
    """
    if any(r is None for r in result_tuple):
        return None

    result, cycle_result, holiday_result, extra_detail = result_tuple

    return_string = [f"<h2>{result:.2f} cigarettes for this trip</h2>"]

    return_string.append(
        f"That's {result * 5. * 2.:.2f} cigarettes a week, on your commute"
    )

    return_string.append(
        f"<p>If you'd cycled, that would have been {cycle_result:.2f}.</p>"
    )
    return_string.append(
        f"<p>If you'd stayed home, that would have been {holiday_result:.2f}.</p>"
    )

    if extra_detail:
        return_string.append(f"<p>{extra_detail}</p>")

    return "<br>".join(return_string)
