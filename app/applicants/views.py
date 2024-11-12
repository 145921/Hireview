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

        # Ensure file is allowed
        folder = os.path.join(
            flask.current_app.config["APPLICATIONS_PROFILE_UPLOAD_PATH"],
            str(application.applicationId),
        )

        # Sanitize filename
        file.filename = secure_filename(file.filename)

        # Validate filename and save file
        if file and allowed_file(file.filename, [".pdf"]):
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
