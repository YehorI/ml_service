use leptos::prelude::*;
use serde_json::Value;

#[cfg(target_arch = "wasm32")]
use crate::socketio::client as sio;

use crate::clients::api_client::ApiClient;
use crate::clients::config::ApiConfig;
use crate::clients::model::models::{MlModel, PredictRequest, Task, TaskStatus};
use crate::credentials::load_credentials;

fn status_badge_class(status: &TaskStatus) -> &'static str {
    match status {
        TaskStatus::Completed => "text-green-700 bg-green-50 border border-green-200",
        TaskStatus::Failed    => "text-red-700 bg-red-50 border border-red-200",
        _                     => "text-yellow-700 bg-yellow-50 border border-yellow-200",
    }
}

fn status_label(status: &TaskStatus) -> &'static str {
    match status {
        TaskStatus::Completed  => "Completed",
        TaskStatus::Failed     => "Failed",
        TaskStatus::Processing => "Processing…",
        _                      => "Pending…",
    }
}

#[island]
pub fn PredictPage(config: ApiConfig) -> impl IntoView {
    let config = StoredValue::new(config);

    // Form state
    let (models, set_models)                   = signal(Vec::<MlModel>::new());
    let (selected_model_id, set_selected_model_id) = signal(Option::<i64>::None);
    let (input_json, set_input_json)           = signal(String::from("{}"));
    let (balance, set_balance)                 = signal(Option::<f64>::None);

    // Submission state
    let (error, set_error)           = signal(Option::<String>::None);
    let (load_error, set_load_error) = signal(Option::<String>::None);
    let (submitting, set_submitting) = signal(false);

    // Result panel
    let (result_task, set_result_task) = signal(Option::<Task>::None);

    // History panel
    let (history, set_history)         = signal(Vec::<Task>::new());
    let (history_open, set_history_open) = signal(false);
    let (history_loading, set_history_loading) = signal(false);

    // WebSocket setup
    #[cfg(target_arch = "wasm32")]
    let socket = {
        use std::rc::Rc;
        use wasm_bindgen::prelude::*;
        let cfg = config.get_value();
        let sock = Rc::new(sio::connect(&cfg.model_base_url));
        if let Some(creds) = load_credentials() {
            sock.emit("join", &JsValue::from_str(&creds.username));
        }
        StoredValue::new_local(sock)
    };

    // Initial data load
    Effect::new(move |_| {
        let cfg = config.get_value();
        leptos::task::spawn_local(async move {
            // Models endpoint is public — always use unauthenticated client
            match ApiClient::new(&cfg) {
                Err(e) => set_load_error.set(Some(format!("Client init error: {}", e))),
                Ok(client) => match client.model().list_models().await {
                    Err(e) => set_load_error.set(Some(format!("Failed to load models: {}", e))),
                    Ok(ms) => {
                        let first_id = ms.first().map(|m| m.id);
                        set_models.set(ms);
                        set_selected_model_id.set(first_id);
                    }
                }
            }

            if let Some(creds) = load_credentials() {
                if let Ok(auth_client) = ApiClient::with_credentials(&cfg, &creds) {
                    if let Ok(b) = auth_client.wallet().get_balance().await {
                        set_balance.set(Some(b.amount));
                    }
                }
            }
        });
    });

    let selected_model = move || {
        let id = selected_model_id.get()?;
        models.get().into_iter().find(|m| m.id == id)
    };

    // Load history on demand
    let load_history = move || {
        let cfg = config.get_value();
        set_history_loading.set(true);
        leptos::task::spawn_local(async move {
            if let Some(creds) = load_credentials() {
                if let Ok(client) = ApiClient::with_credentials(&cfg, &creds) {
                    if let Ok(tasks) = client.model().list_tasks().await {
                        let mut tasks = tasks;
                        tasks.sort_by(|a, b| b.id.cmp(&a.id));
                        tasks.truncate(10);
                        set_history.set(tasks);
                    }
                }
            }
            set_history_loading.set(false);
        });
    };

    let toggle_history = {
        let load_history = load_history.clone();
        move |_| {
            let next = !history_open.get_untracked();
            set_history_open.set(next);
            if next && history.get_untracked().is_empty() {
                load_history();
            }
        }
    };

    let handle_submit = move |ev: leptos::ev::SubmitEvent| {
        ev.prevent_default();
        let cfg = config.get_value();
        let json_str = input_json.get();
        let model_id = selected_model_id.get();
        set_error.set(None);
        set_result_task.set(None);
        set_submitting.set(true);

        leptos::task::spawn_local(async move {
            let result: Result<(), String> = async {
                let model_id = model_id.ok_or("Please select a model")?;

                let input_data: Value = serde_json::from_str(&json_str)
                    .map_err(|e| format!("Invalid JSON: {}", e))?;

                let creds = load_credentials().ok_or("Not authenticated. Please sign in first.")?;
                let client = ApiClient::with_credentials(&cfg, &creds).map_err(|e| e.to_string())?;

                let current_balance = client.wallet().get_balance().await
                    .map_err(|e| format!("Could not check balance: {}", e))?.amount;
                set_balance.set(Some(current_balance));

                let cost = models.get_untracked()
                    .iter()
                    .find(|m| m.id == model_id)
                    .map(|m| m.cost_per_request)
                    .unwrap_or(0.0);

                if current_balance < cost {
                    return Err(format!(
                        "Insufficient balance: need {:.2} credits, have {:.2}",
                        cost, current_balance
                    ));
                }

                let task = client.model()
                    .submit_task(PredictRequest { model_id, input_data })
                    .await
                    .map_err(|e| e.to_string())?;

                let task_id = task.id;
                set_result_task.set(Some(task));

                #[cfg(target_arch = "wasm32")]
                {
                    use wasm_bindgen::prelude::*;
                    let cb_client = client.clone();
                    let cb = Closure::wrap(Box::new(move |data: JsValue| {
                        let event_id = js_sys::Reflect::get(&data, &JsValue::from_str("task_id"))
                            .ok()
                            .and_then(|v| v.as_f64())
                            .map(|v| v as i64);

                        if event_id != Some(task_id) { return; }

                        let client = cb_client.clone();
                        leptos::task::spawn_local(async move {
                            if let Ok(updated) = client.model().get_task(task_id).await {
                                if let Some(ref result) = updated.result {
                                    set_balance.set(Some(current_balance - result.credits_charged));
                                }
                                let is_done = matches!(updated.status, TaskStatus::Completed | TaskStatus::Failed);
                                set_result_task.set(Some(updated.clone()));
                                if is_done {
                                    set_submitting.set(false);
                                    // Refresh history if open
                                    if history_open.get_untracked() {
                                        set_history.update(|h| {
                                            h.retain(|t| t.id != task_id);
                                            h.insert(0, updated);
                                            h.truncate(10);
                                        });
                                    }
                                }
                            }
                        });
                    }) as Box<dyn Fn(JsValue)>);

                    socket.get_value().on("task_updated", &cb);
                    cb.forget();
                    return Ok(());
                }

                #[cfg(not(target_arch = "wasm32"))]
                Ok(())
            }.await;

            if let Err(e) = result {
                set_error.set(Some(e));
                set_submitting.set(false);
            }
        });
    };

    view! {
        <div class="max-w-6xl mx-auto px-4 py-8">
            <div class="flex items-center justify-between mb-6">
                <h1 class="text-3xl font-bold text-gray-900">"ML Prediction"</h1>
                {move || balance.get().map(|b| view! {
                    <span class="text-sm text-gray-500">
                        "Balance: "
                        <span class="font-semibold text-gray-800">{format!("{:.2} credits", b)}</span>
                    </span>
                })}
            </div>

            {move || load_error.get().map(|msg| view! {
                <div class="bg-orange-50 border border-orange-200 rounded-lg px-4 py-3 mb-4 text-sm text-orange-700">
                    "⚠ " {msg}
                </div>
            })}
            {move || error.get().map(|msg| view! {
                <div class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4 text-sm text-red-600">
                    "⚠ " {msg}
                </div>
            })}

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

                // LEFT: Submission form
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <h2 class="text-base font-semibold text-gray-800 mb-5">"Submit"</h2>
                    <form on:submit=handle_submit class="space-y-5">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">"Model"</label>
                            <select
                                class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                on:change=move |ev| {
                                    let val = event_target_value(&ev);
                                    set_selected_model_id.set(val.parse::<i64>().ok());
                                }
                            >
                                {move || models.get().into_iter().map(|m| {
                                    let id = m.id.to_string();
                                    let label = format!("{} — {:.2} credits", m.name, m.cost_per_request);
                                    view! { <option value=id>{label}</option> }
                                }).collect_view()}
                            </select>
                            {move || selected_model().map(|m| view! {
                                <p class="text-xs text-gray-400 mt-1">{m.description}</p>
                            })}
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1.5">"Input (JSON)"</label>
                            <textarea
                                rows="10"
                                placeholder=r#"{"feature1": 1.0, "feature2": "value"}"#
                                class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
                                prop:value=input_json
                                on:input=move |ev| set_input_json.set(event_target_value(&ev))
                            />
                        </div>

                        <button
                            type="submit"
                            disabled=move || submitting.get() || selected_model_id.get().is_none()
                            class="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                            {move || if submitting.get() { "Waiting for result…" } else { "Submit" }}
                        </button>
                    </form>
                </div>

                // RIGHT: Result + history
                <div class="flex flex-col gap-4">

                    // Result panel
                    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex-1">
                        <h2 class="text-base font-semibold text-gray-800 mb-5">"Result"</h2>

                        {move || match result_task.get() {
                            None => view! {
                                <div class="flex flex-col items-center justify-center h-48 text-gray-300 select-none">
                                    <p class="text-5xl mb-3">"🥚"</p>
                                    <p class="text-sm">"Submit a prediction to see results"</p>
                                </div>
                            }.into_any(),

                            Some(task) => {
                                let is_pending = matches!(task.status, TaskStatus::Pending | TaskStatus::Processing);
                                view! {
                                    <div class="space-y-4">
                                        <div class="flex items-center gap-3">
                                            <span class=format!(
                                                "inline-block px-3 py-1 rounded-full text-xs font-semibold {}",
                                                status_badge_class(&task.status)
                                            )>
                                                {status_label(&task.status)}
                                            </span>
                                            <span class="text-xs text-gray-400 font-mono">"#"{task.id.to_string()}</span>
                                        </div>

                                        {if is_pending {
                                            view! {
                                                <div class="flex items-center gap-2 text-sm text-yellow-600">
                                                    <span class="animate-spin inline-block">"⟳"</span>
                                                    "Processing your request…"
                                                </div>
                                            }.into_any()
                                        } else {
                                            view! { <div/> }.into_any()
                                        }}

                                        <div>
                                            <p class="text-xs text-gray-500 mb-1">"Input"</p>
                                            <pre class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm font-mono overflow-x-auto whitespace-pre-wrap">
                                                {serde_json::to_string_pretty(&task.input_data).unwrap_or_default()}
                                            </pre>
                                        </div>

                                        {task.result.map(|r| view! {
                                            <div class="space-y-3">
                                                <div>
                                                    <p class="text-xs text-gray-500 mb-1">"Credits charged"</p>
                                                    <p class="text-xl font-bold text-gray-900">{format!("{:.2}", r.credits_charged)}</p>
                                                </div>
                                                <div>
                                                    <p class="text-xs text-gray-500 mb-1">"Output"</p>
                                                    <pre class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm font-mono overflow-x-auto whitespace-pre-wrap">
                                                        {serde_json::to_string_pretty(&r.output_data).unwrap_or_default()}
                                                    </pre>
                                                </div>
                                            </div>
                                        })}

                                        <p class="text-xs text-gray-400">{task.created_at.chars().take(19).collect::<String>()}</p>
                                    </div>
                                }.into_any()
                            }
                        }}
                    </div>

                    // History drawer
                    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <button
                            class="w-full flex items-center justify-between px-6 py-4 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
                            on:click=toggle_history
                        >
                            <span>"Recent Requests"</span>
                            <span class="text-gray-400 text-xs">
                                {move || if history_open.get() { "▲ Hide" } else { "▼ Show" }}
                            </span>
                        </button>

                        {move || if history_open.get() {
                            view! {
                                <div class="border-t border-gray-100">
                                    {move || if history_loading.get() {
                                        view! {
                                            <p class="px-6 py-8 text-sm text-gray-400">"Loading…"</p>
                                        }.into_any()
                                    } else if history.get().is_empty() {
                                        view! {
                                            <p class="px-6 py-8 text-sm text-gray-400">"No requests yet."</p>
                                        }.into_any()
                                    } else {
                                        view! {
                                            <ul class="divide-y divide-gray-50 max-h-72 overflow-y-auto">
                                                {history.get().into_iter().map(|task| {
                                                    let badge = status_badge_class(&task.status);
                                                    let label = status_label(&task.status);
                                                    let credits = task.result.as_ref()
                                                        .map(|r| format!("{:.2} cr", r.credits_charged))
                                                        .unwrap_or_default();
                                                    let task_clone = task.clone();
                                                    view! {
                                                        <li
                                                            class="flex items-center gap-3 px-6 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
                                                            on:click=move |_| set_result_task.set(Some(task_clone.clone()))
                                                        >
                                                            <span class=format!("px-2 py-0.5 rounded-full text-xs font-medium border {}", badge)>
                                                                {label}
                                                            </span>
                                                            <span class="text-xs text-gray-400 font-mono flex-1">"#"{task.id.to_string()}</span>
                                                            <span class="text-xs text-gray-500">{credits}</span>
                                                            <span class="text-xs text-gray-300">
                                                                {task.created_at.chars().take(10).collect::<String>()}
                                                            </span>
                                                        </li>
                                                    }
                                                }).collect_view()}
                                            </ul>
                                        }.into_any()
                                    }}
                                </div>
                            }.into_any()
                        } else {
                            view! { <div/> }.into_any()
                        }}
                    </div>
                </div>
            </div>
        </div>
    }
}
