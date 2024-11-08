from app import db


class Applicant(db.Model):
    """
    Model representing an Applicant who can apply for job listings.
    """

    __tablename__ = "applicant"

    applicantId = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    emailAddress = db.Column(db.String(100), nullable=False, unique=True)
    phoneNumber = db.Column(db.String(20), unique=True)
    passwordHash = db.Column(db.String(255), nullable=False)
    avatarHash = db.Column(db.String(255))
    gender = db.Column(db.String(20))
    imageUrl = db.Column(db.String(255))
    dateOfBirth = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    preferredLocation = db.Column(db.String(100))
    industries = db.Column(db.String(100))
    jobPreferences = db.Column(db.Text)
    isActive = db.Column(db.Boolean, default=True, nullable=False)
    isVerified = db.Column(db.Boolean, default=False, nullable=False)
    dateCreated = db.Column(db.DateTime, default=db.func.current_timestamp())
    lastUpdated = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Relationships
    educations = db.relationship(
        "Education", back_populates="applicant", cascade="all, delete"
    )
    experiences = db.relationship(
        "Experience", back_populates="applicant", cascade="all, delete"
    )
    applications = db.relationship(
        "Application", back_populates="applicant", cascade="all, delete"
    )

    def __repr__(self) -> str:
        return (
            f"Applicant(applicantId={self.applicantId}, "
            + f"emailAddress={self.emailAddress})"
        )

    @classmethod
    def create(cls, details: dict) -> "Applicant":
        """
        Create a new applicant.

        :param details: dict - Details of the applicant to be created.
        :return: Applicant - The newly created applicant instance.
        """
        applicant = cls(
            name=details.get("name"),
            emailAddress=details.get("emailAddress"),
            phoneNumber=details.get("phoneNumber"),
            passwordHash=details.get("passwordHash"),
            avatarHash=details.get("avatarHash"),
            gender=details.get("gender"),
            imageUrl=details.get("imageUrl"),
            dateOfBirth=details.get("dateOfBirth"),
            nationality=details.get("nationality"),
            preferredLocation=details.get("preferredLocation"),
            industries=details.get("industries"),
            jobPreferences=details.get("jobPreferences"),
            isActive=details.get("isActive", True),
            isVerified=details.get("isVerified", False),
        )
        db.session.add(applicant)
        db.session.commit()
        return applicant

    def update(self, details: dict) -> "Applicant":
        """
        Update applicant details.

        :param details: dict - A dictionary of details to update.
        :return: Applicant - The updated applicant instance.
        """
        self.name = details.get("name", self.name)
        self.emailAddress = details.get("emailAddress", self.emailAddress)
        self.phoneNumber = details.get("phoneNumber", self.phoneNumber)
        self.passwordHash = details.get("passwordHash", self.passwordHash)
        self.avatarHash = details.get("avatarHash", self.avatarHash)
        self.gender = details.get("gender", self.gender)
        self.imageUrl = details.get("imageUrl", self.imageUrl)
        self.dateOfBirth = details.get("dateOfBirth", self.dateOfBirth)
        self.nationality = details.get("nationality", self.nationality)
        self.preferredLocation = details.get(
            "preferredLocation", self.preferredLocation
        )
        self.industries = details.get("industries", self.industries)
        self.jobPreferences = details.get(
            "jobPreferences", self.jobPreferences
        )
        db.session.commit()
        return self

    def delete(self) -> None:
        """
        Delete the applicant.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()
