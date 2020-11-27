import json
from datetime import datetime

import pytest
import requests

from outreach_sdk.exceptions import TokenRefreshError

__mock_target = "outreach_sdk.auth"


def _get_timestamp(iso_string):
    return datetime.fromisoformat(iso_string).timestamp()


def test_credentials(creds):
    credentials = creds()
    assert credentials.to_dict() == {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "redirect_uri": "redirect_uri",
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "expires_at": 0,
    }
    assert credentials.expired is True
    assert credentials.valid is False


@pytest.mark.parametrize(
    "override,expected",
    [
        ({"expires_at": None}, False),  # no expiry assumed to not be expired
        ({"expires_at": _get_timestamp("2020-07-01T13:00:00+00:00")}, False),  # expires in an hour
        ({"expires_at": _get_timestamp("2020-07-01T12:04:59+00:00")}, True),  # under 5 minutes gracetime
        ({"expires_at": _get_timestamp("2020-07-01T11:59:00+00:00")}, True),  # expired 1 minute ago
    ],
)
def test_credentials_expired(override, expected, mock_now, creds):
    mock_now(__mock_target)
    credentials = creds(override=override)
    assert credentials.expired is expected


@pytest.mark.parametrize(
    "override,expected",
    [
        ({"expires_at": None}, True),
        ({"expires_at": _get_timestamp("2020-07-01T13:00:00+00:00")}, True),  # expires in an hour
        ({"expires_at": _get_timestamp("2020-07-01T11:00:00+00:00")}, False),  # expired an hour ago
        ({"access_token": None, "expires_at": _get_timestamp("2020-07-01T13:00:00+00:00")}, False),  # no access_token
    ],
)
def test_credentials_valid(override, expected, mock_now, creds):
    mock_now(__mock_target)
    credentials = creds(override=override)
    assert credentials.valid is expected


def test_credentials_can_apply_headers(creds):
    credentials = creds()
    headers = {}
    credentials.apply(headers)
    assert headers == {"Authorization": "Bearer access_token"}


def test_credentials_can_refresh(requests_mock, creds):
    credentials = creds(override={"access_token": None})
    requests_mock.post(
        "https://api.outreach.io/oauth/token",
        json={
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "created_at": _get_timestamp("2020-07-01T12:00:00+00:00"),
            "expires_in": 7200,  # 2 hours
        },
        status_code=201,
    )
    credentials.refresh()
    assert credentials.to_dict() == {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "redirect_uri": "redirect_uri",
        # only these values should change
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_at": _get_timestamp("2020-07-01T14:00:00+00:00"),
    }


@pytest.mark.parametrize("required_key", ["client_id", "client_secret", "redirect_uri", "refresh_token"])
def test_credentials_refresh_raises_exception_if_missing_required_info(required_key, creds):
    credentials = creds(override={f"{required_key}": None})
    with pytest.raises(TokenRefreshError):
        credentials.refresh()


def test_credentials_refresh_raises_exception_if_request_fails(requests_mock, creds):
    credentials = creds(override={"access_token": None})
    requests_mock.post(
        "https://api.outreach.io/oauth/token",
        json={
            "error_description": "Bad Request",
        },
        status_code=401,
    )
    with pytest.raises(requests.exceptions.HTTPError):
        credentials.refresh()


def test_credentials_to_dict_strip(creds):
    credentials = creds().to_dict(strip=["client_id", "client_secret"])
    assert credentials == {
        "redirect_uri": "redirect_uri",
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "expires_at": 0,
    }


def test_credentials_to_json(creds):
    credentials = creds().to_json(strip=["client_id", "client_secret"])
    assert credentials == json.dumps(
        {
            "redirect_uri": "redirect_uri",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": 0,
        }
    )
