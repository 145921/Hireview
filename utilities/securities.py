import hashlib
from datetime import datetime



def get_gravatar_hash(emailAddress=None):
    """
    Returns the Gravatar hash based on the provided email address.

    :param emailAddress: The email address used to generate the Gravatar hash.
        If not provided, the function returns the hash for an empty string.
    :type emailAddress: str, optional

    :return: The Gravatar hash for the provided email address.
    :rtype: str
    """
    return hashlib.md5(emailAddress.lower().encode("utf-8")).hexdigest()


def get_eligible_applicants_for_job(job_listing):
    """
    Returns a list of applicants eligible for a specific job listing.

    Eligibility is based on:
    - Working method match (onsite, offsite, hybrid)
    - Location match (based on applicant's preferred location)
    - Industry match (based on applicant's job preferences and listing's
        category)
    - Applicant's active and verified status
    - Job listing deadline (only consider if deadline is in the future)
    """
    from app.models import Applicant
    eligible_applicants = []

    # NOTE: This commented code section if irrelevant in this scenario
    # Only consider the job listing if it is not expired
    # if job_listing.deadline and job_listing.deadline < datetime.utcnow():
    #    return eligible_applicants  # No eligible applicants if job listing
    # # is expired

    # Fetch all applicants
    all_applicants = Applicant.query.filter_by(
        isActive=True, isVerified=True
    ).all()

    for applicant in all_applicants:
        # Check matching criteria for eligibility
        if (
            job_listing.workingMethod in (applicant.jobPreferences or "")
            and job_listing.location in (applicant.preferredLocation or "")
            and job_listing.category in (applicant.industries or "")
        ):
            eligible_applicants.append(applicant)

    return eligible_applicants


def get_eligible_job_listings_for_applicant(applicant):
    """
    Returns a list of job listings eligible for a specific applicant.

    Eligibility is based on:
    - Applicant's job preferences (working method and job category)
    - Preferred location match
    - Job listing deadline (only consider if deadline is in the future)
    """
    from app.models import JobListing

    eligible_job_listings = []

    # Fetch all job listings with valid deadlines
    all_job_listings = JobListing.query.filter(
        (JobListing.deadline.is_(None))
        | (JobListing.deadline > datetime.utcnow())
    ).all()

    for job_listing in all_job_listings:
        # Check if job listing matches applicant's criteria
        if (
            job_listing.workingMethod in (applicant.jobPreferences or "")
            and job_listing.location in (applicant.preferredLocation or "")
            and job_listing.category in (applicant.industries or "")
        ):
            eligible_job_listings.append(job_listing)

    return eligible_job_listings
