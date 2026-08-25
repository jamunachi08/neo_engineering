"""Workflow definitions per Section 9 of the specification.

Workflows are created programmatically and idempotently on install so that
role dependencies are guaranteed to exist first (roles are created earlier in
after_install). Each entry:

    states:      [(state, doc_status, allow_edit_role)]
    transitions: [(from_state, action, to_state, allowed_role)]

doc_status: 0 = Draft, 1 = Submitted, 2 = Cancelled.
"""

import frappe

WORKFLOWS = {
    "Project Brief": {
        "states": [
            ("Draft", 0, "Engineering Business Development"),
            ("Internal Review", 0, "Design Lead"),
            ("Client Confirmed", 0, "Project Manager"),
            ("Approved", 1, "Project Manager"),
            ("Superseded", 1, "Project Manager"),
            ("Cancelled", 2, "Project Manager"),
        ],
        "transitions": [
            ("Draft", "Submit for Review", "Internal Review", "Engineering Business Development"),
            ("Internal Review", "Confirm with Client", "Client Confirmed", "Design Lead"),
            ("Internal Review", "Return to Draft", "Draft", "Design Lead"),
            ("Client Confirmed", "Approve", "Approved", "Project Manager"),
            ("Approved", "Supersede", "Superseded", "Project Manager"),
        ],
    },
    "Design Submission": {
        "states": [
            ("Draft", 0, "Design Engineer"),
            ("Submitted for Internal Review", 0, "Design Lead"),
            ("Ready for Client", 0, "Design Lead"),
            ("Sent to Client", 1, "Project Manager"),
            ("Revision Required", 1, "Project Manager"),
            ("Approved", 1, "Project Manager"),
        ],
        "transitions": [
            ("Draft", "Submit for Internal Review", "Submitted for Internal Review", "Design Engineer"),
            ("Submitted for Internal Review", "Mark Ready for Client", "Ready for Client", "Design Lead"),
            ("Submitted for Internal Review", "Return to Draft", "Draft", "Design Lead"),
            ("Ready for Client", "Send to Client", "Sent to Client", "Project Manager"),
            ("Sent to Client", "Record Revision Required", "Revision Required", "Project Manager"),
            ("Sent to Client", "Record Client Approval", "Approved", "Project Manager"),
        ],
    },
    "Technical Review": {
        "states": [
            ("Draft", 0, "Technical Engineer"),
            ("Under Review", 0, "Technical Engineer"),
            ("Comments Issued", 0, "Technical Engineer"),
            ("Resubmitted", 0, "Technical Engineer"),
            ("Approved", 1, "Technical Manager"),
            ("Rejected", 1, "Technical Manager"),
        ],
        "transitions": [
            ("Draft", "Start Review", "Under Review", "Technical Engineer"),
            ("Under Review", "Issue Comments", "Comments Issued", "Technical Engineer"),
            ("Comments Issued", "Record Resubmission", "Resubmitted", "Technical Engineer"),
            ("Resubmitted", "Issue Comments", "Comments Issued", "Technical Engineer"),
            ("Under Review", "Approve", "Approved", "Technical Manager"),
            ("Resubmitted", "Approve", "Approved", "Technical Manager"),
            ("Under Review", "Reject", "Rejected", "Technical Manager"),
            ("Resubmitted", "Reject", "Rejected", "Technical Manager"),
        ],
    },
    "Project BOQ": {
        "states": [
            ("Draft", 0, "Quantity Surveyor"),
            ("Prepared", 0, "Quantity Surveyor"),
            ("Technical Review", 0, "Technical Manager"),
            ("Approved", 1, "Project Manager"),
            ("Superseded", 1, "Project Manager"),
        ],
        "transitions": [
            ("Draft", "Mark Prepared", "Prepared", "Quantity Surveyor"),
            ("Prepared", "Send for Technical Review", "Technical Review", "Quantity Surveyor"),
            ("Technical Review", "Return to Draft", "Draft", "Technical Manager"),
            ("Technical Review", "Approve", "Approved", "Technical Manager"),
            ("Approved", "Supersede", "Superseded", "Project Manager"),
        ],
    },
    "License Application": {
        "states": [
            ("Draft", 0, "Licensing Coordinator"),
            ("Documents Pending", 0, "Licensing Coordinator"),
            ("Ready to Submit", 0, "Licensing Coordinator"),
            ("Submitted", 1, "Licensing Coordinator"),
            ("Authority Comments", 1, "Licensing Coordinator"),
            ("Approved", 1, "Project Manager"),
            ("Rejected", 1, "Project Manager"),
            ("Expired", 1, "Project Manager"),
        ],
        "transitions": [
            ("Draft", "Start Document Collection", "Documents Pending", "Licensing Coordinator"),
            ("Documents Pending", "Mark Ready to Submit", "Ready to Submit", "Licensing Coordinator"),
            ("Ready to Submit", "Submit to Authority", "Submitted", "Licensing Coordinator"),
            ("Submitted", "Record Authority Comments", "Authority Comments", "Licensing Coordinator"),
            ("Authority Comments", "Submit to Authority", "Submitted", "Licensing Coordinator"),
            ("Submitted", "Record Approval", "Approved", "Project Manager"),
            ("Submitted", "Record Rejection", "Rejected", "Project Manager"),
            ("Approved", "Mark Expired", "Expired", "Project Manager"),
        ],
    },
    "Tender Package": {
        "states": [
            ("Draft", 0, "Contracts Specialist"),
            ("Shortlisting", 0, "Contracts Specialist"),
            ("Issued", 1, "Contracts Specialist"),
            ("Bids Received", 1, "Contracts Specialist"),
            ("Evaluation", 1, "Project Manager"),
            ("Negotiation", 1, "Project Manager"),
            ("Award Recommended", 1, "Engineering Management"),
            ("Awarded", 1, "Engineering Management"),
            ("Cancelled", 2, "Engineering Management"),
        ],
        "transitions": [
            ("Draft", "Start Shortlisting", "Shortlisting", "Contracts Specialist"),
            ("Shortlisting", "Issue", "Issued", "Contracts Specialist"),
            ("Issued", "Record Bids Received", "Bids Received", "Contracts Specialist"),
            ("Bids Received", "Start Evaluation", "Evaluation", "Project Manager"),
            ("Evaluation", "Start Negotiation", "Negotiation", "Project Manager"),
            ("Negotiation", "Start Evaluation", "Evaluation", "Project Manager"),
            ("Evaluation", "Recommend Award", "Award Recommended", "Project Manager"),
            ("Negotiation", "Recommend Award", "Award Recommended", "Project Manager"),
            ("Award Recommended", "Award", "Awarded", "Engineering Management"),
        ],
    },
    "Tender Evaluation": {
        "states": [
            ("Draft", 0, "Technical Manager"),
            ("Technical Evaluation", 0, "Technical Manager"),
            ("Commercial Evaluation", 0, "Project Manager"),
            ("Final Review", 0, "Engineering Management"),
            ("Approved", 1, "Engineering Management"),
        ],
        "transitions": [
            ("Draft", "Start Technical Evaluation", "Technical Evaluation", "Technical Manager"),
            ("Technical Evaluation", "Start Commercial Evaluation", "Commercial Evaluation", "Technical Manager"),
            ("Commercial Evaluation", "Send for Final Review", "Final Review", "Project Manager"),
            ("Final Review", "Approve", "Approved", "Engineering Management"),
            ("Final Review", "Return to Draft", "Draft", "Engineering Management"),
        ],
    },
    "Site Inspection": {
        "states": [
            ("Draft", 0, "Site Engineer"),
            ("Inspected", 0, "Site Engineer"),
            ("Observations Open", 0, "Site Engineer"),
            ("Rectification Submitted", 0, "Site Engineer"),
            ("Verified", 0, "Supervision Manager"),
            ("Closed", 1, "Supervision Manager"),
        ],
        "transitions": [
            ("Draft", "Record Inspection", "Inspected", "Site Engineer"),
            ("Inspected", "Open Observations", "Observations Open", "Site Engineer"),
            ("Observations Open", "Submit Rectification", "Rectification Submitted", "Site Engineer"),
            ("Rectification Submitted", "Verify", "Verified", "Supervision Manager"),
            ("Rectification Submitted", "Reopen Observations", "Observations Open", "Supervision Manager"),
            ("Inspected", "Close", "Closed", "Supervision Manager"),
            ("Verified", "Close", "Closed", "Supervision Manager"),
        ],
    },
    "Contractor Progress Certificate": {
        "states": [
            ("Draft", 0, "Site Engineer"),
            ("Engineer Review", 0, "Site Engineer"),
            ("PM Review", 0, "Project Manager"),
            ("Approved", 1, "Engineering Finance Reviewer"),
            ("Rejected", 1, "Project Manager"),
        ],
        "transitions": [
            ("Draft", "Submit for Engineer Review", "Engineer Review", "Site Engineer"),
            ("Engineer Review", "Send to PM Review", "PM Review", "Site Engineer"),
            ("PM Review", "Return to Draft", "Draft", "Project Manager"),
            ("PM Review", "Approve", "Approved", "Engineering Finance Reviewer"),
            ("PM Review", "Reject", "Rejected", "Project Manager"),
        ],
    },
    "Project Handover": {
        "states": [
            ("Draft", 0, "Supervision Manager"),
            ("Snagging", 0, "Supervision Manager"),
            ("Ready for Handover", 0, "Project Manager"),
            ("Customer Review", 0, "Project Manager"),
            ("Revision Required", 0, "Project Manager"),
            ("Accepted", 1, "Project Manager"),
        ],
        "transitions": [
            ("Draft", "Start Snagging", "Snagging", "Supervision Manager"),
            ("Snagging", "Mark Ready for Handover", "Ready for Handover", "Supervision Manager"),
            ("Ready for Handover", "Send for Customer Review", "Customer Review", "Project Manager"),
            ("Customer Review", "Record Revision Required", "Revision Required", "Project Manager"),
            ("Revision Required", "Send for Customer Review", "Customer Review", "Project Manager"),
            ("Customer Review", "Accept", "Accepted", "Project Manager"),
        ],
    },
    "Project Closure": {
        "states": [
            ("Draft", 0, "Project Manager"),
            ("Financial Clearance", 0, "Engineering Finance Reviewer"),
            ("Technical Clearance", 0, "Project Manager"),
            ("Management Approval", 0, "Engineering Management"),
            ("Closed", 1, "Engineering Management"),
        ],
        "transitions": [
            ("Draft", "Start Financial Clearance", "Financial Clearance", "Project Manager"),
            ("Financial Clearance", "Start Technical Clearance", "Technical Clearance", "Engineering Finance Reviewer"),
            ("Technical Clearance", "Send for Management Approval", "Management Approval", "Project Manager"),
            ("Management Approval", "Return to Draft", "Draft", "Engineering Management"),
            ("Management Approval", "Close", "Closed", "Engineering Management"),
        ],
    },
}


def create_workflows():
    for doctype, spec in WORKFLOWS.items():
        _ensure_states_and_actions(spec)
        _create_or_update_workflow(doctype, spec)


def _ensure_states_and_actions(spec):
    for state, _doc_status, _role in spec["states"]:
        if not frappe.db.exists("Workflow State", state):
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": state,
            }).insert(ignore_permissions=True)
    for _from, action, _to, _role in spec["transitions"]:
        if not frappe.db.exists("Workflow Action Master", action):
            frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action,
            }).insert(ignore_permissions=True)


def _create_or_update_workflow(doctype, spec):
    workflow_name = f"{doctype} Workflow"
    doc = (frappe.get_doc("Workflow", workflow_name)
           if frappe.db.exists("Workflow", workflow_name)
           else frappe.new_doc("Workflow"))
    doc.update({
        "workflow_name": workflow_name,
        "document_type": doctype,
        "workflow_state_field": "workflow_state",
        "is_active": 1,
        "send_email_alert": 0,
    })
    doc.set("states", [])
    doc.set("transitions", [])
    for state, doc_status, role in spec["states"]:
        doc.append("states", {
            "state": state,
            "doc_status": str(doc_status),
            "allow_edit": role,
        })
    for from_state, action, to_state, role in spec["transitions"]:
        doc.append("transitions", {
            "state": from_state,
            "action": action,
            "next_state": to_state,
            "allowed": role,
            "allow_self_approval": 1,
        })
    doc.flags.ignore_permissions = True
    doc.save()
