from time import sleep, time
from typing import Optional

try:
    from pymemcache import Client, MemcacheError
except ImportError:
    Client = None
    MemcacheError = None

from shylock.backends import ShylockSyncBackend
from shylock.exceptions import ShylockException

DOCUMENT_TTL = 60 * 5  # 5min seems like a reasonable TTL
POLL_DELAY = 1 / 16  # Some balance between high polling and high delay
RETRY_COUNT = 3  # If a memcache error occurs, retry for this many times.


class ShylockPymemcacheBackend(ShylockSyncBackend):
    def __init__(
        self,
        client: Client,
        noreply: Optional[bool] = False,
        flags: Optional[int] = None,
    ):
        self._check()
        self._client = client
        self._noreply = noreply
        self._flags = flags
        self._owner = None

    @staticmethod
    def create(
        client: Client, noreply: Optional[bool] = False, flags: Optional[int] = None
    ) -> "ShylockPymemcacheBackend":
        """
        Create and initialize the backend
        :param client: An instance of pymemcache.Client connected to the desired server.
        :param noreply: If True, do not wait for a reply.
        :param flags: Arbitrary bit field used for server-specific flags
        """
        inst = ShylockPymemcacheBackend(client, noreply, flags)
        return inst

    def acquire(self, name: str, block: bool = True) -> bool:
        """
        Try to acquire a lock, potentially wait until it's available
        :param name: Name of the lock
        :param block: Wait for lock
        :return: If lock was successfully acquired - always True if block is True
        """
        retries = 0
        while True:
            try:
                result = self._client.add(
                    key=name,
                    value=name,
                    expire=int(time()) + DOCUMENT_TTL,
                    noreply=self._noreply,
                    flags=self._flags,
                )
                if result:
                    return True
                else:
                    if not block:
                        return False
                    sleep(POLL_DELAY)
            except MemcacheError:
                if retries >= RETRY_COUNT:
                    raise
                retries += 1
                sleep(POLL_DELAY)
            except Exception:
                raise

    def release(self, name: str):
        """
        Release a given lock
        :param name: Name of the lock
        """

        response = self._client.get(name)
        if response:
            self._client.delete(name, self._noreply)
        else:
            raise ShylockException(
                f"Lock '{name}' could not be released because it hasn't been acquired."
            )

    @staticmethod
    def _check():
        if Client is None:
            raise ShylockException(
                "No Pymemcache driver available. Cannot use Shylock with Pymemcache "
                "backend without it."
            )
