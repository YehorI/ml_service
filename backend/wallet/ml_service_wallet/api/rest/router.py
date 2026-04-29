import fastapi

from ml_service_wallet.api.rest.wallet.router import router as wallet_router

router = fastapi.APIRouter()
router.include_router(wallet_router, prefix="/wallet", tags=["wallet"])
