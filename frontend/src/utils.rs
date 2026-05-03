use crate::clients::model::models::TaskStatus;

pub fn fmt_datetime(s: &str) -> String {
    s.chars().take(19).collect()
}

pub fn fmt_date(s: &str) -> String {
    s.chars().take(10).collect()
}

pub fn status_badge_class(status: &TaskStatus) -> &'static str {
    match status {
        TaskStatus::Completed => "text-green-700 bg-green-50 border border-green-200",
        TaskStatus::Failed    => "text-red-700 bg-red-50 border border-red-200",
        _                     => "text-yellow-700 bg-yellow-50 border border-yellow-200",
    }
}

pub fn status_label(status: &TaskStatus) -> &'static str {
    match status {
        TaskStatus::Completed  => "Completed",
        TaskStatus::Failed     => "Failed",
        TaskStatus::Processing => "Processing…",
        _                      => "Pending…",
    }
}
