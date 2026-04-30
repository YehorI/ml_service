use leptos::prelude::*;
use leptos_meta::{provide_meta_context, MetaTags, Stylesheet, Title};
use leptos_router::{
    components::{A, Route, Router, Routes},
    StaticSegment,
};

use crate::clients::config::ApiConfig;
use crate::components::auth::{LoginPage, RegisterPage};
use crate::components::nav::NavAuthButtons;
use crate::components::dashboard::Dashboard;
use crate::components::history::HistoryPage;
use crate::components::predict::PredictPage;

pub fn shell(options: LeptosOptions) -> impl IntoView {
    view! {
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1"/>
                <AutoReload options=options.clone()/>
                <HydrationScripts options islands=true/>
                <MetaTags/>
            </head>
            <body>
                <App/>
            </body>
        </html>
    }
}

#[component]
pub fn App() -> impl IntoView {
    provide_meta_context();

    view! {
        <Stylesheet id="leptos" href="/pkg/ml-frontend.css"/>
        <Title text="ML Service"/>

        <Router>
            <Nav/>
            <main>
                <Routes fallback=|| view! { <NotFound/> }>
                    <Route path=StaticSegment("") view=Home/>
                    <Route path=StaticSegment("login") view=LoginRoute/>
                    <Route path=StaticSegment("register") view=RegisterRoute/>
                    <Route path=StaticSegment("dashboard") view=DashboardRoute/>
                    <Route path=StaticSegment("predict") view=PredictRoute/>
                    <Route path=StaticSegment("history") view=HistoryRoute/>
                </Routes>
            </main>
        </Router>
    }
}

#[component]
fn Nav() -> impl IntoView {
    view! {
        <nav class="flex items-center gap-6 px-6 py-4 bg-white border-b border-gray-200 shadow-sm">
            <A href="/" attr:class="text-base font-bold text-gray-900 hover:text-blue-600 transition-colors mr-4">
                "👨‍🍳 ML Service"
            </A>
            <A href="/dashboard" attr:class="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">
                "Dashboard"
            </A>
            <A href="/predict" attr:class="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">
                "Predict"
            </A>
            <A href="/history" attr:class="text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors">
                "History"
            </A>
            <div class="ml-auto flex gap-3">
                <NavAuthButtons/>
            </div>
        </nav>
    }
}

fn get_config() -> ApiConfig {
    ApiConfig::from_env().unwrap_or_default()
}

#[component]
fn Home() -> impl IntoView {
    view! {
        <div class="max-w-4xl mx-auto px-4 py-16 text-center">
            <p class="text-6xl mb-6">"🐦‍⬛"</p>
            <h1 class="text-4xl font-bold text-gray-900 mb-4">"ML Prediction Service"</h1>
            <p class="text-lg text-gray-500 mb-10 max-w-xl mx-auto">
                "Submit your data to cutting-edge machine learning models and receive instant predictions. "
                "Pay only for successful results."
            </p>
            <div class="flex justify-center gap-4 mb-16">
                <a href="/register" class="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors text-sm">
                    "Get Started"
                </a>
                <a href="/login" class="px-8 py-3 border border-gray-300 hover:border-gray-400 text-gray-700 font-semibold rounded-xl transition-colors text-sm">
                    "Sign In"
                </a>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                    <p class="text-2xl mb-3">"🧑‍🌾"</p>
                    <h3 class="font-semibold text-gray-900 mb-2">"Order"</h3>
                    <p class="text-sm text-gray-500">"Cook from your ingridients."</p>
                </div>
                <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                    <p class="text-2xl mb-3">"🍽️"</p>
                    <h3 class="font-semibold text-gray-900 mb-2">"Get your meal"</h3>
                    <p class="text-sm text-gray-500">"Food is processed asynchronously by two cooks."</p>
                </div>
                <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                    <p class="text-2xl mb-3">"🥞"</p>
                    <h3 class="font-semibold text-gray-900 mb-2">"Track History"</h3>
                    <p class="text-sm text-gray-500">"View all your orders and prescripts with full audit trail."</p>
                </div>
            </div>
        </div>
    }
}

#[component]
fn LoginRoute() -> impl IntoView {
    view! { <LoginPage config=get_config()/> }
}

#[component]
fn RegisterRoute() -> impl IntoView {
    view! { <RegisterPage config=get_config()/> }
}

#[component]
fn DashboardRoute() -> impl IntoView {
    view! { <Dashboard config=get_config()/> }
}

#[component]
fn PredictRoute() -> impl IntoView {
    view! { <PredictPage config=get_config()/> }
}

#[component]
fn HistoryRoute() -> impl IntoView {
    view! { <HistoryPage config=get_config()/> }
}

#[component]
fn NotFound() -> impl IntoView {
    view! {
        <div class="max-w-xl mx-auto px-4 py-16 text-center">
            <p class="text-5xl mb-4">"404"</p>
            <p class="text-gray-500 mb-6">"Page not found."</p>
            <a href="/" class="text-blue-600 hover:underline text-sm">"← Back to Home"</a>
        </div>
    }
}
