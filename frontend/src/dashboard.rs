use leptos::prelude::*;
use crate::clients::api_client::ApiClient;
use crate::clients::config::ApiConfig;
use crate::credentials::load_credentials;

#[cfg(target_arch = "wasm32")]
use crate::socketio::client as sio;

#[island]
pub fn Dashboard(config: ApiConfig) -> impl IntoView {
    let config = StoredValue::new(config);
    let (balance, set_balance) = signal(Option::<f64>::None);
    let (deposit_amount, set_deposit_amount) = signal(String::from("10"));
    let (error, set_error) = signal(Option::<String>::None);
    let (deposit_error, set_deposit_error) = signal(Option::<String>::None);
    let (deposit_loading, set_deposit_loading) = signal(false);
    let (task_count, set_task_count) = signal(Option::<usize>::None);

    let load_data = move || {
        let cfg = config.get_value();
        set_error.set(None);
        leptos::task::spawn_local(async move {
            let creds = load_credentials();
            let Some(creds) = creds else {
                set_error.set(Some("Not authenticated. Please sign in.".into()));
                return;
            };
            match ApiClient::with_credentials(&cfg, &creds) {
                Err(e) => set_error.set(Some(e.to_string())),
                Ok(client) => {
                    match client.wallet().get_balance().await {
                        Ok(b) => set_balance.set(Some(b.amount)),
                        Err(e) => set_error.set(Some(format!("Balance error: {}", e))),
                    }
                    match client.model().list_tasks().await {
                        Ok(tasks) => set_task_count.set(Some(tasks.len())),
                        Err(_) => {}
                    }
                }
            }
        });
    };

    let load_on_mount = load_data.clone();
    Effect::new(move |_| { load_on_mount(); });

    #[cfg(target_arch = "wasm32")]
    {
        use wasm_bindgen::prelude::*;
        let load_on_update = load_data.clone();
        Effect::new(move |_| {
            let cfg = config.get_value();
            let Some(creds) = load_credentials() else { return; };

            let cb = Closure::wrap(Box::new(move |_data: JsValue| {
                load_on_update();
            }) as Box<dyn Fn(JsValue)>);

            let socket = sio::connect(&cfg.model_base_url);
            socket.emit("join", &JsValue::from_str(&creds.username));
            socket.on("task_updated", &cb);
            cb.forget();
        });
    }

    let handle_deposit = move |ev: leptos::ev::SubmitEvent| {
        ev.prevent_default();
        let cfg = config.get_value();
        let amount_str = deposit_amount.get();
        set_deposit_error.set(None);
        set_deposit_loading.set(true);

        leptos::task::spawn_local(async move {
            let result: Result<(), String> = async {
                let amount: f64 = amount_str.trim().parse().map_err(|_| "Invalid amount".to_string())?;
                if amount <= 0.0 { return Err("Amount must be positive".into()); }

                let creds = load_credentials().ok_or("Not authenticated")?;
                let client = ApiClient::with_credentials(&cfg, &creds).map_err(|e| e.to_string())?;
                let result = client.wallet().deposit(amount).await.map_err(|e| e.to_string())?;
                set_balance.set(Some(result.amount));
                Ok(())
            }.await;

            if let Err(e) = result { set_deposit_error.set(Some(e)); }
            set_deposit_loading.set(false);
        });
    };

    view! {
        <div class="max-w-4xl mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-8">"Dashboard"</h1>

            {move || error.get().map(|msg| view! {
                <div class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-6 text-sm text-red-600">"⚠ " {msg}</div>
            })}

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <p class="text-sm text-gray-500 mb-1">"Current Balance"</p>
                    <p class="text-4xl font-bold text-gray-900 mb-1">
                        {move || match balance.get() {
                            Some(b) => format!("{:.2} credits", b),
                            None => "Loading…".to_string(),
                        }}
                    </p>
                    <button
                        class="mt-3 text-xs text-blue-600 hover:underline"
                        on:click=move |_| load_data()
                    >
                        "Refresh"
                    </button>
                </div>

                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <p class="text-sm text-gray-500 mb-1">"Total ML Requests"</p>
                    <p class="text-4xl font-bold text-gray-900">
                        {move || match task_count.get() {
                            Some(n) => n.to_string(),
                            None => "—".to_string(),
                        }}
                    </p>
                    <a href="/history" class="mt-3 inline-block text-xs text-blue-600 hover:underline">"View history →"</a>
                </div>
            </div>

            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
                <h2 class="text-lg font-semibold text-gray-900 mb-4">"Add Credits"</h2>
                {move || deposit_error.get().map(|msg| view! {
                    <div class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4 text-sm text-red-600">"⚠ " {msg}</div>
                })}
                <form on:submit=handle_deposit class="flex gap-3 items-end">
                    <div class="flex-1">
                        <label class="block text-sm font-medium text-gray-700 mb-1.5">"Amount (credits)"</label>
                        <input
                            type="number"
                            min="1"
                            step="1"
                            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            prop:value=deposit_amount
                            on:input=move |ev| set_deposit_amount.set(event_target_value(&ev))
                        />
                    </div>
                    <button
                        type="submit"
                        disabled=deposit_loading
                        class="px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-60"
                    >
                        {move || if deposit_loading.get() { "Adding…" } else { "Add Credits" }}
                    </button>
                </form>
            </div>

            // Quick links
            <div class="grid grid-cols-2 gap-4">
                <a href="/predict"
                    class="block bg-blue-600 hover:bg-blue-700 text-white rounded-xl p-5 text-center transition-colors">
                    <p class="text-2xl mb-2">"🥚"</p>
                    <p class="font-semibold">"New ML Request"</p>
                    <p class="text-xs text-blue-200 mt-1">"Submit data for prediction"</p>
                </a>
                <a href="/history"
                    class="block bg-gray-800 hover:bg-gray-900 text-white rounded-xl p-5 text-center transition-colors">
                    <p class="text-2xl mb-2">"🍳"</p>
                    <p class="font-semibold">"View History"</p>
                    <p class="text-xs text-gray-400 mt-1">"Transactions & predictions"</p>
                </a>
            </div>
        </div>
    }
}
