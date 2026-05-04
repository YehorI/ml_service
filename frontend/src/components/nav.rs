use leptos::prelude::*;
use crate::credentials::{clear_credentials, load_credentials};

#[island]
pub fn AdminNavLink() -> impl IntoView {
    let (is_admin, set_is_admin) = signal(false);

    Effect::new(move |_| {
        let creds = load_credentials();
        set_is_admin.set(creds.as_ref().and_then(|c| c.role.as_deref()).map(|r| r == "admin").unwrap_or(false));
    });

    view! {
        {move || is_admin.get().then(|| view! {
            <a href="/admin" class="text-sm font-medium text-purple-600 hover:text-purple-800 transition-colors">
                "Admin"
            </a>
        })}
    }
}

#[island]
pub fn NavAuthButtons() -> impl IntoView {
    let (logged_in, set_logged_in) = signal(false);

    Effect::new(move |_| {
        let creds = load_credentials();
        set_logged_in.set(creds.is_some());
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
