import flask
from flask_login import current_user
from flask_login import login_required


from . import authentication
from .forms import UserLoginForm
from .forms import PasswordResetForm
from .forms import UserRegistrationForm
from .forms import ApplicantRegistrationForm
from .forms import RecruiterRegistrationForm

from app import db
from ..models import User
from ..models import Applicant
from ..models import Recruiter

from utilities.authentication import user_type_validator


def redirect_after_login(dashboard_route, name):
    next_page = flask.request.args.get("next")
    if not next_page or not next_page.startswith("/"):
        next_page = flask.url_for(dashboard_route)

    flask.flash(f"Hello {name}. Welcome back!")
    return flask.redirect(next_page)


def redirect_based_on_role():
    # Redirect based on user type of the current user
    if isinstance(current_user._get_current_object(), User):
        return flask.redirect(flask.url_for("administrators.dashboard"))

    elif isinstance(current_user._get_current_object(), Applicant):
        return flask.redirect(flask.url_for("applicants.dashboard"))

    elif isinstance(current_user._get_current_object(), Recruiter):
        return flask.redirect(flask.url_for("recruiters.dashboard"))

    else:
        return flask.redirect(flask.url_for("authentication.login"))


@authentication.route("/login", methods=["GET", "POST"])
def login():
    # Redirect already logged-in users to their respective dashboards
    if current_user.is_authenticated:
        return redirect_based_on_role()

    form = UserLoginForm()

    if form.validate_on_submit():
        email = form.emailAddress.data.lower()
        password = form.password.data
        remember_me = form.remember_me.data

        # Try to find the user in each user table (User, Applicant, Recruiter)
        user = User.query.filter_by(emailAddress=email).first()
        applicant = (
            Applicant.query.filter_by(emailAddress=email).first()
            if not user
            else None
        )
        recruiter = (
            Recruiter.query.filter_by(emailAddress=email).first()
            if not (user or applicant)
            else None
        )

        # Attempt login for each user type and redirect accordingly
        if (
            user
            and user.login({"password": password, "remember_me": remember_me})[
                0
            ]
        ):
            return redirect_after_login("administrators.dashboard", user.name)

        if (
            applicant
            and applicant.login(
                {"password": password, "remember_me": remember_me}
            )[0]
        ):
            return redirect_after_login("applicants.dashboard", applicant.name)

        if (
            recruiter
            and recruiter.login(
                {"password": password, "remember_me": remember_me}
            )[0]
        ):
            return redirect_after_login("recruiters.dashboard", recruiter.name)

        # Flash message if credentials are invalid for any user type
        flask.flash("You provided invalid credentials. Please try again.")

    return flask.render_template("authentication/login.html", form=form)


# ------------------------------------------------------------------------------
#                                REGISTRATION                                 -
# ------------------------------------------------------------------------------
@authentication.route("/applicant/register", methods=["GET", "POST"])
def applicant_registration():
    form = ApplicantRegistrationForm()

    if form.validate_on_submit():
        details = {
            "name": form.name.data,
            "emailAddress": form.emailAddress.data.lower(),
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }
        Applicant.registerAccount(details)

        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("authentication.applicant_login"))

    return flask.render_template(
        "authentication/applicant_registration.html", form=form
    )


@authentication.route("/user/register", methods=["GET", "POST"])
def user_registration():
    form = UserRegistrationForm()

    if form.validate_on_submit():
        details = {
            "name": form.name.data,
            "middleName": form.middleName.data,
            "lastName": form.lastName.data,
            "gender": form.gender.data,
            "emailAddress": form.emailAddress.data,
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }
        User.registerAccount(details)

        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("authentication.user_login"))

    return flask.render_template(
        "authentication/user_registration.html", form=form
    )


@authentication.route("/recruiter/register", methods=["GET", "POST"])
def recruiter_registration():
    form = RecruiterRegistrationForm()

    if form.validate_on_submit():
        details = {
            "name": form.name.data,
            "middleName": form.middleName.data,
            "lastName": form.lastName.data,
            "gender": form.gender.data,
            "emailAddress": form.emailAddress.data,
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }
        Recruiter.registerAccount(details)

        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("authentication.recruiter_login"))

    return flask.render_template(
        "authentication/recruiter_registration.html", form=form
    )


# ------------------------------------------------------------------------------
#                                SIGNING OUT                                  -
# ------------------------------------------------------------------------------
@authentication.route("/applicant/logout")
@login_required
@user_type_validator("applicant")
def applicant_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.")
    return flask.redirect(flask.url_for("authentication.applicant_login"))


@authentication.route("/user/logout")
@login_required
@user_type_validator("user")
def administrator_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.")
    return flask.redirect(flask.url_for("authentication.user_login"))


@authentication.route("/recruiter/logout")
@login_required
@user_type_validator("recruiter")
def recruiter_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.")
    return flask.redirect(flask.url_for("authentication.recruiter_login"))


# ------------------------------------------------------------------------------
#                           PASSWORD RESET REQUEST                            -
# ------------------------------------------------------------------------------
@authentication.route("/password-reset-request", methods=["GET", "POST"])
def password_reset_request():
    if flask.request.method == "POST":
        # Retrieve the email address from the form
        email_address = flask.request.form["email"].lower()

        # Try to find the user in any of the user tables (User, Applicant,
        # Recruiter)
        user = User.query.filter_by(emailAddress=email_address).first()
        applicant = (
            Applicant.query.filter_by(emailAddress=email_address).first()
            if not user
            else None
        )
        recruiter = (
            Recruiter.query.filter_by(emailAddress=email_address).first()
            if not (user or applicant)
            else None
        )

        # If a user of any type is found, send the password reset email
        if user:
            user.sendPasswordResetEmail()
            flask.flash("Password reset email sent successfully.")
            return flask.redirect(
                flask.url_for("authentication.password_reset_request")
            )
        elif applicant:
            applicant.sendPasswordResetEmail()
            flask.flash("Password reset email sent successfully.")
            return flask.redirect(
                flask.url_for("authentication.password_reset_request")
            )
        elif recruiter:
            recruiter.sendPasswordResetEmail()
            flask.flash("Password reset email sent successfully.")
            return flask.redirect(
                flask.url_for("authentication.password_reset_request")
            )

        # If no user is found, flash an error message
        flask.flash("The provided email address is invalid.", "failure")

    return flask.render_template("authentication/password_reset_request.html")


# -----------------------------------------------------------------------------
#                               PASSWORD RESET                              -
# -----------------------------------------------------------------------------
@authentication.route(
    "/applicant/password-reset/<token>", methods=["GET", "POST"]
)
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
            return flask.redirect(
                flask.url_for("authentication.applicant_login")
            )

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")

    return flask.render_template(
        "authentication/password_reset.html", form=form
    )


@authentication.route("/user/password-reset/<token>", methods=["GET", "POST"])
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
            return flask.redirect(flask.url_for("authentication.user_login"))

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")
    return flask.render_template(
        "authentication/password_reset.html", form=form
    )


@authentication.route(
    "/recruiter/password-reset/<token>", methods=["GET", "POST"]
)
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
            return flask.redirect(
                flask.url_for("authentication.recruiter_login")
            )

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")
    return flask.render_template(
        "authentication/password_reset.html", form=form
    )


# -----------------------------------------------------------------------------
#                           ACCOUNT CONFIRMATION                              -
# -----------------------------------------------------------------------------
@authentication.route("/recruiter/confirm/<int:recruiter_id>/<token>")
def recruiter_confirm(recruiter_id, token):
    """
    Confirms email address of registered recruiter
    :param recruiter_id: int - Recruiter id for the recruiter being confirmed.
    :param token: str - Serialized string containing recruiter information.

    :return: Bool - True if successful, False otherwise.
    """
    template = "authentication/confirmation.html"

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


@authentication.route("/applicant/confirm/<int:applicant_id>/<token>")
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


@authentication.route("/user/confirm/<int:user_id>/<token>")
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


@authentication.route("/resend-confirmation-link/recruiter")
@login_required
@user_type_validator("recruiter")
def resend_confirmation_link_recruiter():
    current_user.sendConfirmationEmail()
    flask.flash("A new confirmation email has been sent to you via email")
    return flask.redirect(
        flask.url_for("authentication.unconfirmed_recruiter")
    )


@authentication.route("/unconfirmed/recruiter")
@login_required
@user_type_validator("recruiter")
def unconfirmed_recruiter():
    if current_user.is_anonymous:
        return flask.redirect(flask.url_for("main.index"))

    elif current_user.isConfirmed:
        return flask.redirect(flask.url_for("recruiters.dashboard"))

    return flask.render_template("authentication/unconfirmed.html")


# ---------------------------------------------------------------------------
#                          HANDLE STALE SESSIONS                            -
# ---------------------------------------------------------------------------
@authentication.route("/reauthenticate")
@login_required
def reauthenticate():
    user = flask.session["user_type"]
    return flask.redirect(flask.url_for(f"authentication.{user}_logout"))
