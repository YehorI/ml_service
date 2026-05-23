pub mod app;
pub mod clients;
pub mod components;
pub mod credentials;
pub mod dashboard;
pub mod error;
pub mod socketio;

#[cfg(feature = "hydrate")]
#[wasm_bindgen::prelude::wasm_bindgen]
pub fn hydrate() {
    console_error_panic_hook::set_once();
    leptos::mount::hydrate_islands();
}
