import flask
from flask_login import current_user
from flask_login import login_required

from . import recruiters
from .forms import JobListingForm
from .forms import OrganizationForm

from ..models import Applicant
from ..models import JobListing
from ..models import Organization
from utilities.authentication import email_confirmation_required


@recruiters.before_request
@email_confirmation_required
def restrict_unconfirmed():
    pass


@recruiters.route("/dashboard")
@login_required
def dashboard():
    return flask.render_template("recruiters/dashboard.html")


@recruiters.route("/organization/register", methods=["GET", "POST"])
@login_required
def register_organization():
    form = OrganizationForm()
    if form.validate_on_submit():
        # Register organization profile
        flask.flash("Organization profile registered.", "success")
        return flask.redirect(flask.url_for("recruiters.dashboard"))
    return flask.render_template(
        "recruiters/register_organization.html", form=form
    )


@recruiters.route("/organization/<int:org_id>/update", methods=["GET", "POST"])
@login_required
def update_organization(org_id):
    organization = Organization.query.get_or_404(org_id)
    form = OrganizationForm(obj=organization)
    if form.validate_on_submit():
        # Update organization profile
        flask.flash("Organization profile updated.", "success")
        return flask.redirect(flask.url_for("recruiters.dashboard"))
    return flask.render_template(
        "recruiters/update_organization.html",
        form=form,
        organization=organization,
    )


@recruiters.route("/organization/<int:org_id>/delete", methods=["POST"])
@login_required
def delete_organization(org_id):
    # Delete organization profile
    flask.flash("Organization profile deleted.", "info")
    return flask.redirect(flask.url_for("recruiters.dashboard"))


@recruiters.route("/jobs", methods=["GET"])
@login_required
def list_jobs():
    jobs = JobListing.query.filter_by(recruiter_id=current_user.id).all()
    return flask.render_template("recruiters/jobs.html", jobs=jobs)


@recruiters.route("/job/add", methods=["GET", "POST"])
@login_required
def add_job():
    form = JobListingForm()
    if form.validate_on_submit():
        # Add job listing
        flask.flash("Job listing added.", "success")
        return flask.redirect(flask.url_for("recruiters.list_jobs"))
    return flask.render_template("recruiters/add_job.html", form=form)


@recruiters.route("/job/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    job = JobListing.query.get_or_404(job_id)
    form = JobListingForm(obj=job)
    if form.validate_on_submit():
        # Update job listing
        flask.flash("Job listing updated.", "success")
        return flask.redirect(flask.url_for("recruiters.list_jobs"))
    return flask.render_template(
        "recruiters/edit_job.html", form=form, job=job
    )


@recruiters.route("/job/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    # Delete job listing
    flask.flash("Job listing deleted.", "info")
    return flask.redirect(flask.url_for("recruiters.list_jobs"))


@recruiters.route("/job/<int:job_id>/close", methods=["POST"])
@login_required
def close_job(job_id):
    # Close job listing
    flask.flash("Job listing closed.", "info")
    return flask.redirect(flask.url_for("recruiters.list_jobs"))


@recruiters.route("/job/<int:job_id>/applications", methods=["GET"])
@login_required
def view_job_applications(job_id):
    applications = Applicant.query.filter_by(job_id=job_id).all()
    return flask.render_template(
        "recruiters/view_job_applications.html", applications=applications
    )


@recruiters.route(
    "/job/<int:job_id>/select-applicant/<int:applicant_id>", methods=["POST"]
)
@login_required
def select_applicant(job_id, applicant_id):
    # Select most eligible applicant
    flask.flash("Applicant selected and notified.", "success")
    return flask.redirect(
        flask.url_for("recruiters.view_job_applications", job_id=job_id)
    )
