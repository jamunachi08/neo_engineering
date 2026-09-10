"""NeoEngineering demo data.

Creates bilingual masters and four demo projects frozen at different
lifecycle stages, with every supporting record (briefs, documents,
submissions, reviews, BOQs, licenses, tenders, inspections, certificates,
handover, closure, warranty) built to satisfy the app's own business rules.

Run explicitly (never automatic):

    bench --site <site> execute neo_engineering.setup.demo.make_demo_data

Idempotent: existing records (matched by name/title) are not duplicated.
Remove everything with:

    bench --site <site> execute neo_engineering.setup.demo.delete_demo_data
"""

import frappe
from frappe.utils import add_days, add_months, nowdate

DEMO_TAG = "NEO-DEMO"

CUSTOMERS = [
    "Al Manar Real Estate | المنار العقارية",
    "Qimam Development | قمم للتطوير",
]

SUPPLIERS = [  # (name, specialty, prequal_status)
    ("Bunyan Contracting | بنيان للمقاولات", "General Building | مباني عامة", "Approved"),
    ("Rawafid Builders | روافد للإنشاءات", "Structural | إنشائي", "Approved"),
    ("Tamkeen MEP | تمكين للكهروميكانيك", "MEP | كهروميكانيك", "Approved"),
]

PROJECT_TYPES = ["Residential | سكني", "Commercial | تجاري", "Villas | فلل"]

PROJECTS = [
    # (project_name, customer_idx, type_idx, service_type, stage, location)
    ("Villa Compound Al Yasmin | مجمع فلل الياسمين", 0, 2,
     "Design + Supervision", "Design", "Riyadh – Al Yasmin | الرياض – الياسمين"),
    ("Qimam Office Tower | برج قمم المكتبي", 1, 1,
     "Design + Supervision + Execution", "Tendering", "Riyadh – KAFD | الرياض – المركز المالي"),
    ("Al Manar Retail Strip | مركز المنار التجاري", 0, 1,
     "Design + Supervision + Execution", "Execution", "Riyadh – Al Malqa | الرياض – الملقا"),
    ("Private Villa 42 | فيلا خاصة ٤٢", 1, 2,
     "Design + Supervision", "Closed", "Riyadh – Hittin | الرياض – حطين"),
]


def make_demo_data():
    frappe.flags.in_import = True  # bypass workflow transition checks for seeding
    try:
        company = _default_company()
        _masters()
        customers = [_customer(n) for n in CUSTOMERS]
        suppliers = [_supplier(*s) for s in SUPPLIERS]
        for idx, spec in enumerate(PROJECTS):
            _project_with_records(idx, spec, customers, suppliers, company)
        frappe.db.commit()
        print("NeoEngineering demo data created ✔")
    finally:
        frappe.flags.in_import = False


# --------------------------------------------------------------------- masters
def _default_company():
    company = frappe.defaults.get_global_default("company") \
        or frappe.db.get_value("Company", {}, "name")
    if not company:
        frappe.throw("No Company found. Create your company first, then re-run.")
    return company


def _masters():
    for pt in PROJECT_TYPES:
        if not frappe.db.exists("Project Type", pt):
            frappe.get_doc({"doctype": "Project Type", "project_type": pt}
                           ).insert(ignore_permissions=True)
    for uom in ["Lump Sum | مقطوعية", "Running Meter | متر طولي"]:
        if not frappe.db.exists("UOM", uom):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom}
                           ).insert(ignore_permissions=True)


def _customer(name):
    if frappe.db.exists("Customer", {"customer_name": name}):
        return frappe.db.get_value("Customer", {"customer_name": name}, "name")
    doc = frappe.get_doc({
        "doctype": "Customer", "customer_name": name,
        "customer_group": frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
            or "All Customer Groups",
        "territory": "All Territories", "customer_type": "Company",
    }).insert(ignore_permissions=True)
    return doc.name


def _supplier(name, specialty, prequal):
    if frappe.db.exists("Supplier", {"supplier_name": name}):
        return frappe.db.get_value("Supplier", {"supplier_name": name}, "name")
    doc = frappe.get_doc({
        "doctype": "Supplier", "supplier_name": name,
        "supplier_group": frappe.db.get_value("Supplier Group", {"is_group": 0}, "name")
            or "All Supplier Groups",
        "supplier_type": "Company",
        "custom_supplier_type": "Contractor",
        "custom_contractor_specialty": specialty,
        "custom_prequalification_status": prequal,
        "custom_prequalification_expiry": add_months(nowdate(), 18),
    }).insert(ignore_permissions=True)
    return doc.name


# ------------------------------------------------------------------- projects
def _project_with_records(idx, spec, customers, suppliers, company):
    project_name, cidx, tidx, service_type, stage, location = spec
    if frappe.db.exists("Project", {"project_name": project_name}):
        return
    customer = customers[cidx]

    brief = _brief(project_name, customer, location)
    project = frappe.get_doc({
        "doctype": "Project", "project_name": project_name,
        "company": company, "customer": customer,
        "project_type": PROJECT_TYPES[tidx],
        "status": "Open", "notes": DEMO_TAG,
        "custom_project_brief": brief,
        "custom_service_type": service_type,
        "custom_project_stage": stage if stage != "Closed" else "Handover",
        "custom_design_origin": "Internal",
        "custom_project_location": location,
        "custom_project_manager": "Administrator",
        "custom_design_lead": "Administrator",
        "custom_technical_manager": "Administrator",
        "custom_supervision_manager": "Administrator",
        "custom_contract_no": f"CNT-{2026}-{100 + idx}",
        "custom_contract_date": add_months(nowdate(), -6),
        "custom_contract_value": 2_500_000 * (idx + 1),
    }).insert(ignore_permissions=True)
    pname = project.name

    _site_visit(pname)
    docs = _design_pack(pname, customer, stage)
    if stage == "Design":
        return  # P1 stops here: documents drafted, submission with the client

    review = _technical_review(pname, docs["submission"])
    boq = _boq(pname, review)
    _license(pname, customer, approved=True)
    tender = _tender(pname, boq, suppliers, awarded=(stage in ("Execution", "Closed")))
    if stage == "Tendering":
        return  # P2 stops mid-tender

    _site_inspection(pname, suppliers[0])
    if stage == "Execution":
        _progress_certificate(pname, suppliers[0], 0, 20, months_ago=2)
        _progress_certificate(pname, suppliers[0], 20, 25, months_ago=1)
        latest = _progress_certificate(pname, suppliers[0], 45, 20, months_ago=0)
        frappe.db.set_value("Project", pname, "custom_site_progress_pct", 65,
            update_modified=False)
        _financial_leg(pname, suppliers[0], latest)
        return  # P3 executing
    _progress_certificate(pname, suppliers[0], 75, 25, months_ago=1)

    handover = _handover(pname, customer)
    _closure(pname, handover)  # on_submit flips Project to Closed / Completed
    _warranty_issue(pname, customer, suppliers[0])


def _site_visit(pname, purpose="Pre-Design"):
    if frappe.db.exists("Engineering Site Visit", {"project": pname, "purpose": purpose}):
        return
    doc = frappe.get_doc({
        "doctype": "Engineering Site Visit", "project": pname,
        "visit_date": add_days(nowdate(), -35), "purpose": purpose,
        "attendees": "PM, Design Lead, Owner rep | مدير المشروع، رئيس التصميم، ممثل المالك",
        "observations": "Site levelled, power available at boundary | "
                        "الموقع مستوٍ والكهرباء متوفرة عند الحد",
        "followup_actions": "Request soil report | طلب تقرير التربة",
    }).insert(ignore_permissions=True)
    doc.submit()
    return doc.name


def _brief(project_name, customer, location):
    title_key = {"project_location": location}
    existing = frappe.db.get_value("Project Brief",
        {"customer": customer, "project_location": location}, "name")
    if existing:
        return existing
    doc = frappe.get_doc({
        "doctype": "Project Brief", "customer": customer,
        "project_location": location,
        "estimated_budget": 3_000_000,
        "objectives": f"{DEMO_TAG}: Owner requirements captured during intake. | "
                      "متطلبات المالك الموثقة أثناء مرحلة الاستقبال.",
        "services": [{"service_type": "Design + Supervision",
                      "discipline": "Architectural", "included": 1,
                      "description": "Full design & supervision | تصميم وإشراف كامل"}],
        "documents": [{"document_name": "Title deed | صك الملكية",
                       "is_mandatory": 1, "received": 1},
                      {"document_name": "Survey report | تقرير الرفع المساحي",
                       "is_mandatory": 1, "received": 1}],
        "workflow_state": "Approved",
    }).insert(ignore_permissions=True)
    doc.submit()
    return doc.name


def _design_pack(pname, customer, stage):
    """Demonstrates the revision loop: Rev A submitted → client requires
    revision → Rev B issued (A superseded) → resubmitted → approved/sent."""
    ed = frappe.get_doc({
        "doctype": "Engineering Document", "project": pname,
        "document_no": f"{pname}-ARC-001", "title": "Architectural Layout | المخطط المعماري",
        "discipline": "Architectural", "origin": "Internal",
        "document_status": "For Client Review",
        "revisions": [{"revision": "A", "revision_date": add_days(nowdate(), -40),
                       "is_current": 1, "reason": "First issue | الإصدار الأول"}],
    }).insert(ignore_permissions=True)

    sub1 = frappe.get_doc({
        "doctype": "Design Submission", "project": pname, "customer": customer,
        "submission_date": add_days(nowdate(), -30), "purpose": "For Approval",
        "documents": [{"engineering_document": ed.name, "revision": "A",
                       "approval_status": "Revision Required"}],
        "workflow_state": "Revision Required",
        "client_response": "Revision Required",
        "client_comments": "Enlarge majlis, revise entrance | "
                           "توسيع المجلس وتعديل المدخل",
    }).insert(ignore_permissions=True)
    sub1.submit()

    # Rev B supersedes A (controller enforces single Current)
    ed.append("revisions", {"revision": "B",
        "revision_date": add_days(nowdate(), -20), "is_current": 1,
        "reason": "Client comments | ملاحظات العميل"})
    ed.revisions[0].is_current = 0
    ed.revisions[0].superseded = 1
    if stage != "Design":
        ed.document_status = "Approved"
    ed.save(ignore_permissions=True)

    sub2 = frappe.get_doc({
        "doctype": "Design Submission", "project": pname, "customer": customer,
        "submission_date": add_days(nowdate(), -15), "purpose": "For Approval",
        "documents": [{"engineering_document": ed.name, "revision": "B",
                       "approval_status": "Pending" if stage == "Design" else "Approved"}],
        "workflow_state": "Sent to Client" if stage == "Design" else "Approved",
        "client_response": None if stage == "Design" else "Approved",
    }).insert(ignore_permissions=True)
    sub2.submit()
    return {"document": ed.name, "submission": sub2.name}


def _technical_review(pname, submission):
    doc = frappe.get_doc({
        "doctype": "Technical Review", "project": pname,
        "design_submission": submission,
        "review_date": add_days(nowdate(), -12),
        "result": "Approved with Comments",
        "comments": [{
            "comment_no": "TR-01", "discipline": "Structural",
            "comment": "Confirm slab thickness at grid C | تأكيد سماكة البلاطة عند المحور C",
            "severity": "Medium", "is_mandatory": 1, "status": "Closed",
            "response": "Updated in Rev B | تم التحديث في المراجعة B",
        }],
        "workflow_state": "Approved",
    }).insert(ignore_permissions=True)
    doc.submit()
    return doc.name


def _boq(pname, review):
    doc = frappe.get_doc({
        "doctype": "Project BOQ", "project": pname, "technical_review": review,
        "boq_date": add_days(nowdate(), -10),
        "items": [
            {"description": "Reinforced concrete works | أعمال الخرسانة المسلحة",
             "uom": "Cubic Meter" if frappe.db.exists("UOM", "Cubic Meter") else "Nos",
             "qty": 850, "rate": 1450},
            {"description": "Blockwork & plaster | أعمال البلوك واللياسة",
             "uom": "Square Meter" if frappe.db.exists("UOM", "Square Meter") else "Nos",
             "qty": 5200, "rate": 95},
            {"description": "Site mobilization | تجهيز الموقع",
             "uom": "Lump Sum | مقطوعية", "qty": 1, "rate": 120000},
        ],
        "workflow_state": "Approved",
    }).insert(ignore_permissions=True)
    doc.submit()
    return doc.name


def _license(pname, customer, approved):
    doc = frappe.get_doc({
        "doctype": "License Application", "project": pname, "customer": customer,
        "authority": "Riyadh Municipality (Balady) | أمانة الرياض (بلدي)",
        "license_type": "Building Permit | رخصة بناء",
        "documents": [{"document_name": "Approved drawings | المخططات المعتمدة",
                       "is_mandatory": 1, "received": 1, "validated": 1},
                      {"document_name": "Owner ID | هوية المالك",
                       "is_mandatory": 1, "received": 1, "validated": 1}],
        "submission_date": add_days(nowdate(), -8),
        "approval_date": add_days(nowdate(), -3) if approved else None,
        "license_no": "BLD-2026-4471" if approved else None,
        "workflow_state": "Approved" if approved else "Submitted",
    }).insert(ignore_permissions=True)
    doc.submit()
    return doc.name


def _tender(pname, boq, suppliers, awarded):
    doc = frappe.get_doc({
        "doctype": "Tender Package", "project": pname, "project_boq": boq,
        "tender_round": 1, "issue_date": add_days(nowdate(), -6),
        "bid_deadline": add_days(nowdate(), 8),
        "description": f"{DEMO_TAG}: Main works package | حزمة الأعمال الرئيسية",
        "contractors": [{"supplier": s, "invited": 1,
                         "evaluation_status": "Qualified" if awarded else "Pending"}
                        for s in suppliers],
        "workflow_state": "Awarded" if awarded else "Issued",
        "awarded_supplier": suppliers[0] if awarded else None,
    }).insert(ignore_permissions=True)
    doc.submit()
    if awarded:
        ev = frappe.get_doc({
            "doctype": "Tender Evaluation", "tender_package": doc.name,
            "technical_weight": 60, "commercial_weight": 40,
            "lines": [{"supplier": s, "supplier_quotation": None,
                       "technical_score": 80 - i * 5, "commercial_score": 75 + i * 3}
                      for i, s in enumerate(suppliers)],
            "recommended_supplier": suppliers[0],
            "recommendation_notes": "Best weighted score | أفضل نتيجة موزونة",
            "workflow_state": "Approved",
        })
        # supplier_quotation is reqd in the child; demo uses direct scoring
        for line in ev.lines:
            line.flags.ignore_mandatory = True
        ev.flags.ignore_mandatory = True
        ev.insert(ignore_permissions=True)
        ev.submit()
    return doc.name


def _site_inspection(pname, supplier):
    closed = frappe.get_doc({
        "doctype": "Site Inspection", "project": pname, "supplier": supplier,
        "inspection_date": add_days(nowdate(), -9),
        "inspection_type": "Structural | إنشائي",
        "result": "Passed with Observations",
        "observations": [{
            "observation": "Rebar cover below spec at column C3 | الغطاء الخرساني أقل من المواصفة عند العمود C3",
            "severity": "High", "is_mandatory": 1, "status": "Verified",
            "supplier": supplier, "due_date": add_days(nowdate(), -5),
        }],
        "workflow_state": "Closed",
    }).insert(ignore_permissions=True)
    closed.submit()

    # a live one with an OPEN observation — lights the dashboard card and
    # demonstrates BR-010 (this record cannot be closed until verified)
    frappe.get_doc({
        "doctype": "Site Inspection", "project": pname, "supplier": supplier,
        "inspection_date": add_days(nowdate(), -1),
        "inspection_type": "MEP | كهروميكانيك",
        "result": "Passed with Observations",
        "observations": [{
            "observation": "Duct insulation missing in corridor | عزل الدكت مفقود في الممر",
            "severity": "High", "is_mandatory": 1, "status": "Open",
            "supplier": supplier, "due_date": add_days(nowdate(), 5),
        }],
        "workflow_state": "Observations Open",
    }).insert(ignore_permissions=True)
    return closed.name


def _progress_certificate(pname, supplier, prev_pct, cur_pct, months_ago=0):
    period_to = add_months(nowdate(), -months_ago)
    doc = frappe.get_doc({
        "doctype": "Contractor Progress Certificate", "project": pname,
        "supplier": supplier,
        "period_from": add_months(period_to, -1), "period_to": period_to,
        "retention_pct": 10,
        "lines": [
            {"description": "Concrete works | أعمال الخرسانة",
             "previous_pct": prev_pct, "current_pct": cur_pct,
             "certified_value": 450000 * cur_pct / 25},
            {"description": "Blockwork | أعمال البلوك",
             "previous_pct": prev_pct, "current_pct": cur_pct,
             "certified_value": 180000 * cur_pct / 25},
        ],
        "workflow_state": "Approved",
    }).insert(ignore_permissions=True)
    doc.submit()
    return doc.name


def _handover(pname, customer):
    doc = frappe.get_doc({
        "doctype": "Project Handover", "project": pname, "customer": customer,
        "handover_date": add_days(nowdate(), -2), "customer_accepted": 1,
        "acceptance_date": add_days(nowdate(), -2),
        "snagging_summary": "All snags rectified | تمت معالجة جميع الملاحظات",
        "documents": [{"document_name": "As-built drawings | المخططات كما نُفذت",
                       "required": 1, "delivered": 1, "accepted": 1},
                      {"document_name": "Warranty certificates | شهادات الضمان",
                       "required": 1, "delivered": 1, "accepted": 1}],
        "workflow_state": "Accepted",
    }).insert(ignore_permissions=True)
    doc.submit()
    return doc.name


def _closure(pname, handover):
    doc = frappe.get_doc({
        "doctype": "Project Closure", "project": pname, "project_handover": handover,
        "closure_date": nowdate(), "financial_cleared": 1, "technical_cleared": 1,
        "checklist": [
            {"category": "Financial", "requirement": "Final account settled | تسوية الحساب الختامي",
             "is_mandatory": 1, "completed": 1, "completion_date": nowdate()},
            {"category": "Technical", "requirement": "As-builts archived | أرشفة المخططات النهائية",
             "is_mandatory": 1, "completed": 1, "completion_date": nowdate()},
        ],
        "remarks": f"{DEMO_TAG} closure",
        "workflow_state": "Closed",
    }).insert(ignore_permissions=True)
    doc.submit()  # sets Project → Closed / Completed (BR-015 path)
    return doc.name


def _warranty_issue(pname, customer, supplier):
    if frappe.db.exists("Issue", {"custom_project": pname}):
        return
    frappe.get_doc({
        "doctype": "Issue",
        "subject": "AC condensate leak – Majlis | تسريب تكييف – المجلس",
        "customer": customer, "status": "Open",
        "custom_project": pname, "custom_issue_category": "Warranty",
        "custom_responsible_supplier": supplier,
        "custom_warranty_due_date": add_days(nowdate(), 20),
        "custom_severity": "Medium",
    }).insert(ignore_permissions=True)


# --------------------------------------------------------------------- delete
def delete_demo_data():
    """Remove demo projects and their child records (matched by DEMO names)."""
    frappe.flags.in_import = True
    try:
        names = [p[0] for p in PROJECTS]
        projects = frappe.get_all("Project",
            filters={"project_name": ("in", names)}, pluck="name")
        child_doctypes = ["Purchase Invoice", "Purchase Order",
            "Issue", "Project Closure", "Project Handover",
            "Contractor Progress Certificate", "Site Inspection",
            "Tender Evaluation", "Tender Package", "License Application",
            "Project BOQ", "Technical Review", "Design Submission",
            "Engineering Document", "Engineering Site Visit"]
        for p in projects:
            for dt in child_doctypes:
                field = "custom_project" if dt == "Issue" else \
                    ("tender_package" if dt == "Tender Evaluation" else "project")
                if dt == "Tender Evaluation":
                    tps = frappe.get_all("Tender Package", {"project": p}, pluck="name")
                    rows = frappe.get_all(dt, {"tender_package": ("in", tps or [""])}, pluck="name")
                else:
                    rows = frappe.get_all(dt, {field: p}, pluck="name")
                for name in rows:
                    doc = frappe.get_doc(dt, name)
                    if doc.docstatus == 1:
                        doc.cancel()
                    frappe.delete_doc(dt, name, force=True, ignore_permissions=True)
            frappe.delete_doc("Project", p, force=True, ignore_permissions=True)
        if frappe.db.exists("Item", "ENG-WORKS-DEMO"):
            frappe.delete_doc("Item", "ENG-WORKS-DEMO", force=True,
                ignore_permissions=True)
        frappe.db.commit()
        print(f"Removed {len(projects)} demo project(s) and children ✔")
    finally:
        frappe.flags.in_import = False


# ------------------------------------------------------------ financial leg
DEMO_ITEM = "ENG-WORKS-DEMO"


def _demo_item(company):
    if frappe.db.exists("Item", DEMO_ITEM):
        return DEMO_ITEM
    frappe.get_doc({
        "doctype": "Item", "item_code": DEMO_ITEM,
        "item_name": "Engineering Works | أعمال هندسية",
        "item_group": frappe.db.get_value("Item Group", {"is_group": 0}, "name")
            or "All Item Groups",
        "stock_uom": "Nos", "is_stock_item": 0, "is_purchase_item": 1,
    }).insert(ignore_permissions=True)
    return DEMO_ITEM


def _financial_leg(pname, supplier, certificate):
    """Purchase Order for the award, then a Purchase Invoice validated live
    against the certificate (BR-012). Wrapped defensively: if the site's
    accounts aren't configured for direct PI creation, the demo continues
    and logs guidance instead of failing."""
    try:
        company = _default_company()
        item = _demo_item(company)
        if not frappe.db.exists("Purchase Order",
                {"project": pname, "supplier": supplier, "docstatus": ("<", 2)}):
            tender = frappe.db.get_value("Tender Package", {"project": pname}, "name")
            po = frappe.get_doc({
                "doctype": "Purchase Order", "supplier": supplier,
                "company": company, "project": pname,
                "custom_tender_package": tender,
                "custom_contract_type": "Main Contract",
                "schedule_date": add_days(nowdate(), 30),
                "items": [{"item_code": item, "qty": 1, "rate": 1200000,
                           "schedule_date": add_days(nowdate(), 30),
                           "project": pname}],
            })
            po.insert(ignore_permissions=True)
            po.submit()
        net = frappe.db.get_value("Contractor Progress Certificate",
            certificate, "net_certified_amount")
        pi = frappe.get_doc({
            "doctype": "Purchase Invoice", "supplier": supplier,
            "company": company, "project": pname,
            "custom_progress_certificate": certificate,
            "items": [{"item_code": item, "qty": 1,
                       "rate": min(300000, net or 300000), "project": pname}],
        })
        pi.insert(ignore_permissions=True)
        pi.submit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "NEO-DEMO financial leg")
        print("  ! Financial leg skipped (accounts not configured for direct "
              "PI creation) — see Error Log. All engineering records created.")
