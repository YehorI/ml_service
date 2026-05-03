use leptos::prelude::*;
use crate::clients::api_client::ApiClient;
use crate::clients::RestClientError;
use crate::clients::config::ApiConfig;
use crate::clients::users::models::{LoginRequest, RegisterRequest};
use crate::credentials::{save_credentials, Credentials};

const INPUT_CLASS: &str = "w-full px-4 py-2.5 border border-gray-300 rounded-lg \
    text-gray-900 placeholder-gray-400 text-sm \
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition";

const BTN_CLASS: &str = "w-full py-2.5 px-4 mt-2 bg-blue-600 hover:bg-blue-700 \
    text-white text-sm font-semibold rounded-lg \
    transition-colors disabled:opacity-60 disabled:cursor-not-allowed";

#[component]
fn ErrorBanner(error: ReadSignal<Option<String>>) -> impl IntoView {
    view! {
        {move || error.get().map(|msg| view! {
            <div class="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4 text-sm text-red-600">
                <span>"⚠ " {msg}</span>
            </div>
        })}
    }
}

#[component]
fn AuthSuccessCard(
    title: &'static str,
    message: &'static str,
    link_href: &'static str,
    link_label: &'static str,
) -> impl IntoView {
    view! {
        <div class="min-h-screen bg-linear-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl shadow-lg p-10 w-full max-w-md text-center">
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5">
                    <span class="text-3xl">"✓"</span>
                </div>
                <h2 class="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
                <p class="text-gray-500 mb-6">{message}</p>
                <a href=link_href class="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors">
                    {link_label}
                </a>
            </div>
        </div>
    }
}

#[component]
fn AuthFormCard(
    title: &'static str,
    subtitle: &'static str,
    footer_text: &'static str,
    footer_link_href: &'static str,
    footer_link_label: &'static str,
    children: Children,
) -> impl IntoView {
    view! {
        <div class="min-h-screen bg-linear-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
                <div class="text-center mb-7">
                    <h1 class="text-3xl font-bold text-gray-900 mb-1">{title}</h1>
                    <p class="text-gray-500 text-sm">{subtitle}</p>
                </div>
                {children()}
                <p class="text-center text-sm text-gray-500 mt-6">
                    {footer_text}
                    " "
                    <a href=footer_link_href class="text-blue-600 hover:underline font-medium">{footer_link_label}</a>
                </p>
            </div>
        </div>
    }
}

#[island]
pub fn LoginPage(config: ApiConfig) -> impl IntoView {
    let config = StoredValue::new(config);
    let (username, set_username) = signal(String::new());
    let (password, set_password) = signal(String::new());
    let (error, set_error) = signal(Option::<String>::None);
    let (loading, set_loading) = signal(false);
    let (success, set_success) = signal(false);

    let on_submit = move |ev: leptos::ev::SubmitEvent| {
        ev.prevent_default();
        let cfg = config.get_value();
        let u = username.get();
        let p = password.get();
        set_error.set(None);
        set_loading.set(true);

        leptos::task::spawn_local(async move {
            let result: Result<(), String> = async {
                if u.trim().is_empty() { return Err("Username is required".into()); }
                if p.is_empty() { return Err("Password is required".into()); }

                let client = ApiClient::new(&cfg).map_err(|e| e.to_string())?;
                client.users().login(&LoginRequest { username: u.clone(), password: p.clone() })
                    .await
                    .map_err(|e| match e {
                        RestClientError::ResponseError { status, .. }
                            if status.as_u16() == 401 || status.as_u16() == 403 =>
                                "Incorrect username or password.".to_string(),
                        RestClientError::ResponseError { status, .. }
                            if status.as_u16() == 404 =>
                                "Account not found.".to_string(),
                        _ => "Login failed. Please try again.".to_string(),
                    })?;

                let creds = Credentials { username: u, password: p };
                save_credentials(&creds);
                #[cfg(target_arch = "wasm32")]
                {
                    let _ = web_sys::window()
                        .and_then(|w| w.location().assign("/dashboard").ok());
                }
                set_success.set(true);
                Ok(())
            }.await;

            if let Err(e) = result { set_error.set(Some(e)); }
            set_loading.set(false);
        });
    };

    view! {
        {move || if success.get() {
            view! {
                <AuthSuccessCard
                    title="Signed in!"
                    message="Redirecting to your dashboard…"
                    link_href="/dashboard"
                    link_label="Dashboard"
                />
            }.into_any()
        } else {
            view! {
                <AuthFormCard
                    title="Sign In"
                    subtitle="ML Service Personal Cabinet"
                    footer_text="Don't have an account?"
                    footer_link_href="/register"
                    footer_link_label="Register"
                >
                    <ErrorBanner error />
                    <form on:submit=on_submit class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">"Username"</label>
                            <input
                                type="text"
                                autocomplete="username"
                                placeholder="your_username"
                                class=INPUT_CLASS
                                prop:value=username
                                on:input=move |ev| set_username.set(event_target_value(&ev))
                            />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">"Password"</label>
                            <input
                                type="password"
                                autocomplete="current-password"
                                placeholder="••••••••"
                                class=INPUT_CLASS
                                prop:value=password
                                on:input=move |ev| set_password.set(event_target_value(&ev))
                            />
                        </div>
                        <button type="submit" disabled=loading class=BTN_CLASS>
                            {move || if loading.get() { "Signing in…" } else { "Sign In" }}
                        </button>
                    </form>
                </AuthFormCard>
            }.into_any()
        }}
    }
}

#[island]
pub fn RegisterPage(config: ApiConfig) -> impl IntoView {
    let config = StoredValue::new(config);
    let (username, set_username) = signal(String::new());
    let (email, set_email) = signal(String::new());
    let (password, set_password) = signal(String::new());
    let (error, set_error) = signal(Option::<String>::None);
    let (loading, set_loading) = signal(false);
    let (success, set_success) = signal(false);

    let on_submit = move |ev: leptos::ev::SubmitEvent| {
        ev.prevent_default();
        let cfg = config.get_value();
        let u = username.get();
        let e = email.get();
        let p = password.get();
        set_error.set(None);
        set_loading.set(true);

        leptos::task::spawn_local(async move {
            let result: Result<(), String> = async {
                if u.len() < 3 { return Err("Username must be at least 3 characters".into()); }
                if !e.contains('@') { return Err("Enter a valid email address".into()); }
                if p.len() < 6 { return Err("Password must be at least 6 characters".into()); }

                let client = ApiClient::new(&cfg).map_err(|e| e.to_string())?;
                client.users().register(&RegisterRequest {
                    username: u,
                    email: e,
                    password: p,
                }).await.map_err(|e| e.to_string())?;

                set_success.set(true);
                Ok(())
            }.await;

            if let Err(e) = result { set_error.set(Some(e)); }
            set_loading.set(false);
        });
    };

    view! {
        {move || if success.get() {
            view! {
                <AuthSuccessCard
                    title="Account created!"
                    message="You can now sign in."
                    link_href="/login"
                    link_label="Sign In"
                />
            }.into_any()
        } else {
            view! {
                <AuthFormCard
                    title="Create Account"
                    subtitle="Join the ML Service"
                    footer_text="Already have an account?"
                    footer_link_href="/login"
                    footer_link_label="Sign In"
                >
                    <ErrorBanner error />
                    <form on:submit=on_submit class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">"Username"</label>
                            <input
                                type="text"
                                autocomplete="username"
                                placeholder="your_username"
                                class=INPUT_CLASS
                                prop:value=username
                                on:input=move |ev| set_username.set(event_target_value(&ev))
                            />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">"Email"</label>
                            <input
                                type="email"
                                autocomplete="email"
                                placeholder="you@example.com"
                                class=INPUT_CLASS
                                prop:value=email
                                on:input=move |ev| set_email.set(event_target_value(&ev))
                            />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">"Password"</label>
                            <input
                                type="password"
                                autocomplete="new-password"
                                placeholder="Min. 6 characters"
                                class=INPUT_CLASS
                                prop:value=password
                                on:input=move |ev| set_password.set(event_target_value(&ev))
                            />
                        </div>
                        <button type="submit" disabled=loading class=BTN_CLASS>
                            {move || if loading.get() { "Creating…" } else { "Create Account" }}
                        </button>
                    </form>
                </AuthFormCard>
            }.into_any()
        }}
    }
}
