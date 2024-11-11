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
