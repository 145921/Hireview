from app import db


class Education(db.Model):
    """
    Model representing Education of an Applicant.
    """

    __tablename__ = "Education"

    educationId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicantId = db.Column(
        db.Integer,
        db.ForeignKey("Applicant.applicantId", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    degree = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100))
    startDate = db.Column(db.Date)
    endDate = db.Column(db.Date)
    issueDate = db.Column(db.Date)
    documentUrl = db.Column(db.String(255))

    # Relationships
    applicant = db.relationship("Applicant", back_populates="educations")

    def __repr__(self) -> str:
        return (
            f"Education(educationId={self.educationId}, degree="
            + f"'{self.degree}')"
        )

    @classmethod
    def create(cls, details: dict) -> "Education":
        """
        Create a new education entry.

        :param details: dict - Details of the education to be created.
        :return: Education - The newly created education instance.
        """
        education = cls(**details)
        db.session.add(education)
        db.session.commit()
        return education

    def update(self, details: dict) -> "Education":
        """
        Update the education details.

        :param details: dict - Details of the education to update.
        :return: Education - The updated education instance.
        """
        for key, value in details.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self) -> None:
        """
        Delete the education entry.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()
