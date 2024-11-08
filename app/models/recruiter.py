from app import db


class Recruiter(db.Model):
    """
    Model representing a Recruiter who posts job listings.
    """

    __tablename__ = "recruiter"

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

    @classmethod
    def create(cls, details: dict) -> "Recruiter":
        """
        Create a new recruiter.

        :param details: dict - Details of the recruiter to be created.
        :return: Recruiter - The newly created recruiter instance.
        """
        recruiter = cls(
            name=details.get("name"),
            emailAddress=details.get("emailAddress"),
            phoneNumber=details.get("phoneNumber"),
            passwordHash=details.get("passwordHash"),
            avatarHash=details.get("avatarHash"),
            imageUrl=details.get("imageUrl"),
            nationality=details.get("nationality"),
            isVerified=details.get("isVerified", False),
            isApproved=details.get("isApproved", False),
        )
        db.session.add(recruiter)
        db.session.commit()
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
