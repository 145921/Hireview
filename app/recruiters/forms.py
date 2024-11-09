from flask_wtf import FlaskForm
from wtforms import URLField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms import IntegerField
from wtforms import SelectField

from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import URL
from wtforms.validators import ValidationError

from ..models import Recruiter
from ..models import Organization


class JobListingForm(FlaskForm):
    title = StringField(
        "Job Title", validators=[DataRequired(), Length(max=255)]
    )
    description = TextAreaField("Job Description", validators=[DataRequired()])
    requirements = TextAreaField("Requirements", validators=[Optional()])
    responsibilities = TextAreaField(
        "Responsibilities", validators=[Optional()]
    )
    employmentType = SelectField(
        "Employment Type",
        choices=[
            ("Full-Time", "Full-Time"),
            ("Part-Time", "Part-Time"),
            ("Internship", "Internship"),
        ],
        validators=[DataRequired()],
    )
    location = StringField(
        "Location", validators=[DataRequired(), Length(max=100)]
    )
    organizationId = IntegerField(
        "Organization ID", validators=[DataRequired()]
    )
    submit = SubmitField("Save Job Listing")

    def validate_organizationId(self, field):
        if not Organization.query.get(field.data):
            raise ValidationError("Invalid organization ID.")


class UpdateJobListingForm(JobListingForm):
    submit = SubmitField("Update Job Listing")


class OrganizationForm(FlaskForm):
    description = TextAreaField("Description", validators=[DataRequired()])
    location = StringField(
        "Location", validators=[Optional(), Length(max=100)]
    )
    employees = IntegerField("Number of Employees", validators=[Optional()])
    imageUrl = URLField("Image URL", validators=[Optional(), URL()])
    recruiterId = IntegerField("Recruiter ID", validators=[Optional()])
    submit = SubmitField("Save Organization")

    def validate_recruiterId(self, field):
        if field.data and not Recruiter.query.get(field.data):
            raise ValidationError("Invalid recruiter ID.")


class UpdateOrganizationForm(OrganizationForm):
    submit = SubmitField("Update Organization")
