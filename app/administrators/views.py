import flask
from flask_login import login_required

from . import administrators

from ..models import Recruiter
from ..models import JobListing


@administrators.route("/dashboard")
@login_required
def dashboard():
    recruiters = Recruiter.query.all()
    return flask.render_template(
        "administrators/dashboard.html", recruiters=recruiters
    )


@administrators.route(
    "/recruiter/<int:recruiter_id>/approve", methods=["POST"]
)
@login_required
def approve_recruiter(recruiter_id):
    # Retrieve recruiter record
    recruiter = Recruiter.query.get_or_404()

    # Approve recruiter
    recruiter.approve()

    # Render success message
    flask.flash("Recruiter approved.", "success")
    return flask.redirect(flask.url_for("administrators.dashboard"))


@administrators.route("/recruiter/<int:recruiter_id>/reject", methods=["POST"])
@login_required
def reject_recruiter(recruiter_id):
    # Retrieve recruiter record
    recruiter = Recruiter.query.get_or_404()

    # Disapprove recruiter
    recruiter.reject()

    # Render success message
    flask.flash("Recruiter disapproved.", "info")
    return flask.redirect(flask.url_for("administrators.dashboard"))


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
