import asyncio
from time import time

from aioarangodb import ArangoClient

from shylock import AsyncLock as Lock
from shylock import ShylockAioArangoDBBackend, configure

HOSTS = "http://localhost:8529"
USERNAME = "root"
PASSWORD = ""


async def main():
    print("Start")

    client = ArangoClient(hosts=HOSTS)
    db = await client.db("shylock_test", username=USERNAME, password=PASSWORD)
    configure(await ShylockAioArangoDBBackend.create(db, "shylock"))
    lock_name = "test-lock"

    test_lock = Lock(lock_name)
    try:
        async with Lock(lock_name):
            print("Got lock")
            print("Testing re-lock")
            assert not await test_lock.acquire(False)
            raise ValueError()
    except ValueError:
        print("Caught exception, lock should be released")

    assert await test_lock.acquire(False)
    await test_lock.release()

    locks = [f"test-lock-a{i}" for i in range(3)]

    async def _wait(lock_name: str):
        start = time()
        print(f"Waiting for release of {lock_name}, this might take a while.")
        async with Lock(lock_name):
            elapsed = time() - start
            print(f"Release of {lock_name} took {elapsed:.3f}s")

    waits = []
    for lock_name in locks:
        l = Lock(lock_name)
        await l.acquire()
        waits.append(_wait(lock_name))

    await asyncio.gather(*waits)

    await client.close()


if __name__ == "__main__":
    # Only in Python 3.7 ->
    # asyncio.run(main())

    # Compatible with Python 3.6 ->
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
