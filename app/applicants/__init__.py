from flask import Blueprint
from flask import current_app

applicants = Blueprint("applicants", __name__)
from . import views, errors


@applicants.app_context_processor
def global_variables():
    """
    Provide global variables for templates within the 'applicants' blueprint.

    :return: A dictionary containing global variables to inject into templates.
    :rtype: dict

    :params: None
    """
    return dict(
        app_name=current_app.config["ORGANIZATION_NAME"],
    )
