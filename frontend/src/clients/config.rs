use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiConfig {
    pub users_base_url: String,
    pub wallet_base_url: String,
    pub model_base_url: String,
    pub timeout_seconds: Option<u32>,
}

impl ApiConfig {
    pub fn from_env() -> Result<Self, envy::Error> {
        dotenv::dotenv().ok();
        envy::from_env::<Self>()
    }
}

impl Default for ApiConfig {
    fn default() -> Self {
        Self {
            users_base_url: "http://localhost:8000".to_string(),
            wallet_base_url: "http://localhost:8001".to_string(),
            model_base_url: "http://localhost:8002".to_string(),
            timeout_seconds: Some(30),
        }
    }
}
