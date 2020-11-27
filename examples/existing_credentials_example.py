import json
import os

from outreach_sdk.auth import Credentials

OUTREACH_APP_ID = os.environ.get("OUTREACH_APP_ID")
OUTREACH_APP_SECRET = os.environ.get("OUTREACH_APP_SECRET")
OUTREACH_OAUTH_REDIRECT_URI = os.environ.get("OUTREACH_OAUTH_REDIRECT_URI")


def read_credentials_from_file(filepath: str) -> Credentials:
    with open(filepath, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
        return Credentials(
            # NOTE: The Credentials class will automatically try to source client_id from $OUTREACH_APP_ID and
            # client_secret from $OUTREACH_APP_SECRET if they aren't provided explicitly at the time of initialization.
            # For the sake of example, we are explicitly accessing and providing those values here.
            client_id=OUTREACH_APP_ID,
            client_secret=OUTREACH_APP_SECRET,
            redirect_uri=OUTREACH_OAUTH_REDIRECT_URI,
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expires_at=data.get("expires_at"),
        )


def save_credentials_to_file(filepath: str, credentials: Credentials) -> None:
    # In this example, we are demonstrating the use of the strip argument to remove any values that we may not want to
    # store along with our credetials. In this case client id, client secret, and redirect uri are made available in
    # environment variables.
    with open(filepath, "w", encoding="utf-8") as json_file:
        json_file.write(credentials.to_json(strip=["client_id", "client_secret", "redirect_uri"]))


if __name__ == "__main__":
    credentials = read_credentials_from_file("./credentials.json")
    if not credentials.valid:
        credentials.refresh()
        save_credentials_to_file("./credentials.json", credentials)
