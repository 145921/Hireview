import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask security configuration options
    SECRET_KEY = os.environ.get("SECRET_KEY") or "Ustbuvrth66}6chjebvhreueurb"

    # SQLAlchemy configuration options
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5

    # Application configuration options
    ORGANIZATION_NAME = os.environ.get("ORGANIZATION_NAME") or "Hireview"

    # File upload configuration options
    RECRUITERS_PROFILE_UPLOAD_PATH = os.path.join(
        basedir + "/app/static/custom/recruiters/"
    )
    USERS_PROFILE_UPLOAD_PATH = os.path.join(
        basedir + "/app/static/custom/users/"
    )
    ORGANIZATIONS_PROFILE_UPLOAD_PATH = os.path.join(
        basedir + "/app/static/custom/organizations/"
    )
    APPLICATIONS_PROFILE_UPLOAD_PATH = os.path.join(
        basedir + "/app/static/custom/applications/"
    )
    APPLICANTS_PROFILE_UPLOAD_PATH = os.path.join(
        basedir + "/app/static/custom/applicants/"
    )

    # Mail connection configuration options
    MAIL_BACKEND = "smtp"
    MAIL_SERVER = "smtp.zoho.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_TIMEOUT = None

    # Mail Credentials Settings
    MAIL_DEFAULT_SENDER = "HireView <info@jisortublow.co.ke>"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "info@jisortublow.co.ke")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "phOhsj3-")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEVELOPMENT_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "hiring.db")


class TestingConfig(Config):
    TESTING = True
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory"
    )


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    SESSION_COOKIE_SECURE = True

    DB_NAME = os.environ.get("DB_NAME") or "hiring"
    DB_USERNAME = os.environ.get("DB_USERNAME") or "root"
    DB_HOST = os.environ.get("DB_HOST") or "localhost"
    DB_PASSWORD = os.environ.get("DB_PASSWORD") or "MySQLXXX-123a8910"

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("PRODUCTION_DATABASE_URL")
        or f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}"
        + f"/{DB_NAME}"
    )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
