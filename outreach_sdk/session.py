import requests

from . import __version__
from .auth import Credentials
from .resources import ApiResource
from .resources.util import load_resource_definition


class Session:
    """
    Creates a session with the provided authentication credentials to allow working with API resources.
    """

    def __init__(self, credentials: Credentials) -> None:
        """
        Args:
            credentials: The Outreach App oauth credentials for API access.
        """
        self._session = requests.Session()
        headers = {"User-Agent": f"Outreach SDK Python/{__version__}", "Content-Type": "application/vnd.api+json"}
        credentials.apply(headers)
        self._session.headers.update(headers)

    def resource(self, name: str) -> ApiResource:
        """
        Initializes and ApiResource instance with the authenticated session.
        Args:
            name: The name of the API resource, e.g., prospects.

        Returns:
          An ApiResource instance.

        Raises:
          :py:class:`.resources.exceptions.ResourceNotSupportedException`: If the resource isn't supported.
        """
        return ApiResource(self._session, **load_resource_definition(name))
