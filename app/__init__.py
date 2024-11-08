import flask
import flask_login
import flask_moment
import flask_mailman
import flask_bootstrap
import flask_sqlalchemy
import flask_jwt_extended

from config import config

# Set endpoint for the login page
login_manager = flask_login.LoginManager()
login_manager.blueprint_login_views = {
    "administrators": "authentication.administrator_login",
    "applicants": "authentication.applicant_login",
    "recruiters": "authentication.recruiter_login",
    "authentication": "authentication.applicant_login",
    "main": "authentication.applicant_login",
}

# Handle stale sessions
login_manager.refresh_view = "authentication.reauthenticate"
login_manager.needs_refresh_message = (
    "To protect your authentication, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    from .models import Recruiter
    from .models import Applicant

    user_type = flask.session.get("user_type")
    if user_type == "applicant":
        user = Applicant.query.get(int(user_id))

    elif user_type == "recruiter":
        user = Recruiter.query.get(int(user_id))

    elif user_type == "user":
        user = User.query.get(int(user_id))

    else:
        user = None

    return user


db = flask_sqlalchemy.SQLAlchemy()
jwt = flask_jwt_extended.JWTManager()
mail = flask_mailman.Mail()
bootstrap = flask_bootstrap.Bootstrap()
moment = flask_moment.Moment()


def create_app(config_name="default"):
    """
    Initialize and configure the Flask application.

    :param config_name: str - The name of the configuration class defined in
        config.py.

    :return app: Flask - The configured Flask application instance.
    """
    app = flask.Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    # Enable SSL redirection if configured
    if app.config["SSL_REDIRECT"]:
        from flask_sslify import SSLify

        SSLify(app)

    # Register blueprints for different parts of the application
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .authentication import authentication as authentication_blueprint

    app.register_blueprint(authentication_blueprint, url_prefix="/authentication")

    from .applicants import applicants as applicants_blueprint

    app.register_blueprint(applicants_blueprint, url_prefix="/applicant")

    from .administrators import administrators as administrators_blueprint

    app.register_blueprint(
        administrators_blueprint, url_prefix="/administrator"
    )

    from .recruiters import recruiters as recruiters_blueprint

    app.register_blueprint(recruiters_blueprint, url_prefix="/recruiter")

    return app
