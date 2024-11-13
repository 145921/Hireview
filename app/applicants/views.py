import os
from datetime import datetime

import flask
from flask_login import current_user
from flask_login import login_required
from werkzeug.utils import secure_filename

from app import db
from . import applicants
from .forms import ApplicationForm
from .forms import UpdateApplicantForm

from ..models import JobListing
from ..models import Application

from utilities.file_saver import allowed_file
from utilities.authentication import user_type_validator
from utilities.authentication import email_confirmation_required


@applicants.before_request
@email_confirmation_required
def restrict_unconfirmed():
    pass


@applicants.route("/dashboard")
@login_required
@user_type_validator("applicant")
def dashboard():
    jobs = JobListing.query.filter(JobListing.deadline > datetime.now()).all()
    return flask.render_template("applicants/dashboard.html", jobs=jobs)


@applicants.route("/jobs/applied")
@login_required
@user_type_validator("applicant")
def view_applied_jobs():
    return flask.render_template(
        "applicants/view_applied_jobs.html",
    )


@applicants.route("/applications/successful")
@login_required
@user_type_validator("applicant")
def view_successful_applications():
    applications = [
        application
        for application in current_user.applications
        if application.status == "Selected"
    ]
    return flask.render_template(
        "applicants/view_successful_applications.html",
        applications=applications,
    )


@applicants.route("/jobs/<int:job_listing_id>/view", methods=["GET", "POST"])
@login_required
@user_type_validator("applicant")
def view_job(job_listing_id):
    job = JobListing.query.filter_by(
        jobListingId=job_listing_id
    ).first_or_404()

    form = ApplicationForm()
    if form.validate_on_submit():
        # Save application details
        details = {
            "coverLetter": form.coverLetter.data,
            "jobListingId": job.jobListingId,
            "yearsOfExperience": form.yearsOfExperience.data,
            "applicantId": current_user.applicantId,
        }
        application = Application.create(details)

        # Save uploaded file
        file = form.resumeFile.data

        # Create folder
        folder = os.path.join(
            flask.current_app.config["APPLICATIONS_PROFILE_UPLOAD_PATH"],
            str(application.applicationId),
        )
        os.makedirs(folder, exist_ok=True)

        # Sanitize filename
        file.filename = secure_filename(file.filename)

        # Validate filename and save file
        if file and allowed_file(file.filename, ["pdf"]):
            file.save(os.path.join(folder, file.filename))

            # Save filename in the db
            application.resumeUrl = file.filename
            db.session.commit()

        # Render success message
        flask.flash("Application saved successfully", "success")
        return flask.redirect(
            flask.url_for(
                "applicants.view_job", job_listing_id=job.jobListingId
            )
        )

    return flask.render_template(
        "applicants/view_job.html", job=job, form=form
    )


@applicants.route(
    "/applications/<int:application_id>/cancel", methods=["POST"]
)
@login_required
@user_type_validator("applicant")
def cancel_application(application_id):
    # Retrieve application record
    application = Application.query.get_or_404(application_id)

    # Delete application
    application.delete()

    # Render success message
    flask.flash("Application cancelled successfully", "success")
    return flask.redirect(flask.url_for("applicants.dashboard"))


@applicants.route(
    "applications/<int:application_id>/update_resume", methods=["POST"]
)
@login_required
@user_type_validator("applicant")
def update_resume(application_id):
    # Retrieve application record
    application = Application.query.get_or_404(application_id)

    # Save new resume file
    file = flask.request.files.get("resumeFile")

    if file and allowed_file(file.filename, ["pdf"]):
        folder = os.path.join(
            flask.current_app.config["APPLICATIONS_PROFILE_UPLOAD_PATH"],
            str(application.applicationId),
        )
        os.makedirs(folder, exist_ok=True)

        # Sanitize filename
        new_filename = secure_filename(file.filename)
        new_file_path = os.path.join(folder, new_filename)

        # Only replace if save is successful
        try:
            file.save(new_file_path)

            # Delete old resume file if it exists
            old_file_path = os.path.join(folder, str(application.resumeUrl))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

            # Update database with new resume filename
            application.resumeUrl = new_filename
            db.session.commit()

            # Render success message
            flask.flash("Resume updated successfully", "success")

        except Exception:
            flask.flash("Failed to update resume. Please try again.", "error")
    else:
        flask.flash(
            "Invalid file format. Only PDF files are allowed.", "error"
        )

    return flask.redirect(
        flask.url_for(
            "applicants.view_job", job_listing_id=application.jobListingId
        )
    )


@applicants.route(
    "/applications/<int:application_id>/update_cover_letter", methods=["POST"]
)
@login_required
@user_type_validator("applicant")
def update_cover_letter(application_id):
    # Retrieve application record
    application = Application.query.get_or_404(application_id)

    # Update cover letter directly
    new_cover_letter = flask.request.form.get("coverLetter")
    if new_cover_letter:
        # Save cover letter in database
        application.coverLetter = new_cover_letter
        db.session.commit()

        # Render success message
        flask.flash("Cover letter updated successfully", "success")

    else:
        flask.flash("Cover letter update failed. Please try again.", "error")

    return flask.redirect(
        flask.url_for(
            "applicants.view_job", job_listing_id=application.jobListingId
        )
    )


@applicants.route("/manage_profile", methods=["GET", "POST"])
@login_required
def manage_profile():
    # Instantiate each form
    profile_form = UpdateApplicantForm(obj=current_user)
    profile_form.csrf_token.render_kw = {"id": "profile_csrf"}

    if profile_form.validate_on_submit():
        # Update applicant profile logic
        flask.flash("Applicant information updated successfully.", "success")
        return flask.redirect(flask.url_for("applicants.manage_profile"))

    # Render the template with all forms
    return flask.render_template(
        "applicants/manage_profile.html",
        profile_form=profile_form,
    )
