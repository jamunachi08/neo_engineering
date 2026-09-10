"""Post-install setup for neo_engineering.

Runs on `bench --site <site> install-app neo_engineering` (after_install
hook) and is safe to re-run: every step is idempotent (Sections 17 / 17.1).
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from neo_engineering.setup.custom_fields import get_custom_fields
from neo_engineering.setup.workflows import create_workflows

ROLES = [
    "Engineering Business Development",
    "Design Engineer",
    "Design Lead",
    "Technical Engineer",
    "Technical Manager",
    "Quantity Surveyor",
    "Licensing Coordinator",
    "Project Manager",
    "Contracts Specialist",
    "Site Engineer",
    "Supervision Manager",
    "Engineering Finance Reviewer",
    "Engineering Management",
    "Engineering App Administrator",
]


def after_install():
    create_roles()
    apply_custom_fields()
    create_workflows()
    seed_settings()
    frappe.db.commit()


def after_migrate():
    """Keep configuration reproducible on every update (Section 17)."""
    create_roles()
    apply_custom_fields()
    create_workflows()


def create_roles():
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role,
                "desk_access": 1,
            }).insert(ignore_permissions=True)


def apply_custom_fields():
    # create_custom_fields updates existing fieldnames in place and never
    # duplicates or fails on an existing field (Section 17.1).
    create_custom_fields(get_custom_fields(), ignore_validate=True)


def seed_settings():
    settings = frappe.get_single("Engineering Management Settings")
    changed = False
    defaults = {
        "default_tender_technical_weight": 60,
        "default_tender_commercial_weight": 40,
        "default_review_due_days": 7,
        "default_inspection_rectification_days": 7,
        "warranty_reminder_days": 14,
        "allow_management_waiver": 1,
        "require_project_closure_before_completion": 1,
        "auto_update_project_kpis": 1,
    }
    for field, value in defaults.items():
        if not settings.get(field):
            settings.set(field, value)
            changed = True
    if not settings.management_waiver_role and frappe.db.exists(
            "Role", "Engineering Management"):
        settings.management_waiver_role = "Engineering Management"
        changed = True
    if changed:
        settings.flags.ignore_permissions = True
        settings.save()
