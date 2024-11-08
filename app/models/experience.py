from app import db


class Experience(db.Model):
    """
    Model representing Work Experience of an Applicant.
    """

    __tablename__ = "Experience"

    experienceId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicantId = db.Column(
        db.Integer,
        db.ForeignKey("Applicant.applicantId", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100))
    description = db.Column(db.Text)
    startDate = db.Column(db.Date)
    endDate = db.Column(db.Date)
    reasonOfTermination = db.Column(db.String(255))

    # Relationships
    applicant = db.relationship("Applicant", back_populates="experiences")

    def __repr__(self) -> str:
        return (
            f"Experience(experienceId={self.experienceId}, position="
            + f"'{self.position}')"
        )

    @classmethod
    def create(cls, details: dict) -> "Experience":
        """
        Create a new experience entry.

        :param details: dict - Details of the experience to be created.
        :return: Experience - The newly created experience instance.
        """
        experience = cls(**details)
        db.session.add(experience)
        db.session.commit()
        return experience

    def update(self, details: dict) -> "Experience":
        """
        Update the experience details.

        :param details: dict - Details of the experience to update.
        :return: Experience - The updated experience instance.
        """
        for key, value in details.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self) -> None:
        """
        Delete the experience entry.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()
