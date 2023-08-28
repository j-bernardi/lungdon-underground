import os
from flask import Flask, request, render_template, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__, template_folder="templates")

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

DEFAULT_LIMITS = ["300 per day", "50 per hour", "20 per minute", "1 per second"]

HTML_FILE = "index.html"  # looks in folder due to line above

# TODO data in here. Maybe colour, and definitely formula parameters
# TODO create a standard data structure
OPTIONS = {
    "Victoria": {"mult": 5},
    "Northern": {"mult": 4},
    "Picadilly": {"mult": 3},
    "Hammersmith and City": {"mult": 1},
}


limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=DEFAULT_LIMITS,
)


@app.route("/", methods=["GET", "POST"])
@limiter.limit("2 per second")
def index():

    options = list(OPTIONS.keys())

    if request.method == "POST":

        tube_line_select = request.form.get("tube_line_selector")
        minutes = request.form.get("minutes")

        if not (tube_line_select and minutes):
            result = f"Invalid A: {minutes} B: {tube_line_select}"

        result = formula(tube_line_select, minutes)

        session["result"] = result

        return redirect(url_for("index"))

    result = session.pop("result", None)
    return render_template(HTML_FILE, options=options, result=result)


@app.route("/about")
def about():
    return 'About'


def formula(tube_line, minutes_spent):

    if not tube_line:
        return ""
    elif tube_line not in OPTIONS:
        result = "Invalid option"

    try:
        mins = int(minutes_spent)
    except:
        return "Invalid minutes: must be integer"

    result = mins * OPTIONS[tube_line]["mult"]
    
    return result
