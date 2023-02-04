from asyncio import sleep
from datetime import datetime
from typing import Optional

try:
    from motor.motor_asyncio import (
        AsyncIOMotorClient,
        AsyncIOMotorCollection,
        AsyncIOMotorDatabase,
    )
    from pymongo.errors import DuplicateKeyError, WriteError
except ImportError:
    AsyncIOMotorClient = None
    AsyncIOMotorCollection = None
    AsyncIOMotorDatabase = None
    DuplicateKeyError = None
    WriteError = None

from shylock.backends import ShylockAsyncBackend
from shylock.exceptions import ShylockException

DOCUMENT_TTL = 60 * 5  # 5min seems like a reasonable TTL
POLL_DELAY = 1 / 16  # Some balance between high polling and high delay


class ShylockMotorAsyncIOBackend(ShylockAsyncBackend):
    @staticmethod
    async def create(
        client: AsyncIOMotorClient, db: str, collection_name: str = "shylock"
    ) -> "ShylockMotorAsyncIOBackend":
        """
        Create and initialize the backend
        :param client: Connected Motor client instance
        :param db: The name of the DB to use for locks
        :param collection_name: The name of the collection reserved for shylock
        """
        inst = ShylockMotorAsyncIOBackend(client, db, collection_name)
        await inst._init_collection()
        return inst

    async def acquire(self, name: str, block: bool = True) -> bool:
        """
        Try to acquire a lock, potentially wait until it's available
        :param name: Name of the lock
        :param block: Wait for lock
        :return: If lock was successfully acquired - always True if block is True
        """
        doc = {"name": name, "createdAt": datetime.utcnow()}

        while True:
            try:
                await self._coll.insert_one(doc)
                return True
            except DuplicateKeyError:
                if not block:
                    return False
                await sleep(POLL_DELAY)
            except WriteError as e:
                # Maybe this should check for blocking? Kinda not related though.
                delay = self._check_retry_exception(e)
                if delay is not None:
                    await sleep(delay)
                    continue

                raise

    async def release(self, name: str):
        """
        Release a given lock
        :param name: Name of the lock
        """
        while True:
            try:
                await self._coll.delete_one({"name": name})
                return
            except WriteError as e:
                delay = self._check_retry_exception(e, 0.25)
                if delay is not None:
                    await sleep(delay)
                    continue

                raise

    @staticmethod
    def _check():
        if AsyncIOMotorClient is None:
            raise ShylockException(
                "No motor driver available. Cannot use Shylock with Motor backend without it."
            )

    def __init__(
        self, client: AsyncIOMotorClient, db: str, collection_name: str = "shylock"
    ):
        self._check()
        self._client: AsyncIOMotorClient = client
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._db_name: str = db
        self._coll: Optional[AsyncIOMotorCollection] = None
        self._collection_name: str = collection_name

    async def _init_collection(self):
        """
        Ensure the collection is ready for our use
        """
        self._db = self._client[self._db_name]
        self._coll = self._db[self._collection_name]

        await self._init_index("name", unique=True)
        await self._init_index("createdAt", expireAfterSeconds=DOCUMENT_TTL)

    async def _init_index(self, index_name: str, **params):
        """
        Set up the given index
        :param index_name:
        :param params: https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html#motor.motor_asyncio.AsyncIOMotorCollection.create_index
        :return:
        """
        idx_info = await self._coll.index_information()
        index_found = False
        for name in idx_info:
            keys = [i[0] for i in idx_info[name]["key"]]

            if index_name in keys:
                index_found = True

        if not index_found:
            await self._coll.create_index(index_name, **params)

    @staticmethod
    def _check_retry_exception(
        e: WriteError, default_retry_time=None
    ) -> Optional[float]:
        """
        Check if the given WriteError implies we should just retry a bit later
        :param e:
        :param default_retry_time:
        :return: Time to wait for, or None if shouldn't retry
        """
        delay = None
        if e.code == 16500:  # Azure CosmosDB rate limiting
            delay = default_retry_time  # Delete does not get a RetryAfterMs
            msg = e.details.get("errmsg", "")
            for part in msg.replace(",", "").split(" "):
                if part.startswith("RetryAfterMs="):
                    delay = float(part[len("RetryAfterMs=") :]) / 1000

        return delay
