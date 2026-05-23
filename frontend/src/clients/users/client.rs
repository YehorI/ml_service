use crate::clients::{BaseRestClient, ClientResult};
use super::models::*;

#[derive(Clone)]
pub struct UsersClient {
    base: BaseRestClient,
}

impl UsersClient {
    pub fn new(base: BaseRestClient) -> Self {
        Self { base }
    }

    pub async fn register(&self, req: &RegisterRequest) -> ClientResult<User> {
        self.base.rest_post("/users/register", req).await
    }

    pub async fn login(&self, req: &LoginRequest) -> ClientResult<LoginResponse> {
        self.base.rest_post("/users/login", req).await
    }

    pub async fn get_user(&self, user_id: i64) -> ClientResult<User> {
        self.base.rest_get(&format!("/users/{}", user_id), None).await
    }
}
