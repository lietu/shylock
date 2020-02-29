import asyncio
from time import time

from motor.motor_asyncio import AsyncIOMotorClient

from shylock import configure, Lock, ShylockMotorAsyncIOBackend

CONNECTION_STRING = "mongodb://your-connection-string"


async def main():
    print("Start")

    c = AsyncIOMotorClient(CONNECTION_STRING)
    configure(await ShylockMotorAsyncIOBackend.create(c, "shylock_test", "shylock"))
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

    locks = [f"test-lock-a{i}" for i in range(10)]

    async def _wait(lock_name: str):
        start = time()
        print(f"Waiting for release of {lock_name}")
        async with Lock(lock_name):
            elapsed = time() - start
            print(f"Release of {lock_name} took {elapsed:.3f}s")

    waits = []
    for lock_name in locks:
        l = Lock(lock_name)
        await l.acquire()
        waits.append(_wait(lock_name))

    await asyncio.gather(*waits)


if __name__ == "__main__":
    asyncio.run(main())
