use leptos::prelude::*;
use serde_json::Value;

async fn wasm_sleep(ms: i32) {
    #[cfg(target_arch = "wasm32")]
    {
        use wasm_bindgen::prelude::*;
        use wasm_bindgen_futures::JsFuture;
        let promise = js_sys::Promise::new(&mut |resolve, _| {
            let cb = Closure::<dyn FnMut()>::once(move || { let _ = resolve.call0(&JsValue::NULL); });
            web_sys::window().unwrap()
                .set_timeout_with_callback_and_timeout_and_arguments_0(
                    cb.as_ref().unchecked_ref(), ms,
                ).unwrap();
            cb.forget();
        });
        JsFuture::from(promise).await.ok();
    }
    #[cfg(not(target_arch = "wasm32"))]
    { let _ = ms; }
}
use crate::clients::api_client::ApiClient;
use crate::clients::config::ApiConfig;
use crate::clients::model::models::{MlModel, PredictRequest, Task, TaskStatus};
use crate::credentials::load_credentials;

#[island]
pub fn PredictPage(config: ApiConfig) -> impl IntoView {
    let config = StoredValue::new(config);
    let (models, set_models) = signal(Vec::<MlModel>::new());
    let (selected_model_id, set_selected_model_id) = signal(Option::<i64>::None);
    let (input_json, set_input_json) = signal(String::from("{}"));
    let (error, set_error) = signal(Option::<String>::None);
    let (loading, set_loading) = signal(false);
    let (result_task, set_result_task) = signal(Option::<Task>::None);
    let (balance, set_balance) = signal(Option::<f64>::None);

    Effect::new(move |_| {
        let cfg = config.get_value();
        leptos::task::spawn_local(async move {
            let Ok(client) = ApiClient::new(&cfg) else { return; };
            if let Ok(ms) = client.model().list_models().await {
                let first_id = ms.first().map(|m| m.id);
                set_models.set(ms);
                set_selected_model_id.set(first_id);
            }

            let creds = load_credentials();
            if let Some(creds) = creds {
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

    let handle_submit = move |ev: leptos::ev::SubmitEvent| {
        ev.prevent_default();
        let cfg = config.get_value();
        let json_str = input_json.get();
        let model_id = selected_model_id.get();
        set_error.set(None);
        set_result_task.set(None);
        set_loading.set(true);

        leptos::task::spawn_local(async move {
            let result: Result<(), String> = async {
                let model_id = model_id.ok_or("Please select a model")?;

                let input_data: Value = serde_json::from_str(&json_str)
                    .map_err(|e| format!("Invalid JSON input: {}", e))?;

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

                for _ in 0..30 {
                    wasm_sleep(2000).await;


                    let updated = client.model().get_task(task_id).await
                        .map_err(|e| e.to_string())?;

                    let done = matches!(updated.status, TaskStatus::Completed | TaskStatus::Failed);
                    if let Some(ref result) = updated.result {
                        let new_balance = current_balance - result.credits_charged;
                        set_balance.set(Some(new_balance));
                    }
                    set_result_task.set(Some(updated));
                    if done { break; }
                }

                Ok(())
            }.await;

            if let Err(e) = result { set_error.set(Some(e)); }
            set_loading.set(false);
        });
    };

    view! {
        <div class="max-w-3xl mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">"ML Prediction"</h1>

            {move || balance.get().map(|b| view! {
                <p class="text-sm text-gray-500 mb-6">"Balance: " <span class="font-semibold text-gray-800">{format!("{:.2} credits", b)}</span></p>
            })}

            {move || error.get().map(|msg| view! {
                <div class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-6 text-sm text-red-600">"⚠️" {msg}</div>
            })}

            <form on:submit=handle_submit class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-5">

                // Model selector
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">"Select Model"</label>
                    <select
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        on:change=move |ev| {
                            let val = event_target_value(&ev);
                            set_selected_model_id.set(val.parse::<i64>().ok());
                        }
                    >
                        {move || models.get().into_iter().map(|m| {
                            let id = m.id.to_string();
                            let label = format!("{} — {:.2} credits/request", m.name, m.cost_per_request);
                            view! { <option value=id>{label}</option> }
                        }).collect_view()}
                    </select>

                    {move || selected_model().map(|m| view! {
                        <p class="text-xs text-gray-500 mt-1">{m.description}</p>
                    })}
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1.5">
                        "Input Data (JSON)"
                    </label>
                    <textarea
                        rows="8"
                        placeholder=r#"{"feature1": 1.0, "feature2": "value"}"#
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
                        prop:value=input_json
                        on:input=move |ev| set_input_json.set(event_target_value(&ev))
                    />
                    <p class="text-xs text-gray-400 mt-1">"Must be valid JSON. Invalid entries will be reported."</p>
                </div>

                <button
                    type="submit"
                    disabled=move || loading.get() || selected_model_id.get().is_none()
                    class="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                    {move || if loading.get() { "Submitting…" } else { "Submit Prediction" }}
                </button>
            </form>

            // Result
            {move || result_task.get().map(|task| {
                let status_class = match task.status {
                    TaskStatus::Completed => "text-green-700 bg-green-50 border-green-200",
                    TaskStatus::Failed => "text-red-700 bg-red-50 border-red-200",
                    _ => "text-yellow-700 bg-yellow-50 border-yellow-200",
                };
                let status_label = match task.status {
                    TaskStatus::Completed => "Completed",
                    TaskStatus::Failed => "Failed",
                    TaskStatus::Processing => "Processing…",
                    _ => "Pending…",
                };

                view! {
                    <div class="mt-6 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                        <h2 class="text-lg font-semibold text-gray-900 mb-3">"Result"</h2>
                        <div class=format!("inline-block px-3 py-1 rounded-full text-xs font-semibold border mb-4 {}", status_class)>
                            {status_label}
                        </div>

                        {task.result.map(|r| view! {
                            <div class="space-y-3">
                                <div>
                                    <p class="text-xs text-gray-500 mb-1">"Credits charged"</p>
                                    <p class="text-lg font-bold text-gray-900">{format!("{:.2}", r.credits_charged)}</p>
                                </div>
                                <div>
                                    <p class="text-xs text-gray-500 mb-1">"Output"</p>
                                    <pre class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm font-mono overflow-x-auto whitespace-pre-wrap">
                                        {serde_json::to_string_pretty(&r.output_data).unwrap_or_default()}
                                    </pre>
                                </div>
                            </div>
                        })}

                        <p class="text-xs text-gray-400 mt-3">"Task ID: " {task.id.to_string()} " · " {task.created_at}</p>
                    </div>
                }
            })}
        </div>
    }
}
