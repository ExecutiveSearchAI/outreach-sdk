from typing import Dict, List, Optional, Union, cast

import requests

from outreach_sdk.types import ApiErrorResponse, ApiResponse, ApiSuccessResponse, JSONDict, JSONList
from outreach_sdk.urls import OUTREACH_API_URL

from .exceptions import ApiError, InvalidFilterParameterError, InvalidSortParameterError
from .types import FilterParameterDict, FilterParameterValue, ResourceAttributes, ResourceRelationships, SortParam
from .util import load_resource_definition


class ApiResource:
    """
    Creates an ApiResource instance for working with the Outreach API.

    Attributes
    ----------
    api_endpoint: str
        The base url of the Outreach API.
    pagination: dict
        Dictionary containing default pagination settings.
    url: str
        The constructed resource endpoint.

    Methods
    -------
    list(**kwargs):
        Queries the API for a list of resources. Filter and sort parameters can be provided as kwargs according
        to the resource's filterable and sortable attributes and relationships. These differ depending on the resource,
        consult the `Outreach API Documentation <https://api.outreach.io/api/v2/docs#api-reference>`_ for details
        regarding specific resources. You can query against a related resource attribute by joining the resource name
        and attribute with double underscores, e.g., relatedResource__attribute and providing it as a keyword argument.
        Sorting can be done by providing the `sort` keyword argument with a value of :py:obj:`str` or :py:obj:`list` of
        :py:obj:`str` where the values are resource attributes. Sorting by related resources can be achieved by joining
        the related resouce name and attribute with a period, e.g., relatedResource.attribute. Descending sort order is
        also supported by prefixing the attribute with a dash ("-attribute").
    get(resource_id: int):
        Gets a single resource by ID.
    """

    api_endpoint: str = OUTREACH_API_URL
    pagination: dict = {"size": 50, "count": False, "limit": 0}
    _filter_fields: Optional[List[str]] = None
    _sort_fields: Optional[List[str]] = None

    def __init__(
        self,
        session: requests.Session,
        api_path: str,
        attributes: ResourceAttributes,
        relationships: ResourceRelationships,
    ):
        """
        Args:
            session: The authenticated session.
            api_path: The API path for the resource.
            attributes: Mapping of the available attributes of the resource and their properties.
            relationships: List of the resource's related resources.
        """
        self.session = session
        self.url = f"{self.api_endpoint}/{api_path}"
        self._attributes = attributes
        self._relationships = relationships

    @property
    def filter_fields(self) -> List[str]:
        """A list of filterable resource attributes"""
        if self._filter_fields is None:
            self._filter_fields = []
            for attr, options in self._attributes.items():
                if options.get("filterable"):
                    self._filter_fields.append(attr)

            for relation in self._relationships:
                rel_name = relation.get("rel_name", "")
                resource = relation.get("resource", "")
                rel_def = load_resource_definition(resource)
                for attr, options in rel_def.get("attributes", {}).items():
                    if options.get("filterable"):
                        self._filter_fields.append(f"{rel_name}.{attr}")

        return self._filter_fields

    @property
    def sort_fields(self) -> List[str]:
        """A list of sortable resource attributes"""
        if self._sort_fields is None:
            self._sort_fields = []
            for attr, options in self._attributes.items():
                if options.get("sortable"):
                    self._sort_fields.append(attr)

            for relation in self._relationships:
                rel_name = relation.get("rel_name", "")
                resource = relation.get("resource", "")
                rel_def = load_resource_definition(resource)
                for attr, options in rel_def.get("attributes", {}).items():
                    if options.get("sortable"):
                        self.sort_fields.append(f"{rel_name}.{attr}")

        return self._sort_fields

    def _build_filter_params(self, filter_dict: FilterParameterDict) -> FilterParameterDict:
        params: FilterParameterDict = {}
        for field, value in filter_dict.items():
            # kwarg can't have a '.' so we use '__' to represent relationship attribute
            field = field.replace("__", ".")
            if field not in self.filter_fields:
                raise InvalidFilterParameterError(f"'{field}' field is not filterable.")

            # split relationship name and attribute if applicable
            parts = field.split(".")
            # build filter querystring key
            qs_key = "filter"
            for part in parts:
                qs_key += f"[{part}]"

            params[qs_key] = value

        return params

    def _build_sort_params(self, sort: Union[List[str], str]) -> Dict[str, str]:
        if isinstance(sort, str):
            sort = [field for field in sort.split(",") if field]

        sort_params: List[SortParam] = []
        for field in sort:
            desc = field[0] == "-"
            sort_params.append(cast(SortParam, {"field": field[1:] if desc else field, "desc": desc}))

        for param in sort_params:
            field = param.get("field", "")
            if field not in self.sort_fields:
                raise InvalidSortParameterError(f"'{field}' field is not sortable.")

        return {
            "sort": ",".join(
                [f"-{param.get('field', '')}" if param.get("desc") else param.get("field", "") for param in sort_params]
            )
        }

    def _check_response(self, response: requests.Response) -> Union[JSONList, JSONDict]:
        """
        Determine if a response is successful or not and behave accordingly.

        Args:
            response: The response object from the API.

        Returns:
            A JSONList or JSONDict of response data for the request action.

        Raises:
            ApiError: If the response json contains an 'error' attribute.
        """
        response_json: ApiResponse = response.json()
        if "errors" in response_json:
            response_json = cast(ApiErrorResponse, response_json)
            error = response_json.get("errors", [])[0]
            raise ApiError(response.status_code, error.get("title", ""), error.get("detail", ""))
        else:
            response_json = cast(ApiSuccessResponse, response_json)

        return cast(Union[JSONList, JSONDict], response_json.get("data"))

    def list(self, **kwargs: FilterParameterValue) -> JSONList:
        """
        Returns a list of resources filtered and sorted according to the provided keyword arguments.

        Args:
            **kwargs: Key value pairings of filter and sort parameters.

        Returns:
             A list of resource attribute dictionaries.

        Raises:
            :py:class:`.exceptions.ApiError`: If the response json contains an 'error' attribute.
            :py:class:`.exceptions.InvalidFilterParameterError`: If the resource or related resource attribute
                is not filterable.
            :py:class:`.exceptions.InvalidSortParameterError`: If the resource or related resource attribute
                is not sortable.

        Examples:
            Create a prospects resource and filter by attribute

            >>> prospects = outreach_sdk.resource("prospects", credentials)
            >>> list_result = prospects.list(email="email@example.com")

            Sorting the results by attribute

            >>> sorted_list_result = prospects.list(sort=['firstName'])

            Sort by descending

            >>> sorted_list_result = prospects.list(sort=['-firstName'])

            Filtering against a related resource attribute

            >>> result = prospects.list(emailAddresses__email="email@example.com")

            Sort by related resource attribute

            >>> sorted_list_result = prospects.list(sort=['emailAddresses.email'])

        """
        sort: Union[List[str], str] = kwargs.pop("sort", [])  # type: ignore
        query_params = self._build_filter_params(kwargs)
        query_params.update(self._build_sort_params(sort))

        response = self.session.get(self.url, params=query_params)
        return cast(JSONList, self._check_response(response))

    def get(self, resource_id: int) -> JSONDict:
        """
        Gets a specific resource by id.

        Args:
            resource_id: The id of the resource to fetch.

        Returns:
            A dictionary of resource attributes.

        Raises:
            :py:class:`.exceptions.ApiError`: If the response json contains an 'error' attribute.

        Examples:
            >>> prospects = outreach_sdk.resource("prospects", credentials)
            >>> result = prospects.get(1)
        """
        response = self.session.get(f"{self.url}/{resource_id}")
        return cast(JSONDict, self._check_response(response))
