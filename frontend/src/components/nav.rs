use leptos::prelude::*;
use crate::credentials::{clear_credentials, load_credentials};

#[island]
pub fn NavAuthButtons() -> impl IntoView {
    let (logged_in, set_logged_in) = signal(false);

    Effect::new(move |_| {
        set_logged_in.set(load_credentials().is_some());
    });

    let sign_out = move |_| {
        clear_credentials();
        set_logged_in.set(false);
        #[cfg(target_arch = "wasm32")]
        {
            let _ = web_sys::window().and_then(|w| w.location().assign("/").ok());
        }
    };

    view! {
        {move || if logged_in.get() {
            view! {
                <div class="flex gap-3">
                    <a href="/dashboard" class="text-sm px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors">
                        "Profile"
                    </a>
                    <button
                        class="text-sm px-4 py-1.5 border border-gray-300 hover:border-red-400 hover:text-red-600 text-gray-700 rounded-lg font-semibold transition-colors"
                        on:click=sign_out
                    >
                        "Sign Out"
                    </button>
                </div>
            }.into_any()
        } else {
            view! {
                <div class="flex gap-3">
                    <a href="/login" class="text-sm px-4 py-1.5 border border-gray-300 hover:border-gray-400 text-gray-700 rounded-lg font-semibold transition-colors">
                        "Sign In"
                    </a>
                    <a href="/register" class="text-sm px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors">
                        "Register"
                    </a>
                </div>
            }.into_any()
        }}
    }
}
