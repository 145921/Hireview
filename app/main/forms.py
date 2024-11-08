import ipaddress

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import ValidationError

from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import Regexp
from wtforms.validators import IPAddress
from wtforms.validators import DataRequired

from ..models import User
from ..models import DHCPServer


class PasswordResetRequestForm(FlaskForm):
    emailAddress = StringField(
        "Enter your email address",
        validators=[DataRequired(), Length(1, 128), Email()],
        render_kw={"placeholder": "Enter your email address"},
    )
    submit = SubmitField("Login")


class LoginForm(FlaskForm):
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


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "Enter your Password",
        validators=[
            DataRequired(),
        ],
        render_kw={
            "autocomplete": "new-password",
            "placeholder": "Enter new password",
        },
    )
    confirmPassword = PasswordField(
        "Confirm your password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={
            "autocomplete": "new-password",
            "placeholder": "Re-enter new password",
        },
    )
    submit = SubmitField("Submit")


class UserRegistrationForm(FlaskForm):
    fullName = StringField(
        "Full Name",
        validators=[DataRequired(), Length(max=200)],
        render_kw={"placeholder": "Enter full name here"},
    )
    emailAddress = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=100)],
        render_kw={"placeholder": "Enter email address here"},
    )
    phoneNumber = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Regexp(r"^\+?1?\d{9,14}$", message="Invalid phone number format."),
        ],
        render_kw={"placeholder": "Enter phone number here"},
    )
    submit = SubmitField("Save User")

    def validate_emailAddress(self, field):
        if User.query.filter_by(emailAddress=field.data.lower()).first():
            raise ValidationError("Email address already registered.")

    def validate_phoneNumber(self, field):
        if User.query.filter_by(phoneNumber=field.data.lower()).first():
            raise ValidationError("Phone number already registered.")


class DHCPServerForm(FlaskForm):
    name = StringField("Server Name", validators=[DataRequired()])
    ip_range_start = StringField(
        "IP Range Start", validators=[DataRequired(), IPAddress()]
    )
    ip_range_end = StringField(
        "IP Range End", validators=[DataRequired(), IPAddress()]
    )
    submit = SubmitField("Add DHCP Server")

    def validate_ip_range_start(self, field):
        # Ensure the range is valid
        try:
            ip_start_int = int(ipaddress.IPv4Address(field.data))
            ip_end_int = int(ipaddress.IPv4Address(self.ip_range_end.data))

            if ip_start_int >= ip_end_int:
                raise ValidationError("Start IP must be less than End IP.")
        except ValueError:
            raise ValidationError("Invalid IP address format.")

        # Check for IP range conflict with existing DHCP servers
        existing_servers = DHCPServer.query.all()
        for server in existing_servers:
            existing_start_int = int(
                ipaddress.IPv4Address(server.ip_range_start)
            )
            existing_end_int = int(ipaddress.IPv4Address(server.ip_range_end))

            # Check if the IP range overlaps
            if (
                ip_start_int <= existing_end_int
                and ip_end_int >= existing_start_int
            ):
                raise ValidationError(
                    "IP range conflicts with existing DHCP server."
                )
