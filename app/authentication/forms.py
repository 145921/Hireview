from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms import TextAreaField
from wtforms import ValidationError

from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import Optional
from wtforms.validators import DataRequired

from ..models import Applicant
from ..models import Recruiter
from ..models import User

from utilities.form_fields import TelephoneField


def validate_unique_email(form, field):
    """
    Validator to ensure that the email address is unique across Applicant,
        User, and Recruiter tables.

    Raises a ValidationError if the email is already used in any table.
    """
    email_address = field.data.lower()  # Normalize to lowercase

    # Check each table for existence of the email
    applicant_exists = (
        Applicant.query.filter_by(emailAddress=email_address).first()
        is not None
    )
    user_exists = (
        User.query.filter_by(emailAddress=email_address).first() is not None
    )
    recruiter_exists = (
        Recruiter.query.filter_by(emailAddress=email_address).first()
        is not None
    )

    if applicant_exists or user_exists or recruiter_exists:
        raise ValidationError("This email address is already registered.")


class UserLoginForm(FlaskForm):
    emailAddress = StringField(
        "Enter your email address",
        validators=[DataRequired(), Length(1, 128), Email()],
        render_kw={"placeholder": "Enter your email address here"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter password"},
    )
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Login")


class ApplicantRegistrationForm(FlaskForm):
    name = StringField(
        "Enter your full name", validators=[DataRequired(), Length(1, 110)]
    )
    emailAddress = StringField(
        "Enter your email address",
        validators=[
            DataRequired(),
            Length(1, 120),
            Email(),
            validate_unique_email,
        ],
    )
    phoneNumber = TelephoneField("Enter your phone number")
    gender = SelectField(
        "Gender",
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        validators=[Optional()],
    )
    dateOfBirth = DateField(
        "Date of Birth", format="%Y-%m-%d", validators=[Optional()]
    )
    nationality = SelectField(
        "Nationality", validators=[Optional(), Length(max=50)]
    )
    preferredLocation = StringField(
        "Preferred Location", validators=[Optional(), Length(max=100)]
    )
    industries = StringField(
        "Industries", validators=[Optional(), Length(max=100)]
    )
    jobPreferences = TextAreaField(
        "Job Preferences", validators=[Optional(), Length(max=500)]
    )
    password = PasswordField(
        "Enter your Password",
        validators=[
            DataRequired(),
        ],
        render_kw={
            "autocomplete": "new-password",
        },
    )
    confirmPassword = PasswordField(
        "Confirm your password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={
            "autocomplete": "new-password",
        },
    )
    consent = BooleanField(
        "I agree to the Terms and Conditions",
        validators=[DataRequired()],
    )
    submit = SubmitField("Create Account")


class RecruiterRegistrationForm(FlaskForm):
    name = StringField(
        "Enter your full name", validators=[DataRequired(), Length(1, 110)]
    )
    gender = SelectField(
        "Select your gender",
        choices=[("Female", "Female"), ("Male", "Male")],
        validators=[DataRequired()],
    )
    nationality = SelectField(
        "Select your nationality", validators=[DataRequired()]
    )
    # Contact details
    emailAddress = StringField(
        "Enter your email address",
        validators=[
            DataRequired(),
            Length(1, 120),
            Email(),
            validate_unique_email,
        ],
    )
    phoneNumber = TelephoneField("Enter your phone number")

    # Security details
    password = PasswordField(
        "Enter your Password",
        validators=[
            DataRequired(),
        ],
        render_kw={
            "autocomplete": "new-password",
        },
    )
    confirmPassword = PasswordField(
        "Confirm your password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={"autocomplete": "new-password"},
    )

    # User consent
    consent = BooleanField(
        "I agree to all statements in Terms of service",
        validators=[DataRequired()],
    )
    submit = SubmitField("Register")

    def validate_emailAddress(self, field):
        if Recruiter.query.filter_by(emailAddress=field.data.lower()).first():
            raise ValidationError("Email address already registered.")


class UserRegistrationForm(FlaskForm):
    # Personal details
    firstName = StringField(
        "Enter first name", validators=[DataRequired(), Length(1, 50)]
    )
    middleName = StringField(
        "Enter middle name", validators=[DataRequired(), Length(1, 50)]
    )
    lastName = StringField(
        "Enter last name", validators=[DataRequired(), Length(1, 50)]
    )
    gender = SelectField(
        "Select your gender",
        choices=[("Female", "Female"), ("Male", "Male")],
        validators=[DataRequired()],
    )

    # Contact details
    emailAddress = StringField(
        "Enter your email address",
        validators=[
            DataRequired(),
            Length(1, 120),
            Email(),
            validate_unique_email,
        ],
    )
    phoneNumber = TelephoneField("Enter your phone number")

    # Security details
    password = PasswordField(
        "Enter your Password",
        validators=[
            DataRequired(),
        ],
        render_kw={
            "autocomplete": "new-password",
        },
    )
    confirmPassword = PasswordField(
        "Confirm your password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={"autocomplete": "new-password"},
    )

    # User consent
    consent = BooleanField(
        "I agree to all statements in Terms of service",
        validators=[DataRequired()],
    )
    submit = SubmitField("Register")

    def validate_emailAddress(self, field):
        if User.query.filter_by(emailAddress=field.data.lower()).first():
            raise ValidationError("Email address already registered.")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "Enter your Password",
        validators=[
            DataRequired(),
        ],
        render_kw={
            "autocomplete": "new-password",
        },
    )
    confirmPassword = PasswordField(
        "Confirm your password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={"autocomplete": "new-password"},
    )
    submit = SubmitField("Submit")
