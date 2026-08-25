app_name = "neo_engineering"
app_title = "NeoEngineering"
app_publisher = "Alwathaeq Engineering Consultancy Office"
app_description = (
    "Single consolidated engineering business app for ERPNext v15: project "
    "brief, design control, technical review, BOQ, licensing, tendering, "
    "supervision, progress certification, handover, closure and warranty."
)
app_email = "it@neoengineering.example"
app_license = "Proprietary"
required_apps = ["erpnext"]

# ---------------------------------------------------------------------------
# Installation / migration (Section 17)
# ---------------------------------------------------------------------------
after_install = "neo_engineering.setup.install.after_install"
after_migrate = "neo_engineering.setup.install.after_migrate"

# ---------------------------------------------------------------------------
# Fixtures (Section 17.1) — export only app-owned configuration, filtered so
# unrelated customer customizations are never captured.
# ---------------------------------------------------------------------------
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [["fieldname", "like", "custom_%"], ["module", "in", [None, "Engineering Management"]]],
    },
    {
        "doctype": "Property Setter",
        "filters": [["module", "=", "Engineering Management"]],
    },
]

# ---------------------------------------------------------------------------
# Document events (Sections 11, 14, 16.3) — server-side rules only where a
# standard DocType must be controlled; custom DocType rules live in their own
# controllers.
# ---------------------------------------------------------------------------
doc_events = {
    "Project": {
        "validate": "neo_engineering.api.project.validate_project",
        "on_update": "neo_engineering.api.project.update_project_kpis",
    },
    "Purchase Invoice": {
        "validate": "neo_engineering.api.progress.validate_progress_invoice",
    },
    "Issue": {
        "validate": "neo_engineering.api.issue.validate_issue",
    },
}

# ---------------------------------------------------------------------------
# Scheduled jobs (Section 12) — overdue and expiry notifications
# ---------------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "neo_engineering.api.notifications.send_daily_alerts",
    ],
}
