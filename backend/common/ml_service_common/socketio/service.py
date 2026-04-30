from typing import Iterable

import facet
import socketio
import uvicorn
from ml_service_common.interfaces.logger import LoggerInterface
from ml_service_common.uvicorn_server import UvicornServer

from .settings import SocketIOSettings


class SocketIOService(facet.AsyncioServiceMixin):
    def __init__(
            self,
            settings: SocketIOSettings,
            logger: LoggerInterface,
            namespaces: Iterable[socketio.AsyncNamespace] = (),
    ):
        self._settings = settings
        self._logger = logger

        self._server = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=settings.allowed_origins,
            client_manager=socketio.AsyncRedisManager(str(settings.redis_url)),
        )
        for namespace in namespaces:
            self._server.register_namespace(namespace)

    async def start(self):
        config = uvicorn.Config(app=self.get_app(), host="0.0.0.0", port=self._settings.port)
        server = UvicornServer(config)

        self.add_task(server.serve())

    def get_app(self) -> socketio.ASGIApp:
        app = socketio.ASGIApp(
            socketio_server=self._server,
            socketio_path=self._settings.root_path,
        )
        return app
