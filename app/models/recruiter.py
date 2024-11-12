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


class Recruiter(flask_login.UserMixin, db.Model):
    """
    Model representing a Recruiter who posts job listings.
    """

    __tablename__ = "Recruiter"

    recruiterId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    emailAddress = db.Column(db.String(100), nullable=False, unique=True)
    phoneNumber = db.Column(db.String(20), unique=True)
    passwordHash = db.Column(db.String(255), nullable=False)
    avatarHash = db.Column(db.String(255))
    imageUrl = db.Column(db.String(255))
    nationality = db.Column(db.String(50))
    isVerified = db.Column(db.Boolean, default=False, nullable=False)
    isApproved = db.Column(db.Boolean, default=False, nullable=False)
    dateCreated = db.Column(db.DateTime, default=db.func.current_timestamp())
    lastUpdated = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Relationships
    organizations = db.relationship(
        "Organization", back_populates="recruiter", cascade="all, delete"
    )

    def __repr__(self) -> str:
        return (
            f"Recruiter(recruiterId={self.recruiterId}, emailAddress="
            + f"{self.emailAddress})"
        )

    def __init__(self, **kwargs):
        super(Recruiter, self).__init__(**kwargs)

        # Generate the avatar hash
        if self.emailAddress is not None and self.avatarHash is None:
            self.avatarHash = get_gravatar_hash(self.emailAddress)

    @classmethod
    def registerAccount(cls, details: dict) -> "Recruiter":
        """
        Create a new recruiter.

        :param details: dict - Details of the recruiter to be created.
        :return: Recruiter - The newly created recruiter instance.
        """
        recruiter = cls(
            name=details.get("name"),
            emailAddress=details.get("emailAddress"),
            phoneNumber=details.get("phoneNumber"),
            password=details.get("password"),
            nationality=details.get("nationality"),
        )
        db.session.add(recruiter)
        db.session.commit()

        # Send confirmation email
        recruiter.sendConfirmationEmail()

        return recruiter

    def update(self, details: dict) -> "Recruiter":
        """
        Update recruiter details.

        :param details: dict - A dictionary of details to update.
        :return: Recruiter - The updated recruiter instance.
        """
        self.name = details.get("name", self.name)
        self.emailAddress = details.get("emailAddress", self.emailAddress)
        self.phoneNumber = details.get("phoneNumber", self.phoneNumber)
        self.passwordHash = details.get("passwordHash", self.passwordHash)
        self.avatarHash = details.get("avatarHash", self.avatarHash)
        self.imageUrl = details.get("imageUrl", self.imageUrl)
        self.nationality = details.get("nationality", self.nationality)
        self.isVerified = details.get("isVerified", self.isVerified)
        self.isApproved = details.get("isApproved", self.isApproved)
        db.session.commit()
        return self

    def delete(self) -> None:
        """
        Delete the recruiter.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()

    def get_id(self) -> int:
        """
        Inherited UserMixin class method used to retrieve user id for
        flask_login

        :return: int - Recruiter ID of the recruiter.
        """
        return self.recruiterId

    def login(self, details=dict()) -> tuple:
        """
        Logs in the user and marks them as online.

        :param details: dict - Contains password and rerecruiter_me boolean
        variable

        :return: tuple - Contains the return status and return message.
        """

        if self.verifyPassword(details.get("password", "")):
            flask_login.login_user(self, details.get("rerecruiter_me", False))

            # Set user type session variable
            flask.session.permanent = True
            flask.session["user_type"] = "recruiter"

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
        Hash the recruiter's password
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
            recruiter = Recruiter.query.filter_by(emailAddress=data).first()

            return recruiter

        except Exception:
            return None

    @staticmethod
    def resetPassword(token, new_password, expiration=3600):
        """
        Reset recruiter's password.

        :param token: str - the token for password reset.
        :param new_password: str - the new password.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token, expiration)

        except Exception:
            return False

        recruiter = Recruiter.query.filter_by(emailAddress=data).first()
        if recruiter is None:
            return False

        recruiter.password = new_password
        db.session.commit()

        return True

    def deleteProfileImage(self) -> None:
        """
        Deletes recruiter's profile image.
        """
        # Delete actual file from the file system
        file_path = os.path.join(
            flask.current_app.config["RECRUITERS_PROFILE_UPLOAD_PATH"],
            self.imageURL,
        )
        os.remove(file_path)

        # Update the same on the database
        self.imageURL = None
        db.session.commit()

    def updateProfileImage(self, image) -> "Recruiter":
        """
        Update recruiter's profile image.

        :param image: FileStorage - the image file to be uploaded.

        :return self: Recruiter - the updated Recruiter instance.
        """
        # Delete the old image if it exists
        if self.imageURL:
            delete_file(
                os.path.join(
                    flask.current_app.config["RECRUITERS_PROFILE_UPLOAD_PATH"],
                    self.imageURL,
                )
            )

        # Save image on file system
        saved_filename = save_image(
            image, flask.current_app.config["RECRUITERS_PROFILE_UPLOAD_PATH"]
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
        Updates recruiter's password.

        :param current_password: str - Recruiter's current password.
        :param new_password: str - Recruiter's new password.

        :return self: Recruiter - the updated Recruiter instance.
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

    def sendConfirmationEmail(self):
        """
        Send confirmation email to the recruiter.
        """
        token = self.generateConfirmationToken()
        confirmation_link = url_for(
            "authentication.recruiter_confirm",
            token=token,
            recruiter_id=self.recruiterId,
            _scheme="http",
            _external=True,
        )

        subject = "Confirm Your Email"
        send_email(
            [self.emailAddress],
            subject,
            "email/email_confirmation",
            user=self,
            confirmation_link=confirmation_link,
        )

    def confirm(self, token, expiration=3600):
        """
        Confirm user's email.

        This method uses a token to confirm the user's email address.

        :return: bool - True if confirmation is successful, False otherwise.
        """
        serializer = Serializer(flask.current_app.config["SECRET_KEY"])

        try:
            data = serializer.loads(token, max_age=expiration)

        except Exception:
            return False

        # Ensure that the link is not corrupted
        if data != self.emailAddress:
            return False

        # Update confirm status
        self.isVerified = True

        db.session.add(self)
        db.session.commit()

        return True

    def approve(self):
        """
        Allows recruiter to interact with the system.
        """
        self.isApproved = True
        db.session.commit()

    def reject(self):
        """
        Restricts recruiter from interacting with the system.
        """
        self.isApproved = False
        db.session.commit()
