from numbers import Number
from typing import Dict, List, Optional, TypedDict, Union


class ResourceAttributeProps(TypedDict):
    filterable: bool
    readonly: bool
    sortable: bool


class ResourceRelationshipProps(TypedDict):
    rel_name: str
    resource: str


ResourceAttributes = Dict[str, ResourceAttributeProps]
ResourceRelationships = List[ResourceRelationshipProps]


class ResourceDefinitionProps(TypedDict):
    api_path: str
    attributes: ResourceAttributes
    relationships: ResourceRelationships
    resource_type: str


ResourceDefinition = Dict[str, ResourceDefinitionProps]


class SortParam(TypedDict):
    """
    Intermediate data structure for keeping track of whether the sort field provided was descending or ascending.
    """

    field: str
    desc: bool


class PaginationOptions(TypedDict):
    size: int
    count: bool
    limit: Optional[int]


FilterParameterValue = Union[int, str, Number, List[int], List[str], List[Number], PaginationOptions]
FilterParameterDict = Dict[str, FilterParameterValue]
