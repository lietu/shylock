.. image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Flietu%2Fshylock.svg?type=shield
    :target: https://app.fossa.io/projects/git%2Bgithub.com%2Flietu%2Fshylock?ref=badge_shield

.. image:: https://img.shields.io/github/actions/workflow/status/lietu/shylock/publish.yaml
    :target: https://github.com/lietu/shylock/actions/workflows/publish.yaml

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://codecov.io/gh/lietu/shylock/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/lietu/shylock

.. image:: https://sonarcloud.io/api/project_badges/measure?project=lietu_shylock&metric=alert_status
    :target: https://sonarcloud.io/dashboard?id=lietu_shylock

.. image:: https://img.shields.io/github/issues/lietu/shylock
    :target: https://github.com/lietu/shylock/issues
    :alt: GitHub issues

.. image:: https://img.shields.io/pypi/dm/shylock
    :target: https://pypi.org/project/shylock/
    :alt: PyPI - Downloads

.. image:: https://img.shields.io/pypi/v/shylock
    :target: https://pypi.org/project/shylock/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/shylock
    :target: https://pypi.org/project/shylock/
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://opensource.org/licenses/BSD-3-Clause

Distributed locks on Python, with asyncio support


What is this?
=============

Locks are required when you have a distributed system (like any API) and you want to ensure consistency for your data and prevent race conditions. There are a lot of ways to implement them, and this library aims to provide easy access to some of the better ways.

The library is written primarily for use with asyncio code, but also supports normal synchronous usage.

Currently supported backends:

- MongoDB (using unique indexes + ttl indexes for consistency and safety)
- ArangoDB (using unique indexes + ttl indexes for consistency and safety)

Can be extended for other storage systems pretty easily.

License
-------

Licensing is important. This project itself uses BSD 3-clause license, but e.g. Mongodb Motor library and other such libraries used by it may have their own licenses.

For more information check the `LICENSE <https://github.com/lietu/shylock/blob/master/LICENSE>`_ -file.


Getting started
===============

Add ``shylock`` to your project via pip / pipenv / poetry

.. code-block:: bash

    # MongoDB asyncio
    pip install shylock[motor]
    # MongoDB
    pip install shylock[pymongo]
    # ArangoDB asyncio
    pip install shylock[aioarangodb]
    # ArangoDB
    pip install shylock[python-arango]

For most easy usage, you should in your application startup logic configure the default backend for Shylock to use, and then use the ``AsyncLock`` class to handle your locking needs.

.. code-block:: python

    from motor.motor_asyncio import AsyncIOMotorClient

    from shylock import configure, AsyncLock as Lock, ShylockMotorAsyncIOBackend

    CONNECTION_STRING = "mongodb://your-connection-string"

    client = AsyncIOMotorClient(CONNECTION_STRING)
    configure(await ShylockMotorAsyncIOBackend.create(client, "projectdb"))

    async def use_lock():
        async with Lock("my-lock"):
            # The lock is now acquired, and will be automatically released
            do_something()

    async def another_lock_use():
        lock = Lock("my-lock")
        try:
            await lock.acquire()
            do_something()
        finally:
             await lock.release()

    async def time_sensitive_code():
        lock = Lock("my-lock")
        try:
            locked = await lock.acquire(block=False)
            if locked:
                do_something()
        finally:
             if locked:
                 await lock.release()

Or the ``Lock`` class for code where ``asyncio`` support isn't required

.. code-block:: python

    from pymongo import MongoClient

    from shylock import configure, Lock, ShylockPymongoBackend

    CONNECTION_STRING = "mongodb://your-connection-string"

    client = MongoClient(CONNECTION_STRING)
    configure(ShylockPymongoBackend.create(client, "projectdb"))

    def use_lock():
        with Lock("my-lock"):
            # The lock is now acquired, and will be automatically released
            do_something()

    def another_lock_use():
        lock = Lock("my-lock")
        try:
            lock.acquire()
            do_something()
        finally:
             lock.release()

    def time_sensitive_code():
        lock = Lock("my-lock")
        try:
            locked = lock.acquire(block=False)
            if locked:
                do_something()
        finally:
             if locked:
                 lock.release()

You can also check out the `examples <https://github.com/lietu/shylock/tree/master/examples/>`_, which also show how to use Shylock with ArangoDB.


Contributing
============

This project is run on GitHub using the issue tracking and pull requests here. If you want to contribute, feel free to `submit issues <https://github.com/lietu/shylock/issues>`_ (incl. feature requests) or PRs here.

To test changes locally ``python setup.py develop`` is a good way to run this, and you can ``python setup.py develop --uninstall`` afterwards (you might want to also use the ``--user`` flag).

.. image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Flietu%2Fshylock.svg?type=large
    :target: https://app.fossa.io/projects/git%2Bgithub.com%2Flietu%2Fshylock?ref=badge_shield


Financial support
=================

This project has been made possible thanks to `Cocreators <https://cocreators.ee>`_ and `Lietu <https://lietu.net>`_. You can help us continue our open source work by supporting us on `Buy me a coffee <https://www.buymeacoffee.com/cocreators>`_.

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
   :target: https://www.buymeacoffee.com/cocreators
