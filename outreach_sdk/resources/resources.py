import json
from typing import Dict, List, MutableSet, Optional, Union, cast

import requests

from outreach_sdk.types import ApiErrorResponse, ApiResponse, ApiSuccessResponse, JSONDict
from outreach_sdk.urls import OUTREACH_API_URL

from .exceptions import (
    ApiError,
    InvalidFilterParameterError,
    InvalidSortParameterError,
    NoRelatedResourceException,
    RelatedResourceNotIncludedException,
)
from .types import (
    FilterParameterDict,
    FilterParameterValue,
    PaginationOptions,
    ResourceAttributes,
    ResourceDefinitionProps,
    ResourceRelationshipProps,
    ResourceRelationships,
    SortParam,
)
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
    resource_type: str
        The API resource type.

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
    get(resource_id: int, include: List[str], fields: List[str]):
        Gets a single resource by ID. Optionally, one may include related resources and sparse fieldsets to return by
        way of the include and `fields` arguments.
    """

    api_endpoint: str = OUTREACH_API_URL
    pagination: PaginationOptions = {"size": 50, "count": False, "limit": None}
    _filter_fields: Optional[MutableSet[str]] = None
    _readonly_fields: Optional[MutableSet[str]] = None
    _sort_fields: Optional[MutableSet[str]] = None

    def __init__(
        self,
        session: requests.Session,
        api_path: str,
        resource_type: str,
        attributes: ResourceAttributes,
        relationships: ResourceRelationships,
    ):
        """
        Args:
            session: The authenticated session.
            api_path: The API path for the resource.
            resource_type: The API resource type.
            attributes: Mapping of the available attributes of the resource and their properties.
            relationships: List of the resource's related resources.
        """
        self.session = session
        self.url = f"{self.api_endpoint}/{api_path}"
        self.resource_type = resource_type
        self._attributes = attributes
        self._relationships = relationships

    @property
    def filter_fields(self) -> MutableSet[str]:
        """A set of filterable resource attributes."""
        if self._filter_fields is None:
            self._filter_fields = set()
            for attr, options in self._attributes.items():
                if options.get("filterable"):
                    self._filter_fields.add(attr)

            for relation in self._relationships:
                rel_name = relation.get("rel_name", "")
                resource = relation.get("resource", "")
                rel_def = load_resource_definition(resource)
                for attr, options in rel_def.get("attributes", {}).items():
                    if options.get("filterable"):
                        self._filter_fields.add(f"{rel_name}.{attr}")

        return self._filter_fields

    @property
    def readonly_fields(self) -> MutableSet[str]:
        """A set of readonly fields for this resource."""
        if self._readonly_fields is None:
            self._readonly_fields = set()
            for attr, options in self._attributes.items():
                if options.get("readonly"):
                    self._readonly_fields.add(attr)

            for relation in self._relationships:
                rel_name = relation.get("rel_name", "")
                resource = relation.get("resource", "")
                rel_def = load_resource_definition(resource)
                for attr, options in rel_def.get("attributes", {}).items():
                    if options.get("readonly"):
                        self._readonly_fields.add(f"{rel_name}.{attr}")

        return self._readonly_fields

    @property
    def sort_fields(self) -> MutableSet[str]:
        """A set of sortable resource attributes."""
        if self._sort_fields is None:
            self._sort_fields = set()
            for attr, options in self._attributes.items():
                if options.get("sortable"):
                    self._sort_fields.add(attr)

            for relation in self._relationships:
                rel_name = relation.get("rel_name", "")
                resource = relation.get("resource", "")
                rel_def = load_resource_definition(resource)
                for attr, options in rel_def.get("attributes", {}).items():
                    if options.get("sortable"):
                        self._sort_fields.add(f"{rel_name}.{attr}")

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

    def _build_query_params(self, included: List[str], fields: List[str]) -> Dict[str, str]:
        for rel in included:
            # Test that the relationship exist. API seems to ignore nested relationships in included in spite of what
            # the docs say, so for now I'm ignoring them too.
            self._get_related_resource_props(rel.split(".")[0])

        params = {"include": ",".join(included)}

        for field in fields:
            parts = field.split(".")
            if len(parts) > 1:
                rel_name, attr = parts[:2]
                if rel_name not in included:
                    raise RelatedResourceNotIncludedException(
                        "To request fields for a related resource it must also be included."
                    )
                related_resource_type = self._get_related_resource_definition(rel_name).get("resource_type")
            else:
                related_resource_type, attr = self.resource_type, parts[0]

            qs_key = f"fields[{related_resource_type}]"
            if qs_key in params:
                params[qs_key] += f",{attr}"
            else:
                params[qs_key] = attr

        return params

    def _build_pagination_params(self, pagination_options: PaginationOptions) -> Dict[str, str]:
        if limit := pagination_options.get("limit", self.pagination["limit"]):
            return {"page[limit]": str(min(limit, 1000))}
        else:
            return {
                "page[size]": str(pagination_options.get("size", self.pagination["size"])),
                "count": json.dumps(pagination_options.get("count", self.pagination["count"]) is True),
            }

    def _check_response(self, response: requests.Response) -> ApiSuccessResponse:
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
            return cast(ApiSuccessResponse, response_json)

    def _get_related_resource_definition(self, relationship_name: str) -> ResourceDefinitionProps:
        props = self._get_related_resource_props(relationship_name)
        return load_resource_definition(cast(str, props.get("resource")))

    def _get_related_resource_props(self, relationship_name: str) -> ResourceRelationshipProps:
        try:
            props = next(relation for relation in self._relationships if relation.get("rel_name") == relationship_name)
        except StopIteration:
            raise NoRelatedResourceException(self.resource_type, relationship_name)
        else:
            return props

    def list(self, **kwargs: FilterParameterValue) -> ApiSuccessResponse:
        """
        Returns a list of resources filtered and sorted according to the provided keyword arguments.

        Args:
            **kwargs: Key value pairings of filter and sort parameters.

        Returns:
             A list of resource attribute dictionaries.

        Raises:
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
        pagination_options: PaginationOptions = kwargs.pop("pagination", {})  # type: ignore
        query_params = self._build_filter_params(kwargs)
        query_params.update(self._build_sort_params(sort))
        query_params.update(self._build_pagination_params(pagination_options))

        response = self.session.get(self.url, params=query_params)
        return self._check_response(response)

    def get(self, resource_id: int, include: List[str] = [], fields: List[str] = []) -> ApiSuccessResponse:
        """
        Gets a specific resource by id.

        Args:
            resource_id: The id of the resource to fetch.
            include: List of related resources to return with the resource.
            fields: List of specific field values to return for the resource and/or relationships.

        Returns:
            An API response containing a top-level data attribute with the resource data dictionary.

        Examples:
            >>> prospects = outreach_sdk.resource("prospects", credentials)
            >>> result = prospects.get(1, include=["owner"], fields=["firstName", "lastName", "owner.email"])
        """

        query_params = self._build_query_params(include, fields)
        response = self.session.get(f"{self.url}/{resource_id}", params=query_params)
        return self._check_response(response)

    def create(self, attributes: JSONDict = {}) -> ApiSuccessResponse:
        """
        Creates a new resource.

        Args:
            attributes: Dictionary of attribute keys for the resource to create.

        Returns:
            An API response including the data for the created resource.
        """
        attributes = {key: value for key, value in attributes.items() if key not in self.readonly_fields}
        data = {
            "type": self.resource_type,
            "attributes": attributes,
        }
        response = self.session.post(self.url, json={"data": data})
        return self._check_response(response)

    def update(self, resource_id: int, attributes: JSONDict = {}) -> ApiSuccessResponse:
        """
        Update the resource specified by resource_id.

        Args:
            resource_id: The id of the resource to fetch.
            attributes: Dictionary of attribute keys and values with which to update.

        Returns:
            An API response including the new values for the updated attributes and relationships.
        """
        # TODO: implement updates for related resource attributes
        attributes = {key: value for key, value in attributes.items() if key not in self.readonly_fields}
        data = {
            "type": f"{self.resource_type}",
            "id": resource_id,
            "attributes": attributes,
        }
        response = self.session.patch(f"{self.url}/{resource_id}", json={"data": data})
        return self._check_response(response)
