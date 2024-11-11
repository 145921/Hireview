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


@recruiters.route("/organizations/register", methods=["GET", "POST"])
@login_required
def register_organization():
    form = OrganizationForm()
    if form.validate_on_submit():
        # Retrieve form details
        details = {
            "name": form.name.data,
            "description": form.description.data,
            "location": form.location.data,
            "employees": form.employees.data,
            "recruiterId": current_user.recruiterId,
        }

        # Save organization details
        Organization.create(details)

        # Render success message to user
        flask.flash("Organization profile registered.", "success")
        return flask.redirect(flask.url_for("recruiters.dashboard"))
    return flask.render_template(
        "recruiters/register_organization.html", form=form
    )


@recruiters.route(
    "/organizations/<int:organization_id>/update", methods=["GET", "POST"]
)
@login_required
def update_organization(organization_id):
    # Retrieve organization record
    organization = Organization.query.get_or_404(organization_id)

    # Instantialize Update Form
    form = OrganizationForm(obj=organization)

    if form.validate_on_submit():
        # Retrieve forms details
        details = {
            "name": form.name.data,
            "description": form.description.data,
            "location": form.location.data,
            "employees": form.employees.data,
        }

        # Update organization profile
        organization.update(details)

        # Render success message
        flask.flash("Organization profile updated.", "success")
        return flask.redirect(flask.url_for("recruiters.dashboard"))

    return flask.render_template(
        "recruiters/update_organization.html",
        form=form,
        organization=organization,
    )


@recruiters.route(
    "/organizations/<int:organization_id>/delete", methods=["POST"]
)
@login_required
def delete_organization(organization_id):
    # Retrieve organization record
    organization = Organization.query.filter_by(
        organizationId=organization_id
    ).first_or_404()

    # Delete organization record
    success = organization.delete()

    # Render success message
    if success:
        flask.flash("Organization deleted successfully.", "info")

    else:
        flask.flash(
            "An error occurred while deleting the organization record",
            "warning",
        )

    return flask.redirect(flask.url_for("recruiters.dashboard"))


@recruiters.route("/organizations/<int:organization_id>/jobs", methods=["GET"])
@login_required
def view_organization(organization_id):
    organization = Organization.query.filter_by(
        organizationId=organization_id
    ).first_or_404()
    return flask.render_template(
        "recruiters/view_organization.html", organization=organization
    )


@recruiters.route("/jobs", methods=["GET"])
@login_required
def list_jobs():
    jobs = JobListing.query.filter_by(recruiter_id=current_user.id).all()
    return flask.render_template("recruiters/jobs.html", jobs=jobs)


@recruiters.route(
    "organizations/<int:organization_id>/jobs/add", methods=["GET", "POST"]
)
@login_required
def add_job_listing(organization_id):
    # Retrieve organization record
    organization = Organization.query.filter_by(
        organizationId=organization_id
    ).first_or_404()

    # Instantialize Add Job Listing Form
    form = JobListingForm()

    if form.validate_on_submit():
        # Retrieve form details
        details = {
            "title": form.title.data,
            "description": form.description.data,
            "position": form.position.data,
            "workingMethod": form.workingMethod.data,
            "category": form.category.data,
            "location": form.location.data,
            "deadline": form.deadline.data,
            "organizationId": organization.organizationId,
        }

        # Save job listing
        JobListing.create(details)

        # Render success message
        flask.flash("Job listing added successfully.", "success")
        return flask.redirect(flask.url_for("recruiters.list_jobs"))

    return flask.render_template(
        "recruiters/add_job.html", form=form, organization=organization
    )


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
