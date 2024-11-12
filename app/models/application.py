from datetime import datetime

from app import db
from utilities.email_utils import send_email


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
            "Selected",
            "Rejected",
            name="application_status",
        ),
        default="Submitted",
        nullable=False,
        index=True,
    )

    # Relationships
    job_listing = db.relationship("JobListing", back_populates="applications")
    applicant = db.relationship("Applicant", back_populates="applications")

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
        # Save application details
        application = cls(**details)
        db.session.add(application)
        db.session.commit()

        # Send receipt confirmation message
        subject = f"Application Received for {application.job.title}"
        send_email(
            [application.applicant.emailAddress],
            subject,
            "email/application_received",
            applicant=application.applicant,
            job=application.job_listing,
        )

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

    def reject(self) -> None:
        """
        Marks the application as rejected and sends notification email to the
        applicant.

        :return: None
        """
        # Update status
        self.status = "Rejected"
        db.session.commit()

        # Send email to applicant
        subject = f"Job Application Update: {self.job_listing.title}"
        send_email(
            [self.applicant.emailAddress],
            subject,
            "email/rejected",
            applicant=self.applicant,
            job=self.job_listing,
        )

    def accept(self) -> None:
        """
        Marks the application as selected and sends notification email to the
        applicant.

        :return: None
        """
        # Update status
        self.status = "Selected"
        db.session.commit()

        # Send email to applicant
        subject = "Congratulations, You've Been Selected!"
        send_email(
            [self.applicant.emailAddress],
            subject,
            "email/selected",
            applicant=self.applicant,
            job=self.job_listing,
        )
