import flask
import iso3166
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

    # Retrieve list of countries
    countries_list = [
        ((country.name), (country.name)) for country in iso3166.countries
    ]
    form.nationality.choices = countries_list

    if form.validate_on_submit():
        # Retrieve form details
        details = {
            "name": form.name.data,
            "emailAddress": form.emailAddress.data.lower(),
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
            "gender": form.gender.data,
            "dateOfBirth": form.dateOfBirth.data,
            "nationality": form.nationality.data,
            "preferredLocation": form.preferredLocation.data,
            "industries": form.industries.data,
            "jobPreferences": form.jobPreferences.data,
        }

        # Save applicant details
        Applicant.registerAccount(details)

        # Render success message
        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("authentication.login"))

    return flask.render_template(
        "authentication/applicant_registration.html", form=form
    )


@authentication.route("/user/register", methods=["GET", "POST"])
def user_registration():
    form = UserRegistrationForm()

    if form.validate_on_submit():
        # Retrieve user form details
        details = {
            "name": form.name.data,
            "middleName": form.middleName.data,
            "lastName": form.lastName.data,
            "gender": form.gender.data,
            "emailAddress": form.emailAddress.data,
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }

        # Save user details in the database
        User.registerAccount(details)

        # Render success message
        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("authentication.login"))

    return flask.render_template(
        "authentication/user_registration.html", form=form
    )


@authentication.route("/recruiter/register", methods=["GET", "POST"])
def recruiter_registration():
    form = RecruiterRegistrationForm()

    # Retrieve list of countries
    countries_list = [
        ((country.name), (country.name)) for country in iso3166.countries
    ]
    form.nationality.choices = countries_list

    if form.validate_on_submit():
        # Retrieve recruiter form details
        details = {
            "name": form.name.data,
            "emailAddress": form.emailAddress.data,
            "nationality": form.nationality.data,
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }

        # Save recruiter details in database
        Recruiter.registerAccount(details)

        # Render success message
        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("authentication.login"))

    return flask.render_template(
        "authentication/recruiter_registration.html", form=form
    )


# ------------------------------------------------------------------------------
#                                SIGNING OUT                                  -
# ------------------------------------------------------------------------------
@authentication.route("/logout")
@login_required
def logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.")
    return flask.redirect(flask.url_for("authentication.login"))


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
            return flask.redirect(flask.url_for("authentication.login"))

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
            return flask.redirect(flask.url_for("authentication.login"))

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
            return flask.redirect(flask.url_for("authentication.login"))

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")
    return flask.render_template(
        "authentication/password_reset.html", form=form
    )


# -----------------------------------------------------------------------------
#                           ACCOUNT CONFIRMATION                              -
# -----------------------------------------------------------------------------
def confirm_user(user_type, user_id, token):
    """Helper function to confirm email address for any user type."""
    template = "authentication/confirmation.html"

    # Select model based on user type
    user_model = {
        "applicant": Applicant,
        "user": User,
        "recruiter": Recruiter,
    }.get(user_type)

    # Validate user model
    if not user_model:
        return flask.render_template(template, invalid_token=True)

    # Retrieve user and confirm token
    user = user_model.query.get(user_id)
    if not user:
        return flask.render_template(template, invalid_token=True)

    if user.isVerified:
        flask.flash("Your email is already confirmed", "warning")
        return flask.redirect(flask.url_for("authentication.login"))

    if user.confirm(token):
        db.session.commit()
        flask.flash("Email confirmed successfully!", "success")
        return flask.redirect(flask.url_for("authentication.login"))

    # If token is invalid or expired
    return flask.render_template(template, invalid_token=True)


@authentication.route("/applicant/confirm/<int:applicant_id>/<token>")
def applicant_confirm(applicant_id, token):
    return confirm_user("applicant", applicant_id, token)


@authentication.route("/user/confirm/<int:user_id>/<token>")
def user_confirm(user_id, token):
    return confirm_user("user", user_id, token)


@authentication.route("/recruiter/confirm/<int:recruiter_id>/<token>")
def recruiter_confirm(recruiter_id, token):
    return confirm_user("recruiter", recruiter_id, token)


@authentication.route("/resend-confirmation-email")
@login_required
@user_type_validator("recruiter")
def resend_confirmation_email():
    current_user.sendConfirmationEmail()
    flask.flash("A new confirmation email has been sent to you via email")
    return flask.redirect(flask.url_for("authentication.confirm_email"))


@authentication.route("/unconfirmed")
@login_required
def confirm_email():
    if current_user.is_anonymous:
        return flask.redirect(flask.url_for("main.index"))

    elif current_user.isVerified:
        return flask.redirect(flask.url_for("authentication.login"))
    print(current_user.isVerified)
    return flask.render_template("authentication/confirm_email.html")


# ---------------------------------------------------------------------------
#                          HANDLE STALE SESSIONS                            -
# ---------------------------------------------------------------------------
@authentication.route("/reauthenticate")
@login_required
def reauthenticate():
    return flask.redirect(flask.url_for("authentication.logout"))
