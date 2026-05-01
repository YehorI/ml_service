use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct MlModel {
    pub id: i64,
    pub name: String,
    pub description: String,
    pub cost_per_request: f64,
    pub is_active: bool,
}

#[derive(Debug, Serialize)]
pub struct PredictRequest {
    pub model_id: i64,
    pub input_data: Value,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PredictionResult {
    pub output_data: Value,
    pub credits_charged: f64,
    pub created_at: String,
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum TaskStatus {
    Pending,
    Processing,
    Completed,
    Failed,
    #[serde(other)]
    Unknown,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Task {
    pub id: i64,
    pub model_id: i64,
    pub status: TaskStatus,
    pub input_data: Value,
    pub created_at: String,
    pub completed_at: Option<String>,
    pub result: Option<PredictionResult>,
}
