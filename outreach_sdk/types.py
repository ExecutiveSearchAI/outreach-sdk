from typing import Any, Dict, List, TypedDict, Union

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
