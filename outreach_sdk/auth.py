import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Union

import requests

from .exceptions import TokenRefreshError
from .urls import OUTREACH_TOKEN_URL

TOKEN_EXPIRY_GRACE_PERIOD = 5 * 60  # 5 minutes


class Credentials:
    """Credentials using OAuth2.0 access token and refresh token."""

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
          client_id (Optional(str)): The Outreach App client ID. Required for refresh. Defaults to OUTREACH_APP_ID
              environment variable if present.
          client_secret (Optional(str)): The Outreach App client secret. Required refresh. Defaults to
              OUTREACH_APP_SECRET environment variable if present.
          redirect_uri (Optional(str)): The redirect uri used for the initial authorization grant. Required and must
              be the same as the original authorization request value to enable refresh.
          access_token (Optional(str)): The OAuth2.0 access_token. Can be None if refresh information is provided.
          refresh_token (Optional(str)): The OAuth2.0 refresh token. Required for refresh.
          expires_at (Optional(int, float)): The expiry unix timestamp from the authorization request (float) or
              the sum of the created_at unix timestamp from the refresh request (int) and the expires_in (int) seconds
              value from the refresh request. If not provided, Credentials will be assumed to not be expired but still
              may be invalid.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False

        # remove five minutes from actual expiration to force refresh a bit early
        expiry = self.expires_at - TOKEN_EXPIRY_GRACE_PERIOD
        return datetime.fromtimestamp(expiry, timezone.utc) < datetime.now(timezone.utc)

    @property
    def valid(self) -> bool:
        return self.access_token is not None and not self.expired

    def apply(self, headers: dict) -> None:
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
            strip (Optional(List[str])): List of keys to exclude from the generated dictionary.

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
        Creates a JSON representation of this instance using Credentials.to_dict().
        Useful for storing/updating credentials in your preferred storage backend.
        """
        return json.dumps(self.to_dict(strip=strip))
