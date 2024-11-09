from wtforms import StringField
from wtforms.validators import Regexp
from wtforms.validators import DataRequired


class TelephoneField(StringField):
    def __init__(self, label="", validators=None, **kwargs):
        if validators is None:
            validators = [
                DataRequired(),
                Regexp(
                    r"^\+?\d{1,3}\d{4,14}$",
                    message="Phone number must be 10 digits e.g.,+2547xxxxxxx",
                ),
            ]

        else:
            validators.append(DataRequired())
            validators.append(
                Regexp(
                    r"^\+?\d{1,3}\d{4,14}$",
                    message="Phone number must be 10 digits e.g.,+2547xxxxxxx",
                )
            )

        super(TelephoneField, self).__init__(label, validators, **kwargs)
