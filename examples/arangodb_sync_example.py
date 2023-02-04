from time import time

from arango import ArangoClient

from shylock import Lock, ShylockPythonArangoBackend, configure

HOSTS = "http://localhost:8529"
USERNAME = "root"
PASSWORD = ""


def main():
    print("Start")

    client = ArangoClient(hosts=HOSTS)
    db = client.db("shylock_test", username=USERNAME, password=PASSWORD)
    configure(ShylockPythonArangoBackend.create(db, "shylock"))
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
        try:
            lock2.acquire()
            released = time() - start
        finally:
            lock2.release()
    print(f"Lock automatically released after {released:.3f}s")


if __name__ == "__main__":
    main()
