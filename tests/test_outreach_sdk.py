import pytest

import outreach_sdk
from outreach_sdk.resources.exceptions import ResourceNotSupportedException


def test_create_resource(creds):
    credentials = creds()
    resource = outreach_sdk.resource("prospects", credentials)
    assert resource.url == "https://api.outreach.io/api/v2/prospects"
    assert resource.resource_type == "prospect"
    assert resource.session.headers["User-Agent"] == "Outreach SDK Python/0.2.0"
    assert resource.session.headers["Content-Type"] == "application/vnd.api+json"
    assert resource.session.headers["Authorization"] == "Bearer access_token"
    assert resource.filter_fields == {
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
        "owner.createdAt",
        "owner.email",
        "owner.firstName",
        "owner.lastName",
        "owner.locked",
        "owner.updatedAt",
        "owner.username",
    }
    assert resource.readonly_fields == {
        "callOptedOut",
        "callsOptedAt",
        "clickCount",
        "contactHistogram",
        "createdAt",
        "emailOptedOut",
        "emailsOptedAt",
        "engagedAt",
        "engagedScore",
        "externalSource",
        "linkedInSlug",
        "name",
        "openCount",
        "optedOutAt",
        "replyCount",
        "smsOptedAt",
        "smsOptedOut",
        "timeZoneIana",
        "timeZoneInferred",
        "touchedAt",
        "updatedAt",
        "account.contactHistogram",
        "account.createdAt",
        "account.externalSource",
        "account.touchedAt",
        "account.trashedAt",
        "account.updatedAt",
        "emailAddresses.bouncedAt",
        "emailAddresses.createdAt",
        "emailAddresses.statusChangedAt",
        "emailAddresses.unsubscribedAt",
        "emailAddresses.updatedAt",
        "owner.createdAt",
        "owner.currentSignInAt",
        "owner.lastSignInAt",
        "owner.name",
        "owner.passwordExpiresAt",
        "owner.updatedAt",
    }
    assert resource.sort_fields == {
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
        "owner.createdAt",
        "owner.email",
        "owner.firstName",
        "owner.lastName",
        "owner.updatedAt",
        "owner.username",
    }


def test_non_existing_resource(creds):
    credentials = creds()
    with pytest.raises(ResourceNotSupportedException):
        outreach_sdk.resource("nothing", credentials)
