from typing import Optional, Union

from shylock.backends import ShylockAsyncBackend, ShylockSyncBackend

BACKEND: Optional[Union[ShylockAsyncBackend, ShylockSyncBackend]] = None


def configure(backend: Union[ShylockAsyncBackend, ShylockSyncBackend]):
    """
    Configure default backend to use
    :param backend: The ready to use backend
    """
    global BACKEND
    BACKEND = backend
