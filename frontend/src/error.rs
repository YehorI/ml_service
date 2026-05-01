use thiserror::Error;
use reqwest::StatusCode;

#[derive(Debug, Error, Clone)]
pub enum AppError {
    #[error("Not authenticated")]
    Unauthenticated,
    #[error("Invalid credentials")]
    Unauthorized,
    #[error("Insufficient balance")]
    InsufficientBalance,
    #[error("API error ({status}): {body}")]
    Api { status: u16, body: String },
    #[error("Network error: {0}")]
    Network(String),
    #[error("{0}")]
    Other(String),
}

impl From<crate::clients::RestClientError> for AppError {
    fn from(e: crate::clients::RestClientError) -> Self {
        match e {
            crate::clients::RestClientError::ResponseError { status, body } => {
                if status == StatusCode::UNAUTHORIZED {
                    AppError::Unauthorized
                } else {
                    AppError::Api { status: status.as_u16(), body }
                }
            }
            crate::clients::RestClientError::Reqwest { message } => AppError::Network(message),
            other => AppError::Other(other.to_string()),
        }
    }
}
