import fastapi
from ml_service_wallet.api.rest.wallet import handlers
from ml_service_wallet.api.rest.wallet.schemas import (TransactionResponse,
                                                       WalletBalanceResponse)

router = fastapi.APIRouter()
router.add_api_route("/balance", handlers.get_balance, methods=["GET"], response_model=WalletBalanceResponse)
router.add_api_route("/deposit", handlers.deposit, methods=["POST"], response_model=WalletBalanceResponse)
router.add_api_route("/transactions", handlers.list_transactions, methods=["GET"], response_model=list[TransactionResponse])
