import pytest

from outreach_sdk.resources.exceptions import (
    ApiError,
    InvalidFilterParameterError,
    InvalidSortParameterError,
    NoRelatedResourceException,
    ReadonlyAttributeUpdateException,
    RelatedResourceNotIncludedException,
)


def test_api_error(requests_mock, prospects):
    requests_mock.get(
        "https://api.outreach.io/api/v2/prospects/1",
        json={
            "errors": [
                {
                    "id": "unauthorizedRequest",
                    "title": "Unauthorized Request",
                    "detail": "You are not authorized to perform that request.",
                }
            ]
        },
        status_code=403,
    )
    with pytest.raises(ApiError) as excinfo:
        prospects.get(1)

    assert str(excinfo.value) == "403 Unauthorized Request\ndetail: You are not authorized to perform that request."


def test_invalid_filter_params(requests_mock, prospects):
    requests_mock.get("https://api.outreach.io/api/v2/prospects")
    # firstName is misspelled
    with pytest.raises(InvalidFilterParameterError):
        prospects.list(fiirstName="John", lastName="Doe")


def test_invalid_sort_params(requests_mock, prospects):
    requests_mock.get("https://api.outreach.io/api/v2/prospects")
    # firstName is misspelled
    with pytest.raises(InvalidSortParameterError):
        prospects.list(sort=["-fiirstName"])


@pytest.mark.parametrize(
    "kwargs,expected_url",
    [
        ({}, "https://api.outreach.io/api/v2/prospects"),
        (
            {"firstName": "John", "emailAddresses__email": "email@example.com", "sort": ["-account.name", "firstName"]},
            "https://api.outreach.io/api/v2/prospects"
            "?filter[firstName]=John&filter[emailAddresses][email]=email@example.com&sort=-account.name,firstName",
        ),
        (
            {"firstName": "John", "emailAddresses__email": "email@example.com"},
            "https://api.outreach.io/api/v2/prospects"
            "?filter[firstName]=John&filter[emailAddresses][email]=email@example.com",
        ),
        (
            {"sort": ["-account.name", "firstName"]},
            "https://api.outreach.io/api/v2/prospects?sort=-account.name,firstName",
        ),
        ({"sort": "-account.name"}, "https://api.outreach.io/api/v2/prospects?sort=-account.name"),
    ],
)
def test_list_resources(kwargs, expected_url, requests_mock, prospects):
    requests_mock.get(
        expected_url,
        json={"data": [{"attributes": {"firstName": "John"}}]},  # partial response
    )
    prospects.list(**kwargs)


@pytest.mark.parametrize(
    "include,fields,expected_url",
    [
        ([], [], "https://api.outreach.io/api/v2/prospects/1"),
        (["owner"], [], "https://api.outreach.io/api/v2/prospects/1?include=owner"),
        (["owner", "account.owner"], [], "https://api.outreach.io/api/v2/prospects/1?include=owner,account.owner"),
        (
            ["owner"],
            ["firstName", "lastName", "owner.firstName", "owner.lastName"],
            "https://api.outreach.io/api/v2/prospects/1"
            "?include=owner&fields[prospect]=firstName,lastName&fields[user]=firstName,lastName",
        ),
    ],
)
def test_get_resource(include, fields, expected_url, requests_mock, prospects):
    requests_mock.get(
        expected_url,
        json={"data": [{"attributes": {"firstName": "John"}}]},  # partial response
    )
    prospects.get(1, include, fields)


def test_get_resource_including_non_existing_relationship(prospects):
    with pytest.raises(NoRelatedResourceException) as excinfo:
        prospects.get(1, ["email"], ["email.field"])

    assert str(excinfo.value) == "Resource 'prospect' does not have relationship 'email'."


def test_get_resource_with_sparce_fieldset_without_including_relationship(prospects):
    with pytest.raises(RelatedResourceNotIncludedException) as excinfo:
        prospects.get(1, [], ["owner.name"])

    assert str(excinfo.value) == "To request fields for a related resource it must also be included."


def test_update_resource(requests_mock, prospects):
    requests_mock.patch("https://api.outreach.io/api/v2/prospects/1", json={})
    prospects.update(1, attributes={"tags": ["Tag 1", "Tag 2"]})

    assert requests_mock.last_request.json() == {
        "data": {"type": "prospect", "id": 1, "attributes": {"tags": ["Tag 1", "Tag 2"]}}
    }


def test_update_resource_readonly_field(requests_mock, prospects):
    with pytest.raises(ReadonlyAttributeUpdateException):
        prospects.update(1, attributes={"lastName": "Bond", "name": "James Bond"})
