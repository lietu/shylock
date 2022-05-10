from time import time

import shylock.backends.pymemcache
from shylock import configure, Lock
from shylock.backends.pymemcache import ShylockPymemcacheBackend

from pymemcache import Client

# You can run a local docker instance of memcached with this command:
# docker run --rm -p 11211:11211 -d --name memcached memcached


def test_pymemcache_lock():
    # Set the timeout to something short.
    shylock.backends.pymemcache.DOCUMENT_TTL = 3

    client = Client("localhost:11211")
    configure(ShylockPymemcacheBackend.create(client))

    lock_name = "test-lock"

    test_lock = Lock(lock_name)
    try:
        with Lock(lock_name):
            assert not test_lock.acquire(False)
            raise ValueError()
    except ValueError:
        pass

    assert test_lock.acquire(False)
    test_lock.release()

    start = time()
    with test_lock:
        lock2 = Lock(lock_name)
        lock2.acquire()
        released = time() - start
    assert released <= shylock.backends.pymemcache.DOCUMENT_TTL
