class ResourceNotSupportedException(Exception):
    """Raised when the API resource has not been defined."""

    def __init__(self, resource_name: str):
        """
        Args:
            resource_name: The name of the resource that was attempted to be created.
        """
        message = f"The resource '{resource_name}' is not currently supported or doesn't exist."
        super(ResourceNotSupportedException, self).__init__(message)


class NoRelatedResourceException(Exception):
    """Raised when the specified related resource is not a valid relationship to the primary resource."""

    def __init__(self, resource_name: str, relationship_name: str):
        """
        Args:
            resource_name: The name of the primary resource.
            relationship_name: The name of the relationship.
        """
        message = f"Resource '{resource_name}' does not have relationship '{relationship_name}'."
        super(NoRelatedResourceException, self).__init__(message)


class RelatedResourceNotIncludedException(Exception):
    """
    Raised when trying to return a related resources attribute in a sparse fieldset without including the resource.
    """

    pass


class InvalidQueryParameterError(ValueError):
    """Base exception class for use when checking request query parameters."""

    pass


class InvalidFilterParameterError(InvalidQueryParameterError):
    """Raised when a provided resource or related resource attribute is not filterable."""

    pass


class InvalidSortParameterError(InvalidQueryParameterError):
    """Raised when a provided resource or related resource attribute is not sortable."""

    pass


class ApiError(Exception):
    """Raised when the API responds with an error response."""

    def __init__(self, status_code: int, title: str, detail: str):
        """
        Args:
            status_code: The HTTP response code.
            title: The error title from the response json.
            detail: The error detail from the response json.
        """
        message = f"{status_code} {title}\ndetail: {detail}"
        super(ApiError, self).__init__(message)
