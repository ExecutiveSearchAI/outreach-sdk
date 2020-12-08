__version__ = "0.1.0"

from .auth import Credentials
from .resources import ApiResource
from .session import Session


def resource(name: str, credentials: Credentials) -> ApiResource:
    """
    Initialize an :py:class`~outreach_sdk.session.Session` and return the specified
    :py:class`~outreach_sdk.resources.ApiResource`.

    Args:
      name: the name of the API resource to create.
      credentials: the OAuth2 credentials to authorize the session.

    Returns:
      An ApiResource instance.

    Raises:
      :py:class:`.exceptions.ResourceNotSupportedException`: If the resource isn't supported.
    """
    return Session(credentials).resource(name)
