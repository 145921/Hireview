from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import SelectField
from wtforms import TextAreaField
from wtforms import DateTimeField

from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional


class JobListingForm(FlaskForm):
    title = StringField(
        "Job Title", validators=[DataRequired(), Length(max=100)]
    )
    position = StringField(
        "Position", validators=[DataRequired(), Length(max=100)]
    )
    workingMethod = SelectField(
        "Working Method",
        choices=[
            ("onsite", "On-Site"),
            ("offsite", "Off-Site"),
            ("hybrid", "Hybrid"),
        ],
        validators=[DataRequired()],
    )
    description = TextAreaField("Job Description", validators=[DataRequired()])
    category = StringField(
        "Category", validators=[Optional(), Length(max=100)]
    )
    location = StringField(
        "Location", validators=[Optional(), Length(max=100)]
    )
    deadline = DateTimeField(
        "Application Deadline", format="%Y-%m-%d", validators=[Optional()]
    )
    submit = SubmitField("Save Job Listing")


class UpdateJobListingForm(JobListingForm):
    submit = SubmitField("Update Job Listing")


class OrganizationForm(FlaskForm):
    name = StringField("Name", validators=[Length(max=255)])
    description = TextAreaField("Description", validators=[DataRequired()])
    location = StringField(
        "Location", validators=[Optional(), Length(max=100)]
    )
    employees = StringField("Number of Employees", validators=[Optional()])
    submit = SubmitField("Save Organization")


class UpdateOrganizationForm(OrganizationForm):
    submit = SubmitField("Update Organization")
