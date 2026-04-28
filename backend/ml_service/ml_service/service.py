import facet

import ml_service_model
import ml_service_users
import ml_service_wallet

from .settings import Settings


class Service(facet.AsyncioServiceMixin):
    def __init__(
            self,
            users: ml_service_users.Service | None,
            wallet: ml_service_wallet.Service | None,
            model: ml_service_model.Service | None,
    ) -> None:
        self._users = users
        self._wallet = wallet
        self._model = model

    @property
    def dependencies(self) -> list[facet.AsyncioServiceMixin]:
        optional = [
            self._users,
            self._wallet,
            self._model,
        ]
        return [*super().dependencies, *filter(None, optional)]

    @property
    def users(self) -> ml_service_users.Service | None:
        return self._users

    @property
    def wallet(self) -> ml_service_wallet.Service | None:
        return self._wallet

    @property
    def model(self) -> ml_service_model.Service | None:
        return self._model


def get_service(
    settings: Settings
) -> Service:
    users_service = ml_service_users.get_service(settings=settings.ml_service_users)
    wallet_service = ml_service_wallet.get_service(settings=settings.ml_service_wallet)
    model_service = ml_service_model.get_service(settings=settings.ml_service_model)
    return Service(users=users_service, wallet=wallet_service, model=model_service)
