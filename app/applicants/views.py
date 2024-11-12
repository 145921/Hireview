import flask
from flask_login import current_user

from . import applicants
from utilities.authentication import email_confirmation_required
from utilities.securities import get_eligible_job_listings_for_applicant


@applicants.before_request
@email_confirmation_required
def restrict_unconfirmed():
    pass


@applicants.route("/dashboard")
def dashboard():
    jobs = get_eligible_job_listings_for_applicant(current_user)
    return flask.render_template("applicants/dashboard.html", jobs=jobs)


@applicants.route("/jobs/applied")
def view_applied_jobs():
    jobs = get_eligible_job_listings_for_applicant(current_user)
    return flask.render_template("applicants/dashboard.html", jobs=jobs)


@applicants.route("/jobs/successful")
def view_successful_jobs():
    jobs = get_eligible_job_listings_for_applicant(current_user)
    return flask.render_template("applicants/dashboard.html", jobs=jobs)


@applicants.route("/jobs/<int:job_listing_id>/view")
def view_job(job_listing_id):
    job = JobListing.query.filter_by(
        jobListingId=job_listing_id
    ).first_or_404()
    return flask.render_template("applicants/view_job.html", job=job)
