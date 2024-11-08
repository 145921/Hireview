import flask
from flask_login import current_user
from flask_login import login_required


from . import accounts
from .forms import UserLoginForm
from .forms import ApplicantLoginForm
from .forms import RecruiterLoginForm
from .forms import PasswordResetForm
from .forms import UserRegistrationForm
from .forms import ApplicantRegistrationForm
from .forms import RecruiterRegistrationForm

from ..models import db
from ..models import User
from ..models import Applicant
from ..models import Recruiter

from utilities.authentication import user_type_validator


# ------------------------------------------------------------------------------
#                                 SIGNING IN                                  -
# ------------------------------------------------------------------------------
@accounts.route("/user/login", methods=["GET", "POST"])
def user_login():
    # Limit functionality to Anonymous Users
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("administrators.dashboard"))

    form = UserLoginForm()

    if form.validate_on_submit():
        # Find user with given email address
        user = User.query.filter_by(
            emailAddress=form.emailAddress.data.lower()
        ).first()

        # Login user if found
        details = {
            "password": form.password.data,
            "remember_me": form.remember_me.data,
        }

        if user:
            success, message = user.login(details)

            if success:
                next = flask.request.args.get("next")
                if not next or not next.startswith("/"):
                    next = flask.url_for("administrators.dashboard")

                flask.flash(f"Hello {current_user.firstName}. Welcome back!")
                return flask.redirect(next)

        # Notify user of invalid credentials
        flask.flash("You provided invalid credentials. Please try again.")

    return flask.render_template("accounts/user_login.html", form=form)


@accounts.route("/applicant/login", methods=["GET", "POST"])
def applicant_login():
    # Limit functionality to Anonymous Users
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("applicants.dashboard"))

    form = ApplicantLoginForm()

    if form.validate_on_submit():
        details = {
            "password": form.password.data,
            "remember_me": form.remember_me.data,
        }

        # Find user with given email address
        applicant = Applicant.query.filter_by(
            emailAddress=form.emailAddress.data.lower()
        ).first()

        # Login user if found
        if applicant:
            success, message = applicant.login(details)

            if success:
                next = flask.request.args.get("next")
                if not next or not next.startswith("/"):
                    next = flask.url_for("applicants.dashboard")

                flask.flash(f"Hello {current_user.fullName}. Welcome back!")
                return flask.redirect(next)

        # Notify user of invalid credentials
        flask.flash("You provided invalid credentials. Please try again.")

    return flask.render_template("accounts/applicant_login.html", form=form)


@accounts.route("/recruiter/login", methods=["GET", "POST"])
def recruiter_login():
    # Limit functionality to Anonymous Users
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("recruiters.dashboard"))

    form = RecruiterLoginForm()

    if form.validate_on_submit():
        details = {
            "password": form.password.data,
            "remember_me": form.remember_me.data,
        }

        # Find user with given email address
        recruiter = Recruiter.query.filter_by(
            emailAddress=form.emailAddress.data.lower()
        ).first()

        # Login user if found
        if recruiter:
            success, message = recruiter.login(details)

            if success:
                next = flask.request.args.get("next")
                if not next or not next.startswith("/"):
                    next = flask.url_for("recruiters.dashboard")

                flask.flash(f"Hello {current_user.firstName}. Welcome back!")
                return flask.redirect(next)

        # Notify user of invalid credentials
        flask.flash("You provided invalid credentials. Please try again.")

    return flask.render_template("accounts/recruiter_login.html", form=form)


# ------------------------------------------------------------------------------
#                                REGISTRATION                                 -
# ------------------------------------------------------------------------------
@accounts.route("/applicant/register", methods=["GET", "POST"])
def applicant_registration():
    form = ApplicantRegistrationForm()

    if form.validate_on_submit():
        details = {
            "fullName": form.fullName.data,
            "emailAddress": form.emailAddress.data.lower(),
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }
        Applicant.registerAccount(details)

        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("accounts.applicant_login"))

    return flask.render_template(
        "accounts/applicant_registration.html", form=form
    )


@accounts.route("/user/register", methods=["GET", "POST"])
def user_registration():
    form = UserRegistrationForm()

    if form.validate_on_submit():
        details = {
            "firstName": form.firstName.data,
            "middleName": form.middleName.data,
            "lastName": form.lastName.data,
            "gender": form.gender.data,
            "emailAddress": form.emailAddress.data,
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }
        User.registerAccount(details)

        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("accounts.user_login"))

    return flask.render_template("accounts/user_registration.html", form=form)


@accounts.route("/recruiter/register", methods=["GET", "POST"])
def recruiter_registration():
    form = RecruiterRegistrationForm()

    if form.validate_on_submit():
        details = {
            "firstName": form.firstName.data,
            "middleName": form.middleName.data,
            "lastName": form.lastName.data,
            "gender": form.gender.data,
            "emailAddress": form.emailAddress.data,
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }
        Recruiter.registerAccount(details)

        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("accounts.recruiter_login"))

    return flask.render_template(
        "accounts/recruiter_registration.html", form=form
    )


# ------------------------------------------------------------------------------
#                                SIGNING OUT                                  -
# ------------------------------------------------------------------------------
@accounts.route("/applicant/logout")
@login_required
@user_type_validator("applicant")
def applicant_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.")
    return flask.redirect(flask.url_for("accounts.applicant_login"))


@accounts.route("/user/logout")
@login_required
@user_type_validator("user")
def administrator_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.")
    return flask.redirect(flask.url_for("accounts.user_login"))


@accounts.route("/recruiter/logout")
@login_required
@user_type_validator("recruiter")
def recruiter_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.")
    return flask.redirect(flask.url_for("accounts.recruiter_login"))


# ------------------------------------------------------------------------------
#                           PASSWORD RESET REQUEST                            -
# ------------------------------------------------------------------------------
@accounts.route("/applicant/password-reset-request", methods=["GET", "POST"])
def applicant_password_reset_request():
    if flask.request.method == "POST":
        # Retrieve applicant
        email_address = flask.request.form["email"]
        applicant = Applicant.query.filter_by(
            emailAddress=email_address
        ).first()

        # Check if applicant exists
        if applicant:
            # Send password reset email
            applicant.sendPasswordResetEmail()

            # Flash success message
            flask.flash("Password reset email sent successfully")
            return flask.redirect(
                flask.url_for("accounts.applicant_password_reset_request")
            )

        # Flash error message
        flask.flash("The provided email address is invalid", "failure")

    return flask.render_template("accounts/password_reset_request.html")


@accounts.route("/user/password-reset-request", methods=["GET", "POST"])
def user_password_reset_request():
    if flask.request.method == "POST":
        # Retrieve user
        email_address = flask.request.form["email"]
        user = User.query.filter_by(emailAddress=email_address).first()

        # Check if user exists
        if user:
            # Send password reset email
            user.sendPasswordResetEmail()

            # Flash success message
            flask.flash("Password reset email sent successfully")
            return flask.redirect(
                flask.url_for("accounts.user_password_reset_request")
            )

        # Flash error message
        flask.flash("The provided email address is invalid", "failure")

    return flask.render_template("accounts/password_reset_request.html")


@accounts.route("/recruiter/password-reset-request", methods=["GET", "POST"])
def recruiter_password_reset_request():
    if flask.request.method == "POST":
        # Retrieve recruiter
        email_address = flask.request.form["email"]
        recruiter = Recruiter.query.filter_by(
            emailAddress=email_address
        ).first()

        # Check if recruiter exists
        if recruiter:
            # Send password reset email
            recruiter.sendPasswordResetEmail()

            # Flash success message
            flask.flash("Password reset email sent successfully")
            return flask.redirect(
                flask.url_for("accounts.applicant_password_reset_request")
            )

        # Flash error message
        flask.flash("The provided email address is invalid", "failure")

    return flask.render_template("accounts/password_reset_request.html")


# -----------------------------------------------------------------------------
#                               PASSWORD RESET                              -
# -----------------------------------------------------------------------------
@accounts.route("/applicant/password-reset/<token>", methods=["GET", "POST"])
def applicant_password_reset(token):
    # Functionality limited to stranded applicants
    if not current_user.is_anonymous:
        return flask.redirect(flask.url_for("applicants.dashboard"))

    # Handle form rendering and submission
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Reset applicant's password
        successful = Applicant.resetPassword(token, form.password.data)

        # Handle successful reset
        if successful:
            flask.flash("Password updated successfully")
            return flask.redirect(flask.url_for("accounts.applicant_login"))

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")

    return flask.render_template("accounts/password_reset.html", form=form)


@accounts.route("/user/password-reset/<token>", methods=["GET", "POST"])
def user_password_reset(token):
    # Functionality limited to stranded users
    if not current_user.is_anonymous:
        return flask.redirect(flask.url_for("users.dashboard"))

    # Handle form rendering and submission
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Reset user's password
        successful = User.resetPassword(token, form.password.data)

        # Handle successful reset
        if successful:
            flask.flash("Password updated successfully")
            return flask.redirect(flask.url_for("accounts.user_login"))

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")
    return flask.render_template("accounts/password_reset.html", form=form)


@accounts.route("/recruiter/password-reset/<token>", methods=["GET", "POST"])
def recruiter_password_reset(token):
    # Functionality limited to stranded recruiters
    if not current_user.is_anonymous:
        return flask.redirect(flask.url_for("recruiters.dashboard"))

    # Handle form rendering and submission
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Reset recruiter's password
        successful = Recruiter.resetPassword(token, form.password.data)

        # Handle successful reset
        if successful:
            flask.flash("Password updated successfully")
            return flask.redirect(flask.url_for("accounts.recruiter_login"))

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")
    return flask.render_template("accounts/password_reset.html", form=form)


# -----------------------------------------------------------------------------
#                           ACCOUNT CONFIRMATION                              -
# -----------------------------------------------------------------------------
@accounts.route("/recruiter/confirm/<int:recruiter_id>/<token>")
def recruiter_confirm(recruiter_id, token):
    """
    Confirms email address of registered recruiter
    :param recruiter_id: int - Recruiter id for the recruiter being confirmed.
    :param token: str - Serialized string containing recruiter information.

    :return: Bool - True if successful, False otherwise.
    """
    template = "accounts/confirmation.html"

    # Retrieve specified recruiter
    current_user = Recruiter.query.get(recruiter_id)
    if not current_user:
        return flask.render_template(template, invalid_token=True)

    if current_user.isConfirmed:
        return flask.render_template(template, user_already_confirmed=True)

    confirmation_result = current_user.confirm(token)

    if confirmation_result:
        return flask.render_template(template, success=True)
    else:
        return flask.render_template(template, invalid_token=True)


@accounts.route("/applicant/confirm/<int:applicant_id>/<token>")
def applicant_confirm(applicant_id, token):
    """Confirms email address of registered applicant"""
    template = "authentication/confirmation.html"

    # Retrieve specified applicant
    current_user = Applicant.query.get(applicant_id)
    if not current_user:
        return flask.render_template(template, invalid_token=True)

    if current_user.isConfirmed:
        return flask.render_template(template, user_already_confirmed=True)

    confirmation_result = current_user.confirm(token)

    if confirmation_result:
        db.session.commit()
        return flask.render_template(template, success=True)
    else:
        return flask.render_template(template, invalid_token=True)


@accounts.route("/user/confirm/<int:user_id>/<token>")
def user_confirm(user_id, token):
    """Confirms email address of registered user"""
    template = "authentication/confirmation.html"

    # Retrieve specified recruiter
    current_user = User.query.get(user_id)
    if not current_user:
        return flask.render_template(template, invalid_token=True)

    if current_user.isConfirmed:
        return flask.render_template(template, user_already_confirmed=True)

    confirmation_result = current_user.confirm(token)

    if confirmation_result:
        db.session.commit()
        return flask.render_template(template, success=True)
    else:
        return flask.render_template(template, invalid_token=True)


@accounts.route("/resend-confirmation-link/recruiter")
@login_required
@user_type_validator("recruiter")
def resend_confirmation_link_recruiter():
    current_user.sendConfirmationEmail()
    flask.flash("A new confirmation email has been sent to you via email")
    return flask.redirect(flask.url_for("accounts.unconfirmed_recruiter"))


@accounts.route("/unconfirmed/recruiter")
@login_required
@user_type_validator("recruiter")
def unconfirmed_recruiter():
    if current_user.is_anonymous:
        return flask.redirect(flask.url_for("main.index"))

    elif current_user.isConfirmed:
        return flask.redirect(flask.url_for("recruiters.dashboard"))

    return flask.render_template("accounts/unconfirmed.html")


# ---------------------------------------------------------------------------
#                          HANDLE STALE SESSIONS                            -
# ---------------------------------------------------------------------------
@accounts.route("/reauthenticate")
@login_required
def reauthenticate():
    user = flask.session["user_type"]
    return flask.redirect(flask.url_for(f"accounts.{user}_logout"))
