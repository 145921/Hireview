import os

import flask
import flask_login
from flask import url_for

from app import db
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from utilities.file_saver import save_image
from utilities.file_saver import delete_file

from utilities.email_utils import send_email
from utilities.securities import get_gravatar_hash


class User(flask_login.UserMixin, db.Model):
    """
    Model representing a User in the system.
    """

    __tablename__ = "User"

    userId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    emailAddress = db.Column(db.String(100), nullable=False, unique=True)
    phoneNumber = db.Column(db.String(20), unique=True)
    passwordHash = db.Column(db.String(255), nullable=False)
    avatarHash = db.Column(db.String(255))
    isActive = db.Column(db.Boolean, default=True, nullable=False)
    isVerified = db.Column(db.Boolean, default=False, nullable=False)
    dateCreated = db.Column(db.DateTime, default=db.func.current_timestamp())
    lastUpdated = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        # Generate the avatar hash
        if self.emailAddress is not None and self.avatarHash is None:
            self.avatarHash = get_gravatar_hash(self.emailAddress)

    def __repr__(self) -> str:
        return f"User(userId={self.userId}, emailAddress={self.emailAddress})"

    @classmethod
    def registerAccount(cls, details: dict) -> "User":
        """
        Create a new user.

        :param details: dict - Details of the user to be created.
        :return: User - The newly created user instance.
        """
        user = cls(
            name=details.get("name"),
            emailAddress=details.get("emailAddress"),
            phoneNumber=details.get("phoneNumber"),
            passwordHash=details.get("passwordHash"),
            avatarHash=details.get("avatarHash"),
            isActive=details.get("isActive", True),
            isVerified=details.get("isVerified", False),
        )
        db.session.add(user)
        db.session.commit()
        return user

    def update(self, details: dict) -> "User":
        """
        Update user details.

        :param details: dict - A dictionary of details to update.
        :return: User - The updated user instance.
        """
        self.name = details.get("name", self.name)
        self.emailAddress = details.get("emailAddress", self.emailAddress)
        self.phoneNumber = details.get("phoneNumber", self.phoneNumber)
        self.passwordHash = details.get("passwordHash", self.passwordHash)
        self.avatarHash = details.get("avatarHash", self.avatarHash)
        self.isActive = details.get("isActive", self.isActive)
        self.isVerified = details.get("isVerified", self.isVerified)
        db.session.commit()
        return self

    def delete(self) -> None:
        """
        Delete the user.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()

    def get_id(self) -> int:
        """
        Inherited UserMixin class method used to retrieve user id for
        flask_login

        :return: int - User ID of the user.
        """
        return self.userId

    def login(self, details=dict()) -> tuple:
        """
        Logs in the user and marks them as online.

        :param details: dict - Contains password and remember_me boolean
        variable

        :return: tuple - Contains the return status and return message.
        """

        if self.verifyPassword(details.get("password", "")):
            flask_login.login_user(self, details.get("remember_me", False))

            # Set user type session variable
            flask.session.permanent = True
            flask.session["user_type"] = "user"

            return (1, "Login Successful")

        return (0, "Invalid password")

    def logout(self) -> tuple:
        """
        Logs out the user and updates their last seen timestamp.

        :return: tuple - Contains return status and return message.
        """
        # Logout user
        flask_login.logout_user()

        return (1, "Logout successful")

    @property
    def password(self) -> AttributeError:
        """
        Raise an AttributeError since the password is private only
        """
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password) -> None:
        """
        Hash the user's password
        """
        self.passwordHash = generate_password_hash(password)

    def generateConfirmationToken(self) -> str:
        """
        Generate a confirmation token.

        This method generates a token for confirming the user's email address.

        :return: str - The confirmation token.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        return serializer.dumps(self.emailAddress)

    def sendPasswordResetEmail(self) -> None:
        """
        Send a password reset email to the user.
        """
        token = self.generateConfirmationToken()
        reset_link = url_for(
            "authentication.password_reset",
            token=token,
            _scheme="https",
            _external=True,
        )

        subject = "Password Reset Request"
        send_email(
            [self.emailAddress],
            subject,
            "email/password_reset",
            user=self,
            reset_link=reset_link,
        )

    @staticmethod
    def confirmPasswordResetToken(token, expiration=3600):
        """
        Validate password request link provided.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])

        try:
            data = serializer.loads(token, max_age=expiration)
            user = User.query.filter_by(emailAddress=data).first()

            return user

        except Exception:
            return None

    @staticmethod
    def resetPassword(token, new_password, expiration=3600):
        """
        Reset user's password.

        :param token: str - the token for password reset.
        :param new_password: str - the new password.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token, expiration)

        except Exception:
            return False

        user = User.query.filter_by(emailAddress=data).first()
        if user is None:
            return False

        user.password = new_password
        db.session.commit()

        return True

    def deleteProfileImage(self) -> None:
        """
        Deletes user's profile image.
        """
        # Delete actual file from the file system
        file_path = os.path.join(
            flask.current_app.config["USERS_PROFILE_UPLOAD_PATH"],
            self.imageURL,
        )
        os.remove(file_path)

        # Update the same on the database
        self.imageURL = None
        db.session.commit()

    def updateProfileImage(self, image) -> "User":
        """
        Update user's profile image.

        :param image: FileStorage - the image file to be uploaded.

        :return self: User - the updated User instance.
        """
        # Delete the old image if it exists
        if self.imageURL:
            delete_file(
                os.path.join(
                    flask.current_app.config["USERS_PROFILE_UPLOAD_PATH"],
                    self.imageURL,
                )
            )

        # Save image on file system
        saved_filename = save_image(
            image, flask.current_app.config["USERS_PROFILE_UPLOAD_PATH"]
        )

        # Save filename in database
        self.imageURL = saved_filename
        db.session.add(self)
        db.session.commit()

        return self

    def activateAccount(self) -> None:
        """
        Activate the user's account.
        """
        if self.isActive:
            return

        self.isActive = True
        db.session.commit()

        # Notify user on account activation via email
        subject = "Account Activation"
        send_email(
            [self.emailAddress],
            subject,
            "email/account_activation",
            user=self,
        )

    def deactivateAccount(self) -> None:
        """
        Deactivate the user's account.
        """
        if not self.isActive:
            return

        self.isActive = False
        db.session.commit()

        # Notify user on account deactivation via email
        subject = "Account Deactivation"
        send_email(
            [self.emailAddress],
            subject,
            "email/account_deactivation",
            user=self,
        )

    def verifyPassword(self, password: str) -> bool:
        """
        Verify the provided password with the stored hash.

        :param password: str - The password to verify.
        :return: bool - True if the password matches, False otherwise.
        """
        return check_password_hash(self.passwordHash, password)

    def updatePassword(self, current_password, new_password):
        """
        Updates user's password.

        :param current_password: str - User's current password.
        :param new_password: str - User's new password.

        :return self: User - the updated User instance.
        """
        if self.verifyPassword(current_password):
            self.password = new_password
            db.session.commit()
            return self

        return

    def getGravatar(self, size=100, default="identicon", rating="g"):
        """
        Generates a Gravatar URL for the user based on their email address.

        :param size: int - The size of the Gravatar image.
        :param default: str - The default image to be displayed if no
        Gravatar is found.
        :param rating: str - The content rating for the image.

        :return: str - The Gravatar URL.
        """
        url = "https://secure.gravatar.com/avatar"

        # Generate avatar hash if it does not exist
        if not self.avatarHash:
            self.avatarHash = get_gravatar_hash(self.emailAddress)
            db.session.commit()

        # Retrieve it for usage
        hash = self.avatarHash
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )
