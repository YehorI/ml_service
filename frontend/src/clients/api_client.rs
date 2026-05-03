use std::collections::HashMap;
use crate::clients::{BaseRestClient, ClientResult};
use crate::clients::config::ApiConfig;
use crate::clients::users::UsersClient;
use crate::clients::wallet::WalletClient;
use crate::clients::model::ModelClient;
use crate::credentials::Credentials;

#[derive(Clone)]
pub struct ApiClient {
    users: UsersClient,
    wallet: WalletClient,
    model: ModelClient,
}

impl ApiClient {
    pub fn new(config: &ApiConfig) -> ClientResult<Self> {
        Ok(Self {
            users: UsersClient::new(BaseRestClient::new(&config.users_base_url, None, config.timeout_seconds)?),
            wallet: WalletClient::new(BaseRestClient::new(&config.wallet_base_url, None, config.timeout_seconds)?),
            model: ModelClient::new(BaseRestClient::new(&config.model_base_url, None, config.timeout_seconds)?),
        })
    }

    pub fn with_credentials(config: &ApiConfig, creds: &Credentials) -> ClientResult<Self> {
        let auth_header = || {
            let mut h = HashMap::new();
            h.insert("Authorization".to_string(), creds.to_basic_header());
            h
        };
        Ok(Self {
            users: UsersClient::new(BaseRestClient::new(&config.users_base_url, Some(auth_header()), config.timeout_seconds)?),
            wallet: WalletClient::new(BaseRestClient::new(&config.wallet_base_url, Some(auth_header()), config.timeout_seconds)?),
            model: ModelClient::new(BaseRestClient::new(&config.model_base_url, Some(auth_header()), config.timeout_seconds)?),
        })
    }

    pub fn users(&self) -> &UsersClient { &self.users }
    pub fn wallet(&self) -> &WalletClient { &self.wallet }
    pub fn model(&self) -> &ModelClient { &self.model }
}
