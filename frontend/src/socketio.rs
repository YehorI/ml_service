#[cfg(target_arch = "wasm32")]
pub mod client {
    use wasm_bindgen::prelude::*;

    #[wasm_bindgen]
    extern "C" {
        pub type Socket;

        #[wasm_bindgen(js_namespace = window, js_name = io)]
        pub fn connect(url: &str) -> Socket;

        #[wasm_bindgen(method)]
        pub fn on(this: &Socket, event: &str, callback: &Closure<dyn Fn(JsValue)>);

        #[wasm_bindgen(method)]
        pub fn emit(this: &Socket, event: &str, data: &JsValue);

        #[wasm_bindgen(method)]
        pub fn disconnect(this: &Socket);
    }
}
