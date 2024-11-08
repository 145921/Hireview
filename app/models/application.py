from app import db
from datetime import datetime


class Application(db.Model):
    """
    Model representing a Job Application.
    """

    __tablename__ = "Application"

    applicationId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jobListingId = db.Column(
        db.Integer,
        db.ForeignKey("JobListing.jobListingId", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    applicantId = db.Column(
        db.Integer,
        db.ForeignKey("Applicant.applicantId", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coverLetter = db.Column(db.Text)
    resumeUrl = db.Column(db.String(255))
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    status = db.Column(
        db.Enum(
            "Submitted",
            "Under Review",
            "Selected",
            "Rejected",
            name="application_status",
        ),
        default="Submitted",
        nullable=False,
        index=True,
    )

    # Relationships
    job_listing = db.relationship("JobListing", backref="applications")
    applicant = db.relationship("Applicant", backref="applications")

    def __repr__(self) -> str:
        return (
            f"Application(applicationId={self.applicationId}, status="
            + f"'{self.status}')"
        )

    @classmethod
    def create(cls, details: dict) -> "Application":
        """
        Create a new job application.

        :param details: dict - Details of the application to be created.
        :return: Application - The newly created application instance.
        """
        application = cls(**details)
        db.session.add(application)
        db.session.commit()
        return application

    def update(self, details: dict) -> "Application":
        """
        Update the application details.

        :param details: dict - Details of the application to update.
        :return: Application - The updated application instance.
        """
        for key, value in details.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self) -> None:
        """
        Delete the application.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()
