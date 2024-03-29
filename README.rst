############
Outreach SDK
############

|  |tests|  |codecov| |code style| |imports|

.. |tests| image:: https://github.com/ExecutiveSearchAI/outreach-sdk/workflows/Tests/badge.svg
    :target: https://github.com/ExecutiveSearchAI/outreach-sdk/actions?workflow=Tests

.. |codecov| image:: https://codecov.io/gh/ExecutiveSearchAI/outreach-sdk/branch/main/graph/badge.svg?token=GUEYWQVUJQ
    :target: https://codecov.io/gh/ExecutiveSearchAI/outreach-sdk

.. |code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |imports| image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/

Quick Links
===========

- `Home Page <https://github.com/ExecutiveSearchAI/outreach-sdk>`_
- `Outreach Platform <https://www.outreach.io/>`_
- `Outreach API Documentation <https://api.outreach.io/api/v2/docs>`_

Summary
=======

outreach-sdk is an API wrapper for the Outreach Customer Engagement Platform in Python.
It provides an easy interface for working with any API resource which can be useful
in automating and integrating your current  workflows and tools. outreach-sdk currently
supports Python 3.7+ and supports the following platforms:

- **Linux**
- **macOS**
- **Windows**

Getting Started
===============

Prerequisites
-------------
To begin working with the Outreach API, you will need to `request API access <https://www.outreach.io/product/platform/api>`_
from the Outreach Support Team. Once your project has been registered with them they will send your Client ID and Client
Secret by email.

Install
-------
Install the package using PyPI.

.. code-block:: shell

   $ pip install outreach-sdk

Get OAuth Credentials
---------------------
Currently the Outreach platform only supports OAuth Web App authorization flow so in order to use this SDK in a server side
application you'll need to get an access token and refresh token and store those in a safe place.

The access token is valid for 2 hours and the refresh token is valid for 14 days. If your access token expires you may use
the refesh token to issue new credentials. For more information see the `Authentication <https://api.outreach.io/api/v2/docs#authentication>`_
section of the Outreach API docs.

In order to create new access credentials, you may use the `authorize.py <https://github.com/ExecutiveSearchAI/outreach-sdk/tree/main/authorize.py>`_
helper script made available in this package.

.. code-block:: shell

    $ authorize \
    >   --client_id <CLIENT_ID> \
    >   --client_secret <CLIENT_SECRET> \
    >   --oauth_redirect_uri <OAUTH_REDIRECT_URI> \
    >   --scope prospects.read \
    >   --scope prospects.write > credentials.json

To reuse existing credentials, refer to the `sample script <https://github.com/ExecutiveSearchAI/outreach-sdk/tree/main/examples/existing_credentials_example.py>`_
in the examples directory. You may need to implement your own read and save logic
based on where and how your credentials are stored.

Example Usage
=============
Once you have your credentials you can begin using the SDK to work with the API.

List
----
List resources applying optional filter and sort options.

.. code-block:: python

    >>> import outreach_sdk
    >>> from outreach_sdk.auth import Credentials
    >>>
    >>> # Load existing credentials from your preferred storage backend, e.g., filesystem, database, etc.
    >>> credentials = Credentials(
    ...     client_id=<OUTREACH_CLIENT_ID>,
    ...     client_secret=<OUTREACH_CLIENT_SECRET>,
    ...     redirect_uri=<OUTREACH_OAUTH_REDIRECT_URL>,
    ...     access_token=<ACCESS_TOKEN>,
    ...     refresh_token=<REFRESH_TOKEN>,
    ...     expires_at=<EXPIRES_AT>
    ...)
    ...
    >>>
    >>> # If credentials have expired since last use, you can refresh them like below.
    >>> if not credentials.valid:
    ...     credentials.refresh()
    ...
    >>>
    >>> prospects = outreach_sdk.resource("prospects", credentials)
    >>> prospects.list(firstName="John", sort="-lastName")
    {
       "data": [
          {"type": "prospect", "id": 1, "attributes": {"firstName": "John", ...}, "relationships": {...}},
          {"type": "prospect", "id": 5, "attributes": {"firstName": "John", ...}, "relationships": {...}}
       ]
    }

Get
---
Get a specific resource by ID.

.. code-block:: python

    >>> prospects = outreach_sdk.resource("prospects", credentials)
    >>> prospects.get(1)
    {"data": {"type": "prospect", "id": 1, "attributes": {...}}}

You can also request related resources. This will return all data associated with the resources.

.. code-block:: python

    >>> prospects = outreach_sdk.resource("prospects", credentials)
    >>> prospects.get(1, include=["owner"])
    {
       "data": {"type": "prospect", "id": 1, "attributes": {...}},
       "included": [{"type": "user", "id": 1, "attributes": {...}}]
    }

When you only need specific data points, you can specify sparse fieldsets to be returned.

.. code-block:: python

    >>> prospects = outreach_sdk.resource("prospects", credentials)
    >>> prospects.get(1, include=["account"], fields=["firstName", "lastName", "account.name"])
    {
       "data": {"type": "prospect", "id": 1, "attributes": {"firstName": "John", "lastName": "Doe"}},
       "included": [{"type": "account", "id": 1, "attributes": {"name": "Acme"}}]
    }

You may also include a relationship's related resource as well.
NOTE: This doesn't seem to work in the API right now.

.. code-block:: python

    >>> prospects = outreach_sdk.resource("prospects", credentials)
    >>> prospects.get(1, include=["account.owner"])
    {
       "data": {"type": "prospect", "id": 1, "attributes": {...}},
       "included": [
          {"type": "account", "id": 1, "attributes": {...}},
          {"type": "user", "id": 1, "attributes": {...}}
       ]
    }

Create
------
Create a resource instance.

.. code-block:: python

    >>> prospects = outreach_sdk.resource("prospects", credentials)
    >>> prospects.create(attributes={"firstName": "Jane", "lastName": "Doe"})
    {
       "data": {"type": "prospect", "id": 1, "attributes": {...}}
    }

Update
------
Update a resources attributes.

.. code-block:: python

    >>> prospects = outreach_sdk.resource("prospects", credentials)
    >>> prospects.update(1, attributes={"tags": ["Tag 1", "Tag 2"]})
    {"data": {"type": "prospect", "id": 1, "attributes": {"tags": ["Tag 1", "Tag 2"]}}}

Delete
------
Delete a resource.

.. code-block:: python

    >>> prospects = outreach_sdk.resource("prospects", credentials)
    >>> prospects.delete(1)

Contributing
============
