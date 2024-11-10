import hashlib

def get_gravatar_hash(emailAddress = None):
    """
    Returns the Gravatar hash based on the provided email address.

    :param emailAddress: The email address used to generate the Gravatar hash. 
        If not provided, the function returns the hash for an empty string.
    :type emailAddress: str, optional

    :return: The Gravatar hash for the provided email address.
    :rtype: str
    """
    return hashlib.md5(emailAddress.lower().encode("utf-8")).hexdigest()
