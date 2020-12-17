from numbers import Number
from typing import Dict, List, Union

try:  # pragma: no cover
    from typing import TypedDict  # type: ignore
except ImportError:  # pragma: no cover
    from typing_extensions import TypedDict


FilterParameterValue = Union[str, Number, List[str], List[Number]]
FilterParameterDict = Dict[str, FilterParameterValue]


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
