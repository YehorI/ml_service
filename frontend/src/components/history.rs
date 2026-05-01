use leptos::prelude::*;
use crate::clients::api_client::ApiClient;
use crate::clients::config::ApiConfig;
use crate::clients::model::models::{Task, TaskStatus};
use crate::clients::wallet::models::Transaction;
use crate::credentials::load_credentials;

#[island]
pub fn HistoryPage(config: ApiConfig) -> impl IntoView {
    let config = StoredValue::new(config);
    let (transactions, set_transactions) = signal(Vec::<Transaction>::new());
    let (tasks, set_tasks) = signal(Vec::<Task>::new());
    let (error, set_error) = signal(Option::<String>::None);
    let (loading, set_loading) = signal(true);
    let (tab, set_tab) = signal(0u8); // 0=transactions, 1=tasks

    Effect::new(move |_| {
        let cfg = config.get_value();
        set_loading.set(true);
        leptos::task::spawn_local(async move {
            let creds = load_credentials();
            let Some(creds) = creds else {
                set_error.set(Some("Not authenticated. Please sign in.".into()));
                set_loading.set(false);
                return;
            };
            match ApiClient::with_credentials(&cfg, &creds) {
                Err(e) => set_error.set(Some(e.to_string())),
                Ok(client) => {
                    match client.wallet().list_transactions().await {
                        Ok(txs) => set_transactions.set(txs),
                        Err(e) => set_error.set(Some(format!("Transactions error: {}", e))),
                    }
                    match client.model().list_tasks().await {
                        Ok(ts) => set_tasks.set(ts),
                        Err(e) => set_error.set(Some(format!("Tasks error: {}", e))),
                    }
                }
            }
            set_loading.set(false);
        });
    });

    let tab_class = move |active: bool| {
        if active {
            "px-4 py-2 rounded-lg text-sm font-semibold bg-white shadow-sm text-blue-600"
        } else {
            "px-4 py-2 rounded-lg text-sm font-medium text-gray-500 hover:text-gray-700"
        }
    };

    view! {
        <div class="max-w-4xl mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-6">"History"</h1>

            {move || error.get().map(|msg| view! {
                <div class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 mb-6 text-sm text-red-600">"⚠ " {msg}</div>
            })}

            <div class="flex bg-gray-100 rounded-xl p-1 mb-6 w-fit">
                <button class=move || tab_class(tab.get() == 0) on:click=move |_| set_tab.set(0)>
                    "Transactions"
                </button>
                <button class=move || tab_class(tab.get() == 1) on:click=move |_| set_tab.set(1)>
                    "ML Requests"
                </button>
            </div>

            {move || if loading.get() {
                view! { <p class="text-gray-500">"Loading…"</p> }.into_any()
            } else if tab.get() == 0 {
                let txs = transactions.get();
                if txs.is_empty() {
                    view! { <p class="text-gray-500 text-sm">"No transactions yet."</p> }.into_any()
                } else {
                    view! {
                        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                            <table class="w-full text-sm">
                                <thead class="bg-gray-50 border-b border-gray-100">
                                    <tr>
                                        <th class="text-left px-4 py-3 text-gray-500 font-medium">"Date"</th>
                                        <th class="text-left px-4 py-3 text-gray-500 font-medium">"Type"</th>
                                        <th class="text-right px-4 py-3 text-gray-500 font-medium">"Amount"</th>
                                        <th class="text-left px-4 py-3 text-gray-500 font-medium">"Status"</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {txs.into_iter().map(|tx| {
                                        let is_deposit = tx.transaction_type == "deposit";
                                        let amount_class = if is_deposit { "text-green-600 font-semibold" } else { "text-red-600 font-semibold" };
                                        let amount_sign = if is_deposit { "+" } else { "-" };
                                        let status_label = if tx.is_applied { "Applied" } else { "Pending" };
                                        view! {
                                            <tr class="border-b border-gray-50 hover:bg-gray-50">
                                                <td class="px-4 py-3 text-gray-500 text-xs">{tx.created_at.chars().take(19).collect::<String>()}</td>
                                                <td class="px-4 py-3 capitalize">{tx.transaction_type}</td>
                                                <td class=format!("px-4 py-3 text-right {}", amount_class)>
                                                    {format!("{}{:.2}", amount_sign, tx.amount)}
                                                </td>
                                                <td class="px-4 py-3 text-gray-500">{status_label}</td>
                                            </tr>
                                        }
                                    }).collect_view()}
                                </tbody>
                            </table>
                        </div>
                    }.into_any()
                }
            } else {
                let ts = tasks.get();
                if ts.is_empty() {
                    view! { <p class="text-gray-500 text-sm">"No ML requests yet."</p> }.into_any()
                } else {
                    view! {
                        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                            <table class="w-full text-sm">
                                <thead class="bg-gray-50 border-b border-gray-100">
                                    <tr>
                                        <th class="text-left px-4 py-3 text-gray-500 font-medium">"Date"</th>
                                        <th class="text-left px-4 py-3 text-gray-500 font-medium">"Task ID"</th>
                                        <th class="text-left px-4 py-3 text-gray-500 font-medium">"Status"</th>
                                        <th class="text-right px-4 py-3 text-gray-500 font-medium">"Credits"</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {ts.into_iter().map(|task| {
                                        let status_class = match task.status {
                                            TaskStatus::Completed => "text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded-full text-xs",
                                            TaskStatus::Failed => "text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded-full text-xs",
                                            _ => "text-yellow-700 bg-yellow-50 border border-yellow-200 px-2 py-0.5 rounded-full text-xs",
                                        };
                                        let status_label = match task.status {
                                            TaskStatus::Completed => "Completed",
                                            TaskStatus::Failed => "Failed",
                                            TaskStatus::Processing => "Processing",
                                            _ => "Pending",
                                        };
                                        let credits = task.result.as_ref().map(|r| format!("{:.2}", r.credits_charged)).unwrap_or("—".to_string());
                                        view! {
                                            <tr class="border-b border-gray-50 hover:bg-gray-50">
                                                <td class="px-4 py-3 text-gray-500 text-xs">{task.created_at.chars().take(19).collect::<String>()}</td>
                                                <td class="px-4 py-3 text-gray-700 font-mono text-xs">{"#"}{task.id.to_string()}</td>
                                                <td class="px-4 py-3"><span class=status_class>{status_label}</span></td>
                                                <td class="px-4 py-3 text-right text-gray-700">{credits}</td>
                                            </tr>
                                        }
                                    }).collect_view()}
                                </tbody>
                            </table>
                        </div>
                    }.into_any()
                }
            }}
        </div>
    }
}
