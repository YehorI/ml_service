use crate::clients::{BaseRestClient, ClientResult};
use super::models::*;

#[derive(Clone)]
pub struct WalletClient {
    base: BaseRestClient,
}

impl WalletClient {
    pub fn new(base: BaseRestClient) -> Self {
        Self { base }
    }

    pub async fn get_balance(&self) -> ClientResult<WalletBalance> {
        self.base.rest_get("/wallet/balance", None).await
    }

    pub async fn deposit(&self, amount: f64) -> ClientResult<WalletBalance> {
        self.base.rest_post("/wallet/deposit", DepositRequest { amount }).await
    }

    pub async fn list_transactions(&self) -> ClientResult<Vec<Transaction>> {
        self.base.rest_get("/wallet/transactions", None).await
    }
}
