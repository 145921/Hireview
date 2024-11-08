import flask
from flask_login import login_required

from . import administrators

from ..models import Recruiter
from ..models import JobListing


@administrators.route("/dashboard")
@login_required
def dashboard():
    return flask.render_template("administrators/dashboard.html")


@administrators.route("/recruiters")
@login_required
def view_recruiters():
    recruiters = Recruiter.query.all()
    return flask.render_template(
        "administrators/recruiters.html", recruiters=recruiters
    )


@administrators.route(
    "/recruiter/<int:recruiter_id>/approve", methods=["POST"]
)
@login_required
def approve_recruiter(recruiter_id):
    # Approve recruiter
    flask.flash("Recruiter approved.", "success")
    return flask.redirect(flask.url_for("administrators.view_recruiters"))


@administrators.route(
    "/recruiter/<int:recruiter_id>/disapprove", methods=["POST"]
)
@login_required
def disapprove_recruiter(recruiter_id):
    # Disapprove recruiter
    flask.flash("Recruiter disapproved.", "info")
    return flask.redirect(flask.url_for("administrators.view_recruiters"))


@administrators.route("/recruiters/report/download", methods=["GET"])
@login_required
def download_recruiters_report():
    # Generate and download report
    return flask.send_file("path/to/recruiters_report.pdf", as_attachment=True)


@administrators.route("/jobs")
@login_required
def view_jobs():
    jobs = JobListing.query.all()
    return flask.render_template("administrators/jobs.html", jobs=jobs)
