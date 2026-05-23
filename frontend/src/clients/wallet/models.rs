use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Deserialize)]
pub struct WalletBalance {
    pub user_id: i64,
    pub amount: f64,
}

#[derive(Debug, Serialize)]
pub struct DepositRequest {
    pub amount: f64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Transaction {
    pub id: i64,
    #[serde(rename = "type")]
    pub transaction_type: String,
    pub amount: f64,
    pub created_at: String,
    pub is_applied: bool,
    pub ml_task_id: Option<i64>,
}
