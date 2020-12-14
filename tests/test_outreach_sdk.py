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
    assert resource.filter_fields == [
        "createdAt",
        "emails",
        "engagedAt",
        "engagedScore",
        "externalSource",
        "firstName",
        "githubUsername",
        "lastName",
        "linkedInId",
        "linkedInSlug",
        "stackOverflowId",
        "title",
        "touchedAt",
        "twitterUsername",
        "updatedAt",
        "account.buyerIntentScore",
        "account.createdAt",
        "account.customId",
        "account.domain",
        "account.name",
        "account.named",
        "account.touchedAt",
        "account.updatedAt",
        "emailAddresses.bouncedAt",
        "emailAddresses.email",
        "emailAddresses.emailType",
        "emailAddresses.order",
        "emailAddresses.status",
        "emailAddresses.statusChangedAt",
        "emailAddresses.unsubscribedAt",
    ]
    assert resource.sort_fields == [
        "createdAt",
        "engagedAt",
        "engagedScore",
        "externalSource",
        "firstName",
        "githubUsername",
        "lastName",
        "linkedInId",
        "linkedInSlug",
        "stackOverflowId",
        "title",
        "touchedAt",
        "twitterUsername",
        "updatedAt",
        "account.buyerIntentScore",
        "account.createdAt",
        "account.customId",
        "account.domain",
        "account.name",
        "account.named",
        "account.touchedAt",
        "account.updatedAt",
        "emailAddresses.bouncedAt",
        "emailAddresses.email",
        "emailAddresses.emailType",
        "emailAddresses.order",
        "emailAddresses.status",
        "emailAddresses.statusChangedAt",
        "emailAddresses.unsubscribedAt",
    ]


def test_non_existing_resource(creds):
    credentials = creds()
    with pytest.raises(ResourceNotSupportedException):
        outreach_sdk.resource("nothing", credentials)
