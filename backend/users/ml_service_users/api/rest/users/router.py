import fastapi
from ml_service_users.api.rest.users import handlers

router = fastapi.APIRouter()

router.add_api_route("/register", handlers.register, methods=["POST"], status_code=201)
router.add_api_route("/login", handlers.login, methods=["POST"])
router.add_api_route("/{user_id}", handlers.get_user, methods=["GET"])
router.add_api_route("/{user_id}", handlers.update_user, methods=["PATCH"])
