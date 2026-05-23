use std::collections::HashMap;
use reqwest::{Client, ClientBuilder, Method, Response, StatusCode};
use serde::de::DeserializeOwned;
use serde::Serialize;
use thiserror::Error;

#[derive(Debug, Error, Clone)]
pub enum RestClientError {
    #[error("HTTP request failed: {message}")]
    Reqwest { message: String },

    #[error("API returned error {status}: {body}")]
    ResponseError { status: StatusCode, body: String },

    #[error("Serialization error: {0}")]
    Serialization(String),

    #[error("Config error: {0}")]
    ConfigError(String),
}

impl From<reqwest::Error> for RestClientError {
    fn from(err: reqwest::Error) -> Self {
        RestClientError::Reqwest { message: err.to_string() }
    }
}

impl From<serde_json::Error> for RestClientError {
    fn from(err: serde_json::Error) -> Self {
        RestClientError::Serialization(err.to_string())
    }
}

pub type ClientResult<T> = Result<T, RestClientError>;

#[derive(Clone)]
pub struct BaseRestClient {
    client: Client,
    base_url: String,
    default_headers: HashMap<String, String>,
}

impl BaseRestClient {
    pub fn new(
        base_url: impl Into<String>,
        headers: Option<HashMap<String, String>>,
        timeout_seconds: Option<u32>,
    ) -> ClientResult<Self> {
        let mut builder = ClientBuilder::new();

        #[cfg(not(target_arch = "wasm32"))]
        if let Some(timeout) = timeout_seconds {
            builder = builder.timeout(std::time::Duration::from_secs(u64::from(timeout)));
        }

        let client = builder.build()?;

        Ok(Self {
            client,
            base_url: base_url.into(),
            default_headers: headers.unwrap_or_default(),
        })
    }

    fn build_url(&self, path: &str) -> String {
        if path.starts_with("http") {
            path.to_string()
        } else {
            format!("{}{}", self.base_url, path)
        }
    }

    async fn send(
        &self,
        method: Method,
        path: &str,
        body: Option<Vec<u8>>,
        params: Option<Vec<(String, String)>>,
        content_type: Option<&str>,
    ) -> ClientResult<Response> {
        let url = self.build_url(path);
        let mut builder = self.client.request(method, &url);

        for (k, v) in &self.default_headers {
            builder = builder.header(k, v);
        }
        if let Some(ct) = content_type {
            builder = builder.header("Content-Type", ct);
        }
        if let Some(params) = params {
            builder = builder.query(&params);
        }
        if let Some(body) = body {
            builder = builder.body(body);
        }

        let response = builder.send().await?;
        let status = response.status();
        if !status.is_success() {
            let body = response.text().await.unwrap_or_default();
            return Err(RestClientError::ResponseError { status, body });
        }
        Ok(response)
    }

    pub async fn rest_get<T: DeserializeOwned>(
        &self,
        path: &str,
        params: Option<Vec<(String, String)>>,
    ) -> ClientResult<T> {
        let resp = self.send(Method::GET, path, None, params, None).await?;
        let bytes = resp.bytes().await?;
        serde_json::from_slice(&bytes).map_err(|e| RestClientError::Serialization(e.to_string()))
    }

    pub async fn rest_post<T: DeserializeOwned, D: Serialize>(
        &self,
        path: &str,
        data: D,
    ) -> ClientResult<T> {
        let body = serde_json::to_vec(&data)?;
        let resp = self
            .send(Method::POST, path, Some(body), None, Some("application/json"))
            .await?;
        let bytes = resp.bytes().await?;
        serde_json::from_slice(&bytes).map_err(|e| RestClientError::Serialization(e.to_string()))
    }
}
