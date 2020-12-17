import datetime

import pytest

import outreach_sdk
from outreach_sdk.auth import Credentials

MOCK_NOW = datetime.datetime.fromisoformat("2020-07-01T12:00:00+00:00")


@pytest.fixture
def mock_now(monkeypatch):
    def patch(from_module):
        class patched(datetime.datetime):
            @classmethod
            def now(cls, tzinfo=None):
                return MOCK_NOW

        monkeypatch.setattr(f"{from_module}.datetime", patched)
        return patched

    return patch


@pytest.fixture
def creds():
    # setting a key to None in override will strip it from the creds dictionary
    def _creds(override={}):
        defaults = {
            "client_id": "client_id",
            "client_secret": "client_secret",
            "redirect_uri": "redirect_uri",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": 0,
        }
        if override:
            defaults.update(override)

        defaults = {k: v for k, v in defaults.items() if v is not None}

        return Credentials(**defaults)

    return _creds


@pytest.fixture
def prospects(creds):
    credentials = creds()
    return outreach_sdk.resource("prospects", credentials)
