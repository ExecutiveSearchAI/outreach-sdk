#!/usr/bin/env python3

import argparse
import os
import sys
from typing import Any, List, Optional
from urllib.parse import parse_qs, urlsplit

from requests import Request, Session

from outreach_sdk.auth import Credentials
from outreach_sdk.urls import OUTREACH_AUTHORIZATION_URL, OUTREACH_TOKEN_URL


class EnvVar(argparse.Action):
    def __init__(self, envvar: str, default: Optional[str] = None, required: bool = True, **kwargs: Any) -> None:
        default = os.environ.get(envvar, default)
        if required and default:
            required = False
        super(EnvVar, self).__init__(default=default, required=required, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: Optional[str] = None,
    ) -> None:
        setattr(namespace, self.dest, values)


def run_local_flow(client_id: str, client_secret: str, redirect_uri: str, scopes: List[str] = []) -> Credentials:
    # manually authorize and get auth code
    payload = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
    }
    auth_request = Request("GET", OUTREACH_AUTHORIZATION_URL, params=payload).prepare()
    try:
        # temporarily redirect stdout to stderr so prompt doesn't get written to credentials file if
        # we are writing the credentials by redirecting stdout to file
        stdout = sys.stdout
        sys.stdout = sys.stderr
        redirected = input(
            f"Go to {auth_request.url} and authorize access.\nEnter the full url to which you were redirected:\n>>"
        )
    finally:
        sys.stdout = stdout

    query = urlsplit(redirected).query
    code = parse_qs(query).get("code", [])[0]

    # exchange code from redirect for auth token
    session = Session()
    response = session.post(
        OUTREACH_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "code": code,
        },
    )

    response.raise_for_status()
    data = response.json()

    return Credentials(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        access_token=data.get("access_token"),
        refresh_token=data.get("refresh_token"),
        expires_at=data.get("created_at") + data.get("expires_in"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Issue new OAuth credentials for OutreachAPI access.", fromfile_prefix_chars="@"
    )
    parser.add_argument("--client_id", action=EnvVar, envvar="OUTREACH_APP_ID", help="The Outreach API client app ID.")
    parser.add_argument(
        "--client_secret", action=EnvVar, envvar="OUTREACH_APP_SECRET", help="The Outreach API client app secret."
    )
    parser.add_argument(
        "--oauth_redirect_uri",
        action=EnvVar,
        envvar="OUTREACH_OAUTH_REDIRECT_URI",
        help="The oauth redirect url for your app.",
    )
    parser.add_argument(
        "-s",
        "--scope",
        dest="scopes",
        action="append",
        metavar="<resource>.<access>",
        required=True,
        type=str,
        help=(
            "The scopes required for the access credentials; e.g., prospects.read, accounts.all. "
            "If you require many scopes you may pass them by file where each line is `-s <value>`. "
            "Ex: python3 %(prog)s @scopes.txt"
        ),
    )
    parser.add_argument(
        "-o",
        "--out",
        required=False,
        default=sys.stdout,
        type=argparse.FileType("w", encoding="utf-8"),
        help="The output file to which to write the credentials. If not provided default is stdout.",
    )
    args = parser.parse_args()

    credentials = run_local_flow(args.client_id, args.client_secret, args.oauth_redirect_uri, args.scopes)
    with args.out as credentials_file:
        credentials_file.write(credentials.to_json())


if __name__ == "__main__":
    main()
