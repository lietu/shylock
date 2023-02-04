from time import sleep
from typing import Optional

try:
    from arango.collection import StandardCollection
    from arango.database import StandardDatabase
    from arango.exceptions import ArangoServerError
except ImportError:
    StandardDatabase = None
    StandardCollection = None
    ArangoServerError = None

from shylock.backends import ShylockSyncBackend
from shylock.exceptions import ShylockException

DOCUMENT_TTL = 60 * 5  # 5min seems like a reasonable TTL
POLL_DELAY = 1 / 16  # Some balance between high polling and high delay

ERROR_ARANGO_CONFLICT = 1200
ERROR_ARANGO_UNIQUE_CONSTRAINT_VIOLATED = 1210


class ShylockPythonArangoBackend(ShylockSyncBackend):
    @staticmethod
    def create(
        db: StandardDatabase, collection_name: str = "shylock"
    ) -> "ShylockPythonArangoBackend":
        """
        Create and initialize the backend
        :param db: An instance of arango.database.StandardDatabase connected to the desired database
        :param collection_name: The name of the collection reserved for shylock
        """
        inst = ShylockPythonArangoBackend(db, collection_name)
        inst._init_collection()
        return inst

    def acquire(self, name: str, block: bool = True) -> bool:
        """
        Try to acquire a lock, potentially wait until it's available
        :param name: Name of the lock
        :param block: Wait for lock
        :return: If lock was successfully acquired - always True if block is True
        """
        while True:
            try:
                self._db.aql.execute(
                    """
                    INSERT {
                      "name": @name,
                      "expiresAt": DATE_NOW() / 1000 + @ttl
                    } IN @@collection
                    """,
                    bind_vars={
                        "name": name,
                        "ttl": DOCUMENT_TTL,
                        "@collection": self._collection_name,
                    },
                )
                return True
            except ArangoServerError as err:
                if err.error_code in {
                    ERROR_ARANGO_UNIQUE_CONSTRAINT_VIOLATED,
                    ERROR_ARANGO_CONFLICT,
                }:
                    if not block:
                        return False
                    sleep(POLL_DELAY)
                else:
                    raise

    def release(self, name: str):
        """
        Release a given lock
        :param name: Name of the lock
        """
        self._db.aql.execute(
            """
            FOR l IN @@collection
                FILTER l.name == @name
                REMOVE l IN @@collection
            """,
            bind_vars={"name": name, "@collection": self._collection_name},
        )

    @staticmethod
    def _check():
        if StandardDatabase is None:
            raise ShylockException(
                "No python-arango driver available. Cannot use Shylock with PythonArango backend without it."
            )

    def __init__(self, db: StandardDatabase, collection_name: str = "shylock"):
        self._check()
        self._db: StandardDatabase = db
        self._coll: Optional[StandardCollection] = None
        self._collection_name: str = collection_name

    def _init_collection(self):
        """
        Ensure the collection is ready for our use
        """
        if self._db.has_collection(self._collection_name):
            self._coll = self._db.collection(self._collection_name)
        else:
            self._coll = self._db.create_collection(self._collection_name)

        self._coll.add_persistent_index(fields=["name"], unique=True)
        self._coll.add_ttl_index(fields=["expiresAt"], expiry_time=0)
