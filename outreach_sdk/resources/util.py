import json
import os

from .exceptions import ResourceNotSupportedException
from .types import ResourceDefinition, ResourceDefinitionProps

# maybe create a Loader class to handle this so the file won't be read at import time
# and so it doesn't have to happen with every call of `load_resource_definition`
# TODO: Look into botocore Loader class
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
with open(f"{DATA_DIR}/resources.json", "r", encoding="utf-8") as resource_file:
    resources: ResourceDefinition = json.load(resource_file)


def load_resource_definition(name: str) -> ResourceDefinitionProps:
    """
    Loads an API resource definition.

    Args:
        name: The resource name, e.g., 'prospects'

    Returns:
        Dictionary of resource properties.

    Raises:
        ResourceNotSupportedException: If the provided resources has is not defined.
    """
    try:
        return resources[name]
    except KeyError as e:
        key = e.args[0]
        raise ResourceNotSupportedException(key)
