import facet

import ml_service_model
import ml_service_users
import ml_service_wallet


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
        users_settings: ml_service_users.Settings | None = None,
        wallet_settings: ml_service_wallet.Settings | None = None,
        model_settings: ml_service_model.Settings | None = None,
) -> Service:
    users_service = ml_service_users.get_service(settings=users_settings)
    wallet_service = ml_service_wallet.get_service(settings=wallet_settings)
    model_service = ml_service_model.get_service(settings=model_settings)
    return Service(users=users_service, wallet=wallet_service, model=model_service)
