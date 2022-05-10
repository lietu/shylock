from time import time

from shylock import configure, Lock
from shylock.backends.pymemcache import ShylockPymemcacheBackend

from pymemcache import Client


def main():
    print("Start")
    client = Client("localhost:11211")
    configure(ShylockPymemcacheBackend.create(client))

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

    print("Testing automatic release, this might take a while.")

    # Test automatic release
    start = time()
    with test_lock:
        lock2 = Lock(lock_name)
        lock2.acquire()
        released = time() - start
    print(f"Lock automatically released after {released:.3f}s")


if __name__ == "__main__":
    main()
