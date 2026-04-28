import logging
from typing import Iterable

import facet
import fastapi
import uvicorn
from collabry_common.interfaces.logger.interfaces import LoggerInterface
from collabry_common.uvicorn_server import UvicornServer
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.sessions import SessionMiddleware

from .log_filters.endpoint import EndpointLogFilter
from .middlewares.session_id import SessionIDMiddleware
from .settings import FastAPISettings


class FastAPIService(facet.AsyncioServiceMixin):
    def __init__(self, settings: FastAPISettings, logger: LoggerInterface):
        self._settings = settings
        self._logger = logger

        super().__init__()

    async def start(self):
        config = uvicorn.Config(app=self.get_app(), host="0.0.0.0", port=self._settings.port)
        server = UvicornServer(config)

        logging.getLogger("uvicorn.access").addFilter(EndpointLogFilter(
            excluded_endpoints=self.get_logging_excluded_endpoints(),
        ))

        self.add_task(server.serve())

    def get_logging_excluded_endpoints(self) -> Iterable[str]:
        return ("/health", "/metrics")

    def get_app(self) -> fastapi.FastAPI:
        app = fastapi.FastAPI(
            root_url=self._settings.root_url,
            root_path=self._settings.root_path,
        )
        app.service = self

        self.setup_middlewares(app=app)
        self.setup_prometheus_instrumentator(app=app)
        self.setup_app(app=app)

        return app

    def setup_middlewares(self, app: fastapi.FastAPI):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(self._settings.allowed_origins),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_middleware(SessionIDMiddleware)
        app.add_middleware(SessionMiddleware, secret_key=self._settings.session_secret_key)

    def setup_prometheus_instrumentator(self, app: fastapi.FastAPI):
        instrumentator = Instrumentator()
        self.setup_metrics_exporter(instrumentator=instrumentator)
        instrumentator.instrument(app).expose(app, include_in_schema=False)

    def setup_app(self, app: fastapi.FastAPI):
        pass

    def setup_metrics_exporter(self, instrumentator: Instrumentator):
        pass
