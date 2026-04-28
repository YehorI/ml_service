import facet
import fastapi
import uvicorn

from .settings import FastAPISettings


class FastAPIService(facet.AsyncioServiceMixin):
    def __init__(self, settings: FastAPISettings) -> None:
        self._settings = settings
        super().__init__()

    async def start(self) -> None:
        config = uvicorn.Config(
            app=self.get_app(),
            host=self._settings.host,
            port=self._settings.port,
        )
        server = uvicorn.Server(config)
        self.add_task(server.serve())

    def get_app(self) -> fastapi.FastAPI:
        app = fastapi.FastAPI(
            title=self._settings.title,
            version=self._settings.version,
        )
        app.service = self
        self.setup_app(app)
        return app

    def setup_app(self, app: fastapi.FastAPI) -> None:
        pass
