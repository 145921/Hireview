from app import db


class User(db.Model):
    """
    Model representing a User in the system.
    """

    __tablename__ = "user"

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

    def __repr__(self) -> str:
        return f"User(userId={self.userId}, emailAddress={self.emailAddress})"

    @classmethod
    def create(cls, details: dict) -> "User":
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
