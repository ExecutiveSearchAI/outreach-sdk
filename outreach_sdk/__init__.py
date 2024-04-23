from importlib.metadata import PackageNotFoundError, version

__version__ = version(__name__)

from .auth import Credentials
from .resources import ApiResource


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
    from .session import Session

    return Session(credentials).resource(name)
