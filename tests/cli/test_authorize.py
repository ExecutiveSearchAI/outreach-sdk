import io
import json
import sys
from contextlib import contextmanager

import _pytest

from outreach_sdk.cli import authorize


@contextmanager
def mock_input(value):
    orig = sys.stdin
    sys.stdin = value
    yield
    sys.stdin = orig


def test_run_local_flow(requests_mock):
    requests_mock.post(
        "https://api.outreach.io/oauth/token",
        json={"access_token": "ACCESS_TOKEN", "refresh_token": "REFRESH_TOKEN", "created_at": 1000, "expires_in": 234},
    )

    with mock_input(io.StringIO("https://www.example.com/oauth?code=oauthcode")):
        result = authorize.run_local_flow(
            "TEST_CLIENT_ID", "TEST_CLIENT_SECRET", "https://www.example.com/oauth", ["prospects.all"]
        )

        assert result.to_dict() == {
            "client_id": "TEST_CLIENT_ID",
            "client_secret": "TEST_CLIENT_SECRET",
            "redirect_uri": "https://www.example.com/oauth",
            "access_token": "ACCESS_TOKEN",
            "refresh_token": "REFRESH_TOKEN",
            "expires_at": 1234,
        }

    assert requests_mock.last_request.text == (
        "client_id=TEST_CLIENT_ID&client_secret=TEST_CLIENT_SECRET&redirect_uri=https%3A%2F%2Fwww.example.com%2Foauth"
        "&grant_type=authorization_code&code=oauthcode"
    )


def test_main(monkeypatch, capfd, creds):
    monkeypatch.setattr("outreach_sdk.cli.authorize.run_local_flow", lambda *_: creds())
    # hack to enable using the capture as a context manager
    setattr(_pytest.capture.EncodedFile, "__enter__", lambda self, *args: self)
    setattr(_pytest.capture.EncodedFile, "__exit__", lambda self, *args: self)
    authorize.main(
        [
            "--client_id",
            "client_id",
            "--client_secret",
            "client_secret",
            "--oauth_redirect_uri",
            "redirect_uri",
            "--scope",
            "prospects.all",
        ]
    )
    out, err = capfd.readouterr()

    assert json.loads(out) == {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "redirect_uri": "redirect_uri",
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "expires_at": 0,
    }


def test_main_with_env_defaults(monkeypatch, capfd, creds):
    monkeypatch.setenv("OUTREACH_APP_ID", "client_id")
    monkeypatch.setenv("OUTREACH_APP_SECRET", "client_secret")
    monkeypatch.setenv("OUTREACH_OAUTH_REDIRECT_URI", "redirect_uri")
    monkeypatch.setattr("outreach_sdk.cli.authorize.run_local_flow", lambda *_: creds())
    # hack to enable using the capture as a context manager
    setattr(_pytest.capture.EncodedFile, "__enter__", lambda self, *args: self)
    setattr(_pytest.capture.EncodedFile, "__exit__", lambda self, *args: self)
    authorize.main(["--scope", "prospects.all"])
    out, err = capfd.readouterr()

    assert json.loads(out) == {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "redirect_uri": "redirect_uri",
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "expires_at": 0,
    }
