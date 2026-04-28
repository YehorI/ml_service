from ml_service_users.service import get_service

_service = get_service()
app = _service.api.get_app()
