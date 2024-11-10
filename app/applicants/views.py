import flask

from . import applicants


@applicants.route("/dashboard")
def dashboard():
    return flask.render_template("applicants/dashboard.html")
