use std::collections::HashMap;
use leptos::prelude::*;
use crate::clients::api_client::ApiClient;
use crate::clients::config::ApiConfig;
use crate::clients::users::models::User;
use crate::credentials::load_credentials;

#[island]
pub fn AdminPage(config: ApiConfig) -> impl IntoView {
    let config = StoredValue::new(config);
    let (users, set_users) = signal(Vec::<User>::new());
    let (balances, set_balances) = signal(HashMap::<i64, f64>::new());
    let (loading, set_loading) = signal(true);
    let (error, set_error) = signal(Option::<String>::None);
    let (selected_user_id, set_selected_user_id) = signal(Option::<i64>::None);
    let (deposit_amount, set_deposit_amount) = signal(String::from("10"));
    let (deposit_loading, set_deposit_loading) = signal(false);
    let (deposit_error, set_deposit_error) = signal(Option::<String>::None);
    let (deposit_success, set_deposit_success) = signal(Option::<String>::None);

    let load_data = move || {
        let cfg = config.get_value();
        set_error.set(None);
        set_loading.set(true);

        leptos::task::spawn_local(async move {
            let creds = load_credentials();
            let Some(creds) = creds else {
                set_error.set(Some("Not authenticated. Please sign in.".into()));
                set_loading.set(false);
                return;
            };

            if creds.role.as_deref() != Some("admin") {
                set_error.set(Some("Access denied: admin only.".into()));
                set_loading.set(false);
                return;
            }

            let client = match ApiClient::with_credentials(&cfg, &creds) {
                Ok(c) => c,
                Err(e) => {
                    set_error.set(Some(e.to_string()));
                    set_loading.set(false);
                    return;
                }
            };

            match client.users().list_users().await {
                Err(e) => {
                    set_error.set(Some(format!("Failed to load users: {}", e)));
                    set_loading.set(false);
                    return;
                }
                Ok(user_list) => {
                    let ids: Vec<i64> = user_list.iter().map(|u| u.id).collect();
                    set_users.set(user_list);

                    let mut bal_map = HashMap::new();
                    for id in ids {
                        if let Ok(b) = client.wallet().admin_get_balance(id).await {
                            bal_map.insert(id, b.amount);
                        }
                    }
                    set_balances.set(bal_map);
                }
            }

            set_loading.set(false);
        });
    };

    {
        let load_for_mount = load_data.clone();
        Effect::new(move |_| { load_for_mount(); });
    }

    let handle_deposit = move |ev: leptos::ev::SubmitEvent| {
        ev.prevent_default();
        let cfg = config.get_value();
        let amount_str = deposit_amount.get();
        let Some(uid) = selected_user_id.get() else {
            set_deposit_error.set(Some("Select a user first.".into()));
            return;
        };
        set_deposit_error.set(None);
        set_deposit_success.set(None);
        set_deposit_loading.set(true);

        leptos::task::spawn_local(async move {
            let result: Result<f64, String> = async {
                let amount: f64 = amount_str.trim().parse().map_err(|_| "Invalid amount".to_string())?;
                if amount <= 0.0 { return Err("Amount must be positive".into()); }
                let creds = load_credentials().ok_or("Not authenticated")?;
                let client = ApiClient::with_credentials(&cfg, &creds).map_err(|e| e.to_string())?;
                let result = client.wallet().admin_deposit(uid, amount).await.map_err(|e| e.to_string())?;
                Ok(result.amount)
            }.await;

            match result {
                Err(e) => set_deposit_error.set(Some(e)),
                Ok(new_balance) => {
                    set_balances.update(|m| { m.insert(uid, new_balance); });
                    set_deposit_success.set(Some(format!("Added credits. New balance: {:.2}", new_balance)));
                }
            }
            set_deposit_loading.set(false);
        });
    };

    view! {
        <div class="max-w-5xl mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-8">"Admin Panel"</h1>

            {move || error.get().map(|msg| view! {
                <div class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-6 text-sm text-red-600">"⚠ " {msg}</div>
            })}

            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-8">
                <h2 class="text-lg font-semibold text-gray-900 mb-4">"Users"</h2>
                {move || if loading.get() {
                    view! { <p class="text-gray-400 text-sm animate-pulse">"Loading users…"</p> }.into_any()
                } else {
                    let user_list = users.get();
                    let bal_map = balances.get();
                    view! {
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead>
                                    <tr class="border-b border-gray-100 text-left text-gray-500">
                                        <th class="pb-3 pr-6 font-medium">"Username"</th>
                                        <th class="pb-3 pr-6 font-medium">"Email"</th>
                                        <th class="pb-3 pr-6 font-medium">"Role"</th>
                                        <th class="pb-3 font-medium">"Balance"</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {user_list.into_iter().map(|u| {
                                        let uid = u.id;
                                        let balance = bal_map.get(&uid).copied();
                                        let is_selected = move || selected_user_id.get() == Some(uid);
                                        view! {
                                            <tr
                                                class="border-b border-gray-50 cursor-pointer hover:bg-blue-50 transition-colors"
                                                class:bg-blue-50=is_selected
                                                on:click=move |_| set_selected_user_id.set(Some(uid))
                                            >
                                                <td class="py-3 pr-6 font-medium text-gray-900">{u.username.clone()}</td>
                                                <td class="py-3 pr-6 text-gray-600">{u.email.clone()}</td>
                                                <td class="py-3 pr-6">
                                                    <span class=move || if u.role == "admin" {
                                                        "px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-semibold"
                                                    } else {
                                                        "px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-semibold"
                                                    }>
                                                        {u.role.clone()}
                                                    </span>
                                                </td>
                                                <td class="py-3 text-gray-700">
                                                    {match balance {
                                                        Some(b) => format!("{:.2} credits", b),
                                                        None => "—".to_string(),
                                                    }}
                                                </td>
                                            </tr>
                                        }
                                    }).collect_view()}
                                </tbody>
                            </table>
                        </div>
                    }.into_any()
                }}
            </div>

            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <h2 class="text-lg font-semibold text-gray-900 mb-4">"Add Credits"</h2>
                {move || deposit_error.get().map(|msg| view! {
                    <div class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-4 text-sm text-red-600">"⚠ " {msg}</div>
                })}
                {move || deposit_success.get().map(|msg| view! {
                    <div class="bg-green-50 border border-green-200 rounded-lg px-4 py-3 mb-4 text-sm text-green-700">"✓ " {msg}</div>
                })}
                <form on:submit=handle_deposit class="flex gap-3 items-end flex-wrap">
                    <div class="flex-1 min-w-48">
                        <label class="block text-sm font-medium text-gray-700 mb-1.5">"User"</label>
                        <select
                            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                            on:change=move |ev| {
                                let val = event_target_value(&ev);
                                set_selected_user_id.set(val.parse::<i64>().ok());
                            }
                        >
                            <option value="">"— select user —"</option>
                            {move || users.get().into_iter().map(|u| {
                                let uid_str = u.id.to_string();
                                let is_sel = selected_user_id.get() == Some(u.id);
                                view! {
                                    <option value=uid_str prop:selected=is_sel>
                                        {format!("{} ({})", u.username, u.email)}
                                    </option>
                                }
                            }).collect_view()}
                        </select>
                    </div>
                    <div class="w-40">
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
        </div>
    }
}
