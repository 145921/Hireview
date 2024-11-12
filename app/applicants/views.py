import os

import flask
from flask_login import current_user
from werkzeug.utils import secure_filename

from app import db
from . import applicants
from .forms import ApplicationForm
from ..models import JobListing
from ..models import Application

from utilities.file_saver import allowed_file
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
    return flask.render_template(
        "applicants/view_applied_jobs.html",
    )


@applicants.route("/applications/successful")
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
