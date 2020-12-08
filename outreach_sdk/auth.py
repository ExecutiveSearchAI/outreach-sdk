import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Union

import requests

from .exceptions import TokenRefreshError
from .urls import OUTREACH_TOKEN_URL

TOKEN_EXPIRY_GRACE_PERIOD = 5 * 60  # 5 minutes


class Credentials:
    """
    Credentials using OAuth2.0 access token and refresh token.

    Attributes:
        token_uri: The Outreach API token URL.
        client_id: The Outreach App client ID.
        client_secret: The Outreach App client secret.
        redirect_uri: The redirect uri used for the initial authorization grant.
        access_token: The OAuth2.0 access_token.
        refresh_token: The OAuth2.0 refresh token.
        expires_at: Token expiration unix timestamp
    """

    token_uri = OUTREACH_TOKEN_URL

    def __init__(
        self,
        client_id: Optional[str] = os.environ.get("OUTREACH_APP_ID"),
        client_secret: Optional[str] = os.environ.get("OUTREACH_APP_SECRET"),
        redirect_uri: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expires_at: Optional[Union[int, float]] = None,
    ) -> None:
        """
        Args:
            client_id: The Outreach App client ID. Required for refresh. Defaults to OUTREACH_APP_ID environment
                variable if present.
            client_secret: The Outreach App client secret. Required refresh. Defaults to OUTREACH_APP_SECRET environment
                variable if present.
            redirect_uri: The redirect uri used for the initial authorization grant. Required and must be the same as
                the original authorization request value to enable refresh.
            access_token: The OAuth2.0 access_token. Can be None if refresh information is provided.
            refresh_token: The OAuth2.0 refresh token. Required for refresh.
            expires_at: The expiry unix timestamp from the authorization request (float) or the sum of the created_at
                unix timestamp from the refresh request (int) and the expires_in (int) seconds value from the refresh
                request. If not provided, Credentials will be assumed to not be expired but still may be invalid.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

    @property
    def expired(self) -> bool:
        """Returns whether or not the credentials have expired."""
        if self.expires_at is None:
            return False

        # remove five minutes from actual expiration to force refresh a bit early
        expiry = self.expires_at - TOKEN_EXPIRY_GRACE_PERIOD
        return datetime.fromtimestamp(expiry, timezone.utc) < datetime.now(timezone.utc)

    @property
    def valid(self) -> bool:
        """Returns whether or not the credentials are valid."""
        return self.access_token is not None and not self.expired

    def apply(self, headers: dict) -> None:
        """
        Updates the given headers dictionary with the access token.

        Args:
            headers: Dictionary of session header values.
        """
        headers.update({"Authorization": f"Bearer {self.access_token}"})

    def refresh(self) -> None:
        """
        Refreshes the access token.

        Raises:
            outreach_sdk.exceptions.RefreshError: If the credentials could not be refreshed due to lack of information.
            requests.exceptions.HTTPError: If the request failed for some reason.
        """
        if not all([self.client_id, self.client_secret, self.redirect_uri, self.refresh_token]):
            raise TokenRefreshError(
                "These credentials do not contain the necessary fields needed to refresh the access token. "
                "You must specify client_id, client_secret, redirect_uri, and refresh_token."
            )

        response = requests.post(
            self.token_uri,
            json={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            },
        )
        response.raise_for_status()

        data = response.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        self.expires_at = data.get("created_at") + data.get("expires_in")

    def to_dict(self, strip: List[str] = None) -> dict:
        """
        Creates a dictionary representation of a Credentials object.

        Args:
            strip: List of keys to exclude from the generated dictionary.

        Returns:
            dict: A dictionary representation of this instance.
        """
        prep = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
        }

        prep = {k: v for k, v in prep.items() if v is not None}

        if strip is not None:
            prep = {k: v for k, v in prep.items() if k not in strip}

        return prep

    def to_json(self, strip: List[str] = None) -> str:
        """
        Creates a JSON representation of this instance using :py:meth:`Credentials.to_dict`.
        Useful for storing/updating credentials in your preferred storage backend.

        Args:
            strip: List of keys to exclude from the generated dictionary.

        Returns:
            A JSON string representation of this instance.
        """
        return json.dumps(self.to_dict(strip=strip))
