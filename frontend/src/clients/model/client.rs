use crate::clients::{BaseRestClient, ClientResult};
use super::models::*;

#[derive(Clone)]
pub struct ModelClient {
    base: BaseRestClient,
}

impl ModelClient {
    pub fn new(base: BaseRestClient) -> Self {
        Self { base }
    }

    pub async fn list_models(&self) -> ClientResult<Vec<MlModel>> {
        self.base.rest_get("/models", None).await
    }

    pub async fn list_tasks(&self) -> ClientResult<Vec<Task>> {
        self.base.rest_get("/tasks", None).await
    }

    pub async fn submit_task(&self, req: PredictRequest) -> ClientResult<Task> {
        self.base.rest_post("/tasks", req).await
    }

    pub async fn get_task(&self, task_id: i64) -> ClientResult<Task> {
        self.base.rest_get(&format!("/tasks/{}", task_id), None).await
    }
}
