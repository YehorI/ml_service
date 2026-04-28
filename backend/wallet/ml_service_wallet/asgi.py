from ml_service_wallet.service import get_service

_service = get_service()
app = _service.api.get_app()
