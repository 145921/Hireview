from flask import Blueprint
from flask import session
from flask import current_app
from flask_cors import CORS


accounts = Blueprint("accounts", __name__)
from . import views, errors

# Enable CORS for the 'accounts' blueprint
CORS(accounts, supports_credentials=True)


@accounts.app_context_processor
def global_variables():
    """
    Provide global variables for templates within the 'accounts' blueprint.

    :return: A dictionary containing global variables to inject into templates.
    :rtype: dict

    :params: None
    """
    return dict(
        app_name=current_app.config["ORGANIZATION_NAME"],
        user_type=session.get("user_type"),
    )
