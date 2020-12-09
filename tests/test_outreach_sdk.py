import pytest

import outreach_sdk
from outreach_sdk.resources.exceptions import ResourceNotSupportedException


def test_create_resource(creds):
    credentials = creds()
    resource = outreach_sdk.resource("prospects", credentials)
    assert resource.url == "https://api.outreach.io/api/v2/prospects"
    assert resource.session.headers["User-Agent"] == "Outreach SDK Python/0.1.0"
    assert resource.session.headers["Content-Type"] == "application/vnd.api+json"
    assert resource.session.headers["Authorization"] == "Bearer access_token"
    assert resource.filter_fields == ["firstName", "lastName", "account.name", "emailAddresses.email"]
    assert resource.sort_fields == ["firstName", "lastName", "account.name", "emailAddresses.email"]


def test_non_existing_resource(creds):
    credentials = creds()
    with pytest.raises(ResourceNotSupportedException):
        outreach_sdk.resource("nothing", credentials)
