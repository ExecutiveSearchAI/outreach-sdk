import pytest

import outreach_sdk
from outreach_sdk.resources.exceptions import ApiError, InvalidFilterParameterError, InvalidSortParameterError


def test_api_error(requests_mock, creds):
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
    credentials = creds()
    prospects = outreach_sdk.resource("prospects", credentials)
    with pytest.raises(ApiError) as excinfo:
        prospects.get(1)

    assert str(excinfo.value) == "403 Unauthorized Request\ndetail: You are not authorized to perform that request."


def test_invalid_filter_params(requests_mock, creds):
    requests_mock.get("https://api.outreach.io/api/v2/prospects")
    credentials = creds()
    prospects = outreach_sdk.resource("prospects", credentials)
    # firstName is misspelled
    with pytest.raises(InvalidFilterParameterError):
        prospects.list(fiirstName="John", lastName="Doe")


def test_invalid_sort_params(requests_mock, creds):
    requests_mock.get("https://api.outreach.io/api/v2/prospects")
    credentials = creds()
    prospects = outreach_sdk.resource("prospects", credentials)
    # firstName is misspelled
    with pytest.raises(InvalidSortParameterError):
        prospects.list(sort=["-fiirstName"])


def test_list_resource(requests_mock, creds):
    requests_mock.get(
        "https://api.outreach.io/api/v2/prospects"
        "?filter[firstName]=John&filter[emailAddresses][email]=email@example.com&sort=-account.name,firstName",
        json={"data": [{"attributes": {"firstName": "John"}}]},  # partial response
    )
    credentials = creds()
    prospects = outreach_sdk.resource("prospects", credentials)
    response = prospects.list(
        firstName="John", emailAddresses__email="email@example.com", sort=["-account.name", "firstName"]
    )
    assert response == [{"attributes": {"firstName": "John"}}]


def test_sort_parameter_as_string(requests_mock, creds):
    requests_mock.get(
        "https://api.outreach.io/api/v2/prospects?sort=-account.name",
        json={"data": [{"attributes": {"firstName": "John"}}]},  # partial response
    )
    credentials = creds()
    prospects = outreach_sdk.resource("prospects", credentials)
    response = prospects.list(sort="-account.name")
    assert response == [{"attributes": {"firstName": "John"}}]
