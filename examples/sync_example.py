from time import time

from pymongo import MongoClient

from shylock import Lock, ShylockPymongoBackend, configure
from shylock.backends.pymongo import DOCUMENT_TTL

CONNECTION_STRING = "mongodb://localhost:27017"


def main():
    print("Start")

    c = MongoClient(CONNECTION_STRING)
    configure(ShylockPymongoBackend.create(c, "shylock_test", "shylock"))
    lock_name = "test-lock"

    test_lock = Lock(lock_name)
    try:
        with Lock(lock_name):
            print("Got lock")
            print("Testing re-lock")
            assert not test_lock.acquire(False)
            raise ValueError()
    except ValueError:
        print("Caught exception, lock should be released")

    assert test_lock.acquire(False)
    test_lock.release()

    print(
        f"Testing automatic release, this will take a while (~{DOCUMENT_TTL}-{DOCUMENT_TTL+60}s)."
    )

    # Test automatic release
    start = time()
    with test_lock:
        lock2 = Lock(lock_name)
        try:
            lock2.acquire()
            released = time() - start
        finally:
            lock2.release()
    print(f"Lock automatically released after {released:.3f}s")


if __name__ == "__main__":
    main()
