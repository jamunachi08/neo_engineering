import frappe


def get_settings():
    """Cached accessor for Engineering Management Settings."""
    return frappe.get_cached_doc("Engineering Management Settings")


def user_can_waive():
    """Whether the current user holds the configured management waiver role."""
    settings = get_settings()
    if not settings.allow_management_waiver:
        return False
    role = settings.management_waiver_role or "Engineering Management"
    return role in frappe.get_roles()
