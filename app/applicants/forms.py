from wtforms import DateField
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import SelectField
from wtforms import DateTimeField
from wtforms import TextAreaField

from wtforms.validators import URL
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import Regexp
from wtforms.validators import Optional
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError

from ..models import Applicant


class ApplicantRegistrationForm(FlaskForm):
    fullName = StringField(
        "Full Name", validators=[DataRequired(), Length(max=200)]
    )
    email = StringField(
        "Email Address", validators=[DataRequired(), Length(max=100), Email()]
    )
    phoneNumber = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Regexp(r"^\+?1?\d{9,15}$", message="Invalid phone number format."),
        ],
    )
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    resumeUrl = StringField("Resume URL", validators=[Optional(), URL()])
    submit = SubmitField("Register Applicant")

    def validate_email(self, field):
        if Applicant.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Email address already registered.")

    def validate_phoneNumber(self, field):
        if Applicant.query.filter_by(phoneNumber=field.data).first():
            raise ValidationError("Phone number already registered.")


class UpdateApplicantForm(ApplicantRegistrationForm):
    submit = SubmitField("Update Applicant Information")


class EducationForm(FlaskForm):
    degree = StringField(
        "Degree", validators=[DataRequired(), Length(max=100)]
    )
    institution = StringField(
        "Institution", validators=[Optional(), Length(max=100)]
    )
    startDate = DateField("Start Date", validators=[Optional()])
    endDate = DateField("End Date", validators=[Optional()])
    issueDate = DateField("Issue Date", validators=[Optional()])
    documentUrl = StringField("Document URL", validators=[Optional(), URL()])
    submit = SubmitField("Save Education Entry")


class UpdateEducationForm(EducationForm):
    submit = SubmitField("Update Education Entry")


class ExperienceForm(FlaskForm):
    position = StringField(
        "Position", validators=[DataRequired(), Length(max=100)]
    )
    institution = StringField(
        "Institution", validators=[Optional(), Length(max=100)]
    )
    description = TextAreaField("Description", validators=[Optional()])
    startDate = DateField("Start Date", validators=[Optional()])
    endDate = DateField("End Date", validators=[Optional()])
    reasonOfTermination = StringField(
        "Reason of Termination", validators=[Optional(), Length(max=255)]
    )
    submit = SubmitField("Save Experience Entry")


class UpdateExperienceForm(ExperienceForm):
    submit = SubmitField("Update Experience Entry")


class JobListingForm(FlaskForm):
    title = StringField(
        "Job Title",
        validators=[DataRequired(), Length(max=100)],
        render_kw={"placeholder": "Enter job title here"},
    )
    position = StringField(
        "Position",
        validators=[DataRequired(), Length(max=100)],
        render_kw={"placeholder": "Enter position here"},
    )
    workingMethod = SelectField(
        "Working Method",
        choices=[
            ("onsite", "Onsite"),
            ("offsite", "Offsite"),
            ("hybrid", "Hybrid"),
        ],
        validators=[DataRequired()],
    )
    description = TextAreaField(
        "Job Description",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter job description here"},
    )
    category = StringField(
        "Category",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Enter job category here"},
    )
    location = StringField(
        "Location",
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Enter location here"},
    )
    deadline = DateTimeField(
        "Application Deadline",
        validators=[Optional()],
        render_kw={"placeholder": "Enter deadline here (YYYY-MM-DD HH:MM:SS)"},
    )
    submit = SubmitField("Save Job Listing")
