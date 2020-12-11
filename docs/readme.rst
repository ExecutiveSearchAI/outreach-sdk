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

Example Usage
=============

Load existing credentials
-------------------------

.. literalinclude:: ../examples/existing_credentials_example.py
    :linenos:
    :language: python
