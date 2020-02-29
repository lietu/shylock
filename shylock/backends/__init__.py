class ShylockBackend:
    @staticmethod
    def _check():
        raise NotImplementedError()

    async def acquire(self, name: str, block: bool = True):
        raise NotImplementedError()

    async def release(self, name: str):
        raise NotImplementedError()
