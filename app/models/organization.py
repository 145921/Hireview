from app import db
from sqlalchemy.orm import relationship


class Organization(db.Model):
    """
    Model representing an Organization.
    """

    __tablename__ = "Organization"

    organizationId = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    employees = db.Column(db.String(20))
    recruiterId = db.Column(
        db.Integer,
        db.ForeignKey("Recruiter.recruiterId", ondelete="SET NULL"),
        index=True,
    )

    # Relationships
    recruiter = relationship("Recruiter", back_populates="organizations")
    job_listings = relationship(
        "JobListing",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"Organization(organizationId={self.organizationId}, "
            + f"description='{self.description}')"
        )

    @classmethod
    def create(cls, details: dict) -> "Organization":
        """
        Create a new organization.

        :param details: dict - Details of the organization to be created.
        :return: Organization - The newly created organization instance.
        """
        organization = cls(**details)
        db.session.add(organization)
        db.session.commit()
        return organization

    def update(self, details: dict) -> "Organization":
        """
        Update the organization details.

        :param details: dict - Details of the organization to update.
        :return: Organization - The updated organization instance.
        """
        for key, value in details.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self) -> None:
        """
        Delete the organization.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()
