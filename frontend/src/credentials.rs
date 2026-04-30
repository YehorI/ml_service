use serde::{Deserialize, Serialize};

const CREDS_KEY: &str = "ml_credentials";

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Credentials {
    pub username: String,
    pub password: String,
}

impl Credentials {
    pub fn to_basic_header(&self) -> String {
        use base64::Engine;
        let raw = format!("{}:{}", self.username, self.password);
        format!("Basic {}", base64::engine::general_purpose::STANDARD.encode(raw))
    }
}

pub fn save_credentials(c: &Credentials) {
    let _ = c;
    #[cfg(target_arch = "wasm32")]
    if let Some(storage) = local_storage() {
        if let Ok(json) = serde_json::to_string(c) {
            let _ = storage.set_item(CREDS_KEY, &json);
        }
    }
}

pub fn load_credentials() -> Option<Credentials> {
    #[cfg(not(target_arch = "wasm32"))]
    return None;

    #[cfg(target_arch = "wasm32")]
    {
        let json = local_storage()?.get_item(CREDS_KEY).ok()??;
        serde_json::from_str(&json).ok()
    }
}

pub fn clear_credentials() {
    #[cfg(target_arch = "wasm32")]
    if let Some(storage) = local_storage() {
        let _ = storage.remove_item(CREDS_KEY);
    }
}

#[cfg(target_arch = "wasm32")]
fn local_storage() -> Option<web_sys::Storage> {
    web_sys::window()?.local_storage().ok()?
}
