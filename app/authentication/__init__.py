from flask import Blueprint
from flask import session
from flask import current_app
from flask_cors import CORS


authentication = Blueprint("authentication", __name__)
from . import views, errors

# Enable CORS for the 'authentication' blueprint
CORS(authentication, supports_credentials=True)


@authentication.app_context_processor
def global_variables():
    """
    Provide global variables for templates within the 'authentication' blueprint.

    :return: A dictionary containing global variables to inject into templates.
    :rtype: dict

    :params: None
    """
    return dict(
        app_name=current_app.config["ORGANIZATION_NAME"],
        user_type=session.get("user_type"),
    )
