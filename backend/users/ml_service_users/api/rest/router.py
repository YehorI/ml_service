import fastapi

from ml_service_users.api.rest.users.router import router as users_router

router = fastapi.APIRouter()
router.include_router(users_router, prefix="/users", tags=["users"])
