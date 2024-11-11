from app import db
from datetime import datetime

from utilities.email_utils import send_email
from utilities.securities import get_eligible_applicants_for_job


class JobListing(db.Model):
    """
    Model representing a Job Listing.
    """

    __tablename__ = "JobListing"

    jobListingId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    workingMethod = db.Column(
        db.Enum("onsite", "offsite", "hybrid"), nullable=False
    )
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), index=True)
    location = db.Column(db.String(100), index=True)
    deadline = db.Column(db.DateTime)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
    lastUpdated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    organizationId = db.Column(
        db.Integer,
        db.ForeignKey("Organization.organizationId", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    # Relationships
    organization = db.relationship(
        "Organization", back_populates="job_listings"
    )
    applications = db.relationship("Application", back_populates="job_listing")

    def __repr__(self) -> str:
        return (
            f"JobListing(jobListingId={self.jobListingId}, title="
            + f"'{self.title}', position='{self.position}')"
        )

    @classmethod
    def create(cls, details: dict) -> "JobListing":
        """
        Create a new job listing.

        :param details: dict - Details of the job listing to be created.
        :return: JobListing - The newly created job listing instance.
        """
        job_listing = cls(**details)
        db.session.add(job_listing)
        db.session.commit()

        # Send email to all relevant applicants
        subject = f"New Job Available: {job_listing.title}"
        for applicant in get_eligible_applicants_for_job(job_listing):
            send_email(
                [applicant.emailAddress],
                subject,
                "email/new_job",
                job=job_listing,
            )

        return job_listing

    def update(self, details: dict) -> "JobListing":
        """
        Update the job listing details.

        :param details: dict - Details of the job listing to update.
        :return: JobListing - The updated job listing instance.
        """
        for key, value in details.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self) -> None:
        """
        Delete the job listing.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()
