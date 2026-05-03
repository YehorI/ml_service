use leptos::prelude::*;
use crate::credentials::load_credentials;

#[island]
pub fn HomeCta() -> impl IntoView {
    let (logged_in, set_logged_in) = signal(false);

    Effect::new(move |_| {
        set_logged_in.set(load_credentials().is_some());
    });

    view! {
        {move || if logged_in.get() {
            view! {
                <div class="flex justify-center gap-4 mb-16">
                    <a href="/predict" class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors text-sm">
                        "New Prediction"
                    </a>
                    <a href="/dashboard" class="px-8 py-3 border border-gray-300 hover:border-gray-400 text-gray-700 font-semibold rounded-xl transition-colors text-sm">
                        "Dashboard"
                    </a>
                </div>
            }.into_any()
        } else {
            view! {
                <div class="flex justify-center gap-4 mb-16">
                    <a href="/register" class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors text-sm">
                        "Get Started"
                    </a>
                    <a href="/login" class="px-8 py-3 border border-gray-300 hover:border-gray-400 text-gray-700 font-semibold rounded-xl transition-colors text-sm">
                        "Sign In"
                    </a>
                </div>
            }.into_any()
        }}
    }
}
