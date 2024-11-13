from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import SelectField
from wtforms import IntegerField
from wtforms import TextAreaField
from wtforms import DateTimeField

from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import NumberRange
from wtforms.validators import DataRequired


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
    category = SelectField(
        "Category",
        validators=[Optional(), Length(max=120)],
        choices=[
            ("Software Development", "Software Development"),
            (
                "Engineering (Civil, Mechanical, Electrical)",
                "Engineering (Civil, Mechanical, Electrical)",
            ),
            ("Data Science and Analytics", "Data Science and Analytics"),
            (
                "Information Technology (IT) and Systems",
                "Information Technology (IT) and Systems",
            ),
            ("Marketing and Communications", "Marketing and Communications"),
            (
                "Human Resources (HR) and Talent Acquisition",
                "Human Resources (HR) and Talent Acquisition",
            ),
            (
                "Sales and Business Development",
                "Sales and Business Development",
            ),
            ("Finance and Accounting", "Finance and Accounting"),
            (
                "Customer Support and Client Services",
                "Customer Support and Client Services",
            ),
            ("Operations and Supply Chain", "Operations and Supply Chain"),
            ("Product Management", "Product Management"),
            ("Project Management", "Project Management"),
            ("Legal and Compliance", "Legal and Compliance"),
            ("Healthcare and Nursing", "Healthcare and Nursing"),
            ("Education and Training", "Education and Training"),
            ("Design and Creative Services", "Design and Creative Services"),
            (
                "Manufacturing and Quality Control",
                "Manufacturing and Quality Control",
            ),
            ("Administrative Support", "Administrative Support"),
            (
                "Research and Development (R&D)",
                "Research and Development (R&D)",
            ),
            (
                "Environmental and Sustainability",
                "Environmental and Sustainability",
            ),
            ("Construction and Real Estate", "Construction and Real Estate"),
            ("Consulting and Strategy", "Consulting and Strategy"),
            ("Other", "Other"),
        ],
    )

    educationLevel = SelectField(
        "Education Level",
        choices=[
            ("High School Diploma", "High School Diploma"),
            ("Associate Degree", "Associate Degree"),
            ("Bachelor's Degree", "Bachelor's Degree"),
            ("Master's Degree", "Master's Degree"),
            ("Doctorate", "Doctorate"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )
    yearsOfExperience = IntegerField(
        "Years of Experience",
        validators=[
            Optional(),
            NumberRange(min=0, message="Must be a non-negative number"),
        ],
    )
    location = StringField(
        "Location", validators=[Optional(), Length(max=120)]
    )
    deadline = DateField("Deadline", validators=[Optional()])
    submit = SubmitField("Save Job Listing")


class PlacementRequestRegistrationForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    course = StringField(
        "Course", validators=[DataRequired(), Length(max=255)]
    )
    description = TextAreaField("Description", validators=[Optional()])
    position = StringField(
        "Position", validators=[DataRequired(), Length(max=255)]
    )
    deadline = DateField("Deadline", validators=[Optional()])
    location = StringField(
        "Location", validators=[Optional(), Length(max=120)]
    )
    placementType = SelectField(
        "Placement Type",
        validators=[DataRequired(), Length(max=120)],
        choices=[
            ("Internship", "Internship"),
            ("Co-op", "Co-op"),
            ("Apprenticeship", "Apprenticeship"),
            ("Part-time Placement", "Part-time Placement"),
            ("Full-time Placement", "Full-time Placement"),
            ("Remote", "Remote"),
            ("On-site", "On-site"),
            ("Hybrid", "Hybrid"),
            ("Volunteer", "Volunteer"),
            ("Project-based", "Project-based"),
            ("Freelance/Contract", "Freelance/Contract"),
            ("Traineeship", "Traineeship"),
            ("Externship", "Externship"),
            ("Other", "Other"),
        ],
    )
    category = SelectField(
        "Category",
        validators=[DataRequired(), Length(max=120)],
        choices=[
            ("Software Development", "Software Development"),
            (
                "Engineering (Civil, Mechanical, Electrical)",
                "Engineering (Civil, Mechanical, Electrical)",
            ),
            ("Data Science and Analytics", "Data Science and Analytics"),
            (
                "Information Technology (IT) and Systems",
                "Information Technology (IT) and Systems",
            ),
            ("Marketing and Communications", "Marketing and Communications"),
            (
                "Human Resources (HR) and Talent Acquisition",
                "Human Resources (HR) and Talent Acquisition",
            ),
            (
                "Sales and Business Development",
                "Sales and Business Development",
            ),
            ("Finance and Accounting", "Finance and Accounting"),
            (
                "Customer Support and Client Services",
                "Customer Support and Client Services",
            ),
            ("Operations and Supply Chain", "Operations and Supply Chain"),
            ("Product Management", "Product Management"),
            ("Project Management", "Project Management"),
            ("Legal and Compliance", "Legal and Compliance"),
            ("Healthcare and Nursing", "Healthcare and Nursing"),
            ("Education and Training", "Education and Training"),
            ("Design and Creative Services", "Design and Creative Services"),
            (
                "Manufacturing and Quality Control",
                "Manufacturing and Quality Control",
            ),
            ("Administrative Support", "Administrative Support"),
            (
                "Research and Development (R&D)",
                "Research and Development (R&D)",
            ),
            (
                "Environmental and Sustainability",
                "Environmental and Sustainability",
            ),
            ("Construction and Real Estate", "Construction and Real Estate"),
            ("Consulting and Strategy", "Consulting and Strategy"),
            ("Other", "Other"),
        ],
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
