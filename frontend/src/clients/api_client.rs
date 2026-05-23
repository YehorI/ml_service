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
        let auth = creds.to_basic_header();
        let mut headers = HashMap::new();
        headers.insert("Authorization".to_string(), auth);

        Ok(Self {
            users: UsersClient::new(BaseRestClient::new(&config.users_base_url, Some(headers.clone()), config.timeout_seconds)?),
            wallet: WalletClient::new(BaseRestClient::new(&config.wallet_base_url, Some(headers.clone()), config.timeout_seconds)?),
            model: ModelClient::new(BaseRestClient::new(&config.model_base_url, Some(headers), config.timeout_seconds)?),
        })
    }

    pub fn users(&self) -> &UsersClient { &self.users }
    pub fn wallet(&self) -> &WalletClient { &self.wallet }
    pub fn model(&self) -> &ModelClient { &self.model }
}
