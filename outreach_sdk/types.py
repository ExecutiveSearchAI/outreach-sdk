from typing import Any, Dict, List, Union

try:  # pragma: no cover
    from typing import TypedDict  # type: ignore
except ImportError:  # pragma: no cover
    from typing_extensions import TypedDict

JSONDict = Dict[str, Any]
JSONList = List[JSONDict]


class ApiErrorDict(TypedDict):
    id: str
    title: str
    detail: str


class ApiErrorResponse(TypedDict):
    errors: List[ApiErrorDict]


class ApiSuccessResponse(TypedDict):
    data: Union[JSONDict, JSONList]


ApiResponse = Union[ApiErrorResponse, ApiSuccessResponse]
