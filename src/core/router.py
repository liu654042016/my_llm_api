from __future__ import annotations

class RouterError(Exception):
    pass


class Router:
    def __init__(self, config):
        self.config = config

    async def route(self, **kwargs):
        # Minimal stub: return a dummy response-like object
        class DummyResponse:
            def __init__(self):
                self.content = b"{}"
            async def aiter_bytes(self):
                yield self.content

        return DummyResponse()

    async def close(self):
        return None
