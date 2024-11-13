import flask
from flask_login import current_user
from flask_login import login_required

from . import recruiters
from .forms import JobListingForm
from .forms import OrganizationForm

from ..models import JobListing
from ..models import Application
from ..models import Organization

from utilities.authentication import user_type_validator


@recruiters.route("/dashboard")
@login_required
@user_type_validator("recruiter")
def dashboard():
    return flask.render_template("recruiters/dashboard.html")


@recruiters.route("/organizations/register", methods=["GET", "POST"])
@login_required
@user_type_validator("recruiter")
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
@user_type_validator("recruiter")
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
@user_type_validator("recruiter")
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
@user_type_validator("recruiter")
def view_organization(organization_id):
    organization = Organization.query.filter_by(
        organizationId=organization_id
    ).first_or_404()
    return flask.render_template(
        "recruiters/view_organization.html", organization=organization
    )


@recruiters.route("/jobs", methods=["GET"])
@login_required
@user_type_validator("recruiter")
def list_jobs():
    jobs = (
        JobListing.query.join(
            Organization,
            JobListing.organizationId == Organization.organizationId,
        )
        .filter(Organization.recruiterId == current_user.recruiterId)
        .all()
    )
    return flask.render_template("recruiters/view_jobs.html", jobs=jobs)


@recruiters.route(
    "organizations/<int:organization_id>/jobs/add", methods=["GET", "POST"]
)
@login_required
@user_type_validator("recruiter")
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
            "educationLevel": form.educationLevel.data,
            "yearsOfExperience": form.yearsOfExperience.data,
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


@recruiters.route("/jobs/<int:job_listing_id>/edit")
@login_required
@user_type_validator("recruiter")
def view_job(job_listing_id):
    job = JobListing.query.filter_by(
        jobListingId=job_listing_id
    ).first_or_404()
    return flask.render_template("recruiters/view_job.html", job=job)


@recruiters.route("/jobs/<int:job_listing_id>/update", methods=["GET", "POST"])
@login_required
@user_type_validator("recruiter")
def update_job(job_listing_id):
    # Retrieve job record
    job = JobListing.query.get_or_404(job_listing_id)

    # Instantialize Job Listing Update Form
    form = JobListingForm(obj=job)

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
            "educationLevel": form.educationLevel.data,
            "yearsOfExperience": form.yearsOfExperience.data,
        }
        # Update job listing
        job.update(details)

        # Render success message
        flask.flash("Job listing updated.", "success")
        return flask.redirect(
            flask.url_for(
                "recruiters.view_job", job_listing_id=job.jobListingId
            )
        )

    return flask.render_template(
        "recruiters/update_job.html", form=form, job=job
    )


@recruiters.route("/jobs/<int:job_listing_id>/delete", methods=["POST"])
@login_required
@user_type_validator("recruiter")
def delete_job(job_listing_id):
    # Retrieve job listing
    job = JobListing.query.get_or_404(job_listing_id)

    # Delete job listing
    job.delete()

    # Render success message
    flask.flash("Job listing deleted.", "info")
    return flask.redirect(flask.url_for("recruiters.list_jobs"))


@recruiters.route(
    "/applications/<int:application_id>/reject", methods=["POST"]
)
@login_required
@user_type_validator("recruiter")
def reject_application(application_id):
    # Retrieve application record
    application = Application.query.get_or_404(application_id)

    # Mark application as rejected
    application.reject()

    # Render success message and redirect to job profile page
    flask.flash("Email sent to applicant successfully", "success")
    return flask.redirect(
        flask.url_for(
            "recruiters.view_job",
            job_listing_id=application.job_listing.jobListingId,
        )
    )


@recruiters.route(
    "/applications/<int:application_id>/accept", methods=["POST"]
)
@login_required
@user_type_validator("recruiter")
def accept_application(application_id):
    # Retrieve application record
    application = Application.query.get_or_404(application_id)

    # Mark application as accepted
    application.accept()

    # Render success message and redirect to job profile page
    flask.flash("Email sent to applicant successfully", "success")
    return flask.redirect(
        flask.url_for(
            "recruiters.view_job",
            job_listing_id=application.job_listing.jobListingId,
        )
    )
