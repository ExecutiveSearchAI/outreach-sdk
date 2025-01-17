import pytest

from outreach_sdk.resources.exceptions import (
    ApiError,
    InvalidFilterParameterError,
    InvalidSortParameterError,
    NoRelatedResourceException,
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
            "?filter[firstName]=John&filter[emailAddresses][email]=email@example.com&sort=-account.name,firstName"
            "&page[size]=50&count=false",
        ),
        (
            {"firstName": "John", "emailAddresses__email": "email@example.com"},
            "https://api.outreach.io/api/v2/prospects"
            "?filter[firstName]=John&filter[emailAddresses][email]=email@example.com&page[size]=50&count=false",
        ),
        (
            {"sort": ["-account.name", "firstName"]},
            "https://api.outreach.io/api/v2/prospects?sort=-account.name,firstName&page[size]=50&count=false",
        ),
        (
            {"sort": "-account.name"},
            "https://api.outreach.io/api/v2/prospects?sort=-account.name&page[size]=50&count=false",
        ),
        (
            {"updatedAt": "2017-01-01..inf", "pagination": {"limit": 3}},
            "https://api.outreach.io/api/v2/prospects?filter[updatedAt]=2017-01-01..inf&page[limit]=3",
        ),
        (
            {"updatedAt": "2017-01-01..inf", "pagination": {"size": 200, "count": True}},
            "https://api.outreach.io/api/v2/prospects?filter[updatedAt]=2017-01-01..inf&page[size]=200&count=true",
        ),
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


def test_create_resource(requests_mock, prospects):
    requests_mock.post("https://api.outreach.io/api/v2/prospects", json={})
    prospects.create(attributes={"firstName": "James", "lastName": "Bond", "name": "James Bond"})

    assert requests_mock.last_request.json() == {
        "data": {"type": "prospect", "attributes": {"firstName": "James", "lastName": "Bond"}, "relationships": {}}
    }


def test_update_resource(requests_mock, prospects):
    requests_mock.patch("https://api.outreach.io/api/v2/prospects/1", json={})
    prospects.update(1, attributes={"tags": ["Tag 1", "Tag 2"]})

    assert requests_mock.last_request.json() == {
        "data": {"type": "prospect", "id": 1, "attributes": {"tags": ["Tag 1", "Tag 2"]}}
    }


def test_update_resource_readonly_field(requests_mock, prospects):
    requests_mock.patch("https://api.outreach.io/api/v2/prospects/1", json={})
    prospects.update(1, attributes={"lastName": "Bond", "name": "James Bond"})

    assert requests_mock.last_request.json() == {
        "data": {"type": "prospect", "id": 1, "attributes": {"lastName": "Bond"}}
    }


def test_delete_resource(requests_mock, prospects):
    requests_mock.delete("https://api.outreach.io/api/v2/prospects/1", text="", status_code=204)
    response = prospects.delete(1)
    assert response == {"data": {"message": "success", "detail": "prospect deleted"}}
