// NeoEngineering — Engineering Project Process Flow Chart
// Styled after the office's classic flow chart: five department lanes with
// icons, filled step boxes, decision diamonds with Yes/No exits, revision
// note boxes, and a "Key Outputs at Each Stage" strip — every step and
// output clickable, with BR rule tooltips.

frappe.pages["engineering-process-map"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Engineering Process Map"),
		single_column: true,
	});
	page.set_secondary_action(__("Refresh"), () => render(page));
	render(page);
};

const BR_RULES = {
	"BR-001": "An active project must have Service Type, Project Stage, Project Manager and Location filled.",
	"BR-002": "Supervision Only projects must state the design origin: External, or Internal with a linked Project Brief.",
	"BR-003": "A Design Submission cannot be saved or submitted without at least one document revision in it.",
	"BR-004": "Only one revision of a document is Current, and only that revision may be submitted; older revisions are superseded automatically.",
	"BR-005": "A Technical Review cannot be approved while mandatory comments are still Open.",
	"BR-006": "A BOQ needs at least one item with a valid UOM and a quantity greater than zero.",
	"BR-007": "A tender cannot be issued without an approved Project BOQ (management may waive with a written reason).",
	"BR-008": "Only prequalified contractors with unexpired status may be shortlisted, when prequalification is enabled in Settings.",
	"BR-009": "A tender cannot be awarded without an approved Tender Evaluation (waivable by management with reason).",
	"BR-010": "A Site Inspection cannot close while mandatory, High or Critical observations are unverified.",
	"BR-011": "Cumulative certified progress per line cannot exceed 100% unless the line is flagged as a variation.",
	"BR-012": "A Purchase Invoice cannot exceed the certificate's certified amount minus what was already invoiced against it.",
	"BR-013": "A Handover cannot be accepted while mandatory documents are undelivered, unless management waives with reason.",
	"BR-014": "A Closure cannot be approved with incomplete mandatory checklist items or missing Financial/Technical clearance.",
	"BR-015": "A Project may only become Completed after an approved Project Closure (Design Only: an accepted Handover suffices).",
	"BR-016": "A warranty/defect Issue cannot be closed without resolution details and a named internal verifier.",
};

const LANES = [
	{ key: 1, icon: "👤", label: "Client", tint: "#dbeafe", strong: "#eff6ff", border: "#1e4e8c", text: "#1e3a5f" },
	{ key: 2, icon: "📐", label: "Architectural Design Department", tint: "#dcfce7", strong: "#f0fdf4", border: "#2e7d4f", text: "#14532d" },
	{ key: 3, icon: "⚙️", label: "Technical Department", tint: "#fef3c7", strong: "#fffbeb", border: "#b45309", text: "#78350f" },
	{ key: 4, icon: "👷", label: "Supervision / Construction Department", tint: "#ede9fe", strong: "#f5f3ff", border: "#6d28d9", text: "#4c1d95" },
	{ key: 5, icon: "📋", label: "Project Management", tint: "#fee2e2", strong: "#fef2f2", border: "#b91c1c", text: "#7f1d1d" },
];

// kind: start | end | step | decision | note
const NODES = [
	{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
	{ id: "s1", lane: 1, row: 2, kind: "step", num: 1, title: "Client Inquiry and Meeting",
		desc: "Discuss needs, budget and project type",
		links: [["Lead", "Lead"], ["Opportunity", "Opportunity"]] },
	{ id: "s2", lane: 2, row: 3, kind: "step", num: 2, title: "Prepare Technical & Financial Proposal",
		desc: "Service type decides the project path",
		links: [["Quotation", "Quotation"], ["Project Brief", "Project Brief"]] },
	{ id: "d1", lane: 1, row: 4, kind: "decision", title: "Client\nApproves?" },
	{ id: "n1", lane: 1, row: 5, kind: "note", title: "Discuss Revisions / Alternatives" },
	{ id: "s3", lane: 2, row: 6, kind: "step", num: 3, title: "Sign Contract and Project Kick-off",
		desc: "Create the Project, fill Engineering Control tab (BR-001)",
		links: [["Project", "Project"]] },
	{ id: "s4", lane: 2, row: 7, kind: "step", num: 4, title: "Site Visit and Data Collection",
		desc: "Observations, attendees, follow-ups",
		links: [["Site Visit", "Engineering Site Visit"]] },
	{ id: "s5", lane: 2, row: 8, kind: "step", num: 5, title: "Prepare Design",
		desc: "Concept & detailed drawings, revisions Rev A, B… (BR-004)",
		links: [["Engineering Document", "Engineering Document"]] },
	{ id: "s6", lane: 2, row: 9, kind: "step", num: 6, title: "Submit Design for Client Review",
		desc: "Needs ≥1 current revision (BR-003)",
		links: [["Design Submission", "Design Submission"]] },
	{ id: "d2", lane: 1, row: 10, kind: "decision", title: "Client\nApproval?" },
	{ id: "n2", lane: 1, row: 11, kind: "note", title: "Revise Design (as per comments)" },
	{ id: "s7", lane: 2, row: 12, kind: "step", num: 7, title: "Finalize Drawings and Obtain Permits",
		desc: "Authority licensing runs here",
		links: [["License Application", "License Application"]] },
	{ id: "s8", lane: 3, row: 13, kind: "step", num: 8, title: "Technical Review",
		desc: "Check drawings, calculate quantities, ensure compliance (BR-005)",
		links: [["Technical Review", "Technical Review"]] },
	{ id: "d3", lane: 3, row: 14, kind: "decision", title: "Any\nRemarks?" },
	{ id: "n3", lane: 2, row: 15, kind: "note", title: "Send Back for Corrections" },
	{ id: "s9", lane: 3, row: 16, kind: "step", num: 9, title: "Approve Drawings and Bill of Quantities (BOQ)",
		desc: "Baseline quantities and rates (BR-006)",
		links: [["Project BOQ", "Project BOQ"]] },
	{ id: "s10", lane: 4, row: 17, kind: "step", num: 10, title: "Tendering / Direct Assignment",
		desc: "Evaluate contractors and award (BR-007, BR-008, BR-009)",
		links: [["Tender Package", "Tender Package"], ["Tender Evaluation", "Tender Evaluation"],
			["Purchase Order", "Purchase Order"]] },
	{ id: "s11", lane: 4, row: 18, kind: "step", num: 11, title: "Project Execution and Supervision",
		desc: "Manage construction, site visits, quality control (BR-010, BR-011, BR-012)",
		links: [["Site Inspection", "Site Inspection"],
			["Progress Certificate", "Contractor Progress Certificate"],
			["Purchase Invoice", "Purchase Invoice"]] },
	{ id: "s12", lane: 5, row: 19, kind: "step", num: 12, title: "Project Closure and Handover",
		desc: "Inspect, finalize, handover documents (BR-013, BR-014, BR-015)",
		links: [["Project Handover", "Project Handover"], ["Project Closure", "Project Closure"]] },
	{ id: "end", lane: 5, row: 20, kind: "end", title: "End" },
	{ id: "n4", lane: 5, row: 21, kind: "note", title: "Warranty & Defects after completion (BR-016)",
		links: [["Warranty Issue", "Issue"]] },
];

const EDGES = [
	["start", "s1", {}],
	["s1", "s2", { route: "side" }],
	["s2", "d1", { route: "elbow" }],
	["d1", "n1", { label: "No" }],
	["n1", "s2", { route: "loop" }],
	["d1", "s3", { label: "Yes", route: "elbow" }],
	["s3", "s4", {}], ["s4", "s5", {}], ["s5", "s6", {}],
	["s6", "d2", { route: "elbow" }],
	["d2", "n2", { label: "No" }],
	["n2", "s6", { route: "loop" }],
	["d2", "s7", { label: "Yes", route: "elbow" }],
	["s7", "s8", { route: "side" }],
	["s8", "d3", {}],
	["d3", "n3", { label: "Yes", route: "side" }],
	["n3", "s7", { route: "elbow-up" }],
	["d3", "s9", { label: "No" }],
	["s9", "s10", { route: "side" }],
	["s10", "s11", {}],
	["s11", "s12", { route: "side" }],
	["s12", "end", {}],
	["end", "n4", { label: "after completion", dashed: 1 }],
];

const KEY_OUTPUTS = [
	{ n: 1, lane: 0, title: "Client Onboarding",
		items: [["Client requirements (Project Brief)", "Project Brief"],
			["Meeting record (Site Visit)", "Engineering Site Visit"]] },
	{ n: 2, lane: 1, title: "Design & Permits",
		items: [["Concept and detailed drawings", "Engineering Document"],
			["Approved design", "Design Submission"],
			["Building permits", "License Application"]] },
	{ n: 3, lane: 2, title: "Technical Review",
		items: [["Reviewed drawings", "Technical Review"],
			["Bill of quantities (BOQ)", "Project BOQ"]] },
	{ n: 4, lane: 3, title: "Tendering / Execution",
		items: [["Tender documents", "Tender Package"],
			["Signed contract (PO)", "Purchase Order"],
			["Progress certificates", "Contractor Progress Certificate"]] },
	{ n: 5, lane: 4, title: "Handover",
		items: [["Final inspection report", "Site Inspection"],
			["Handover certificate", "Project Handover"],
			["Closure record", "Project Closure"]] },
];

function slug(dt) { return frappe.router.slug(dt); }

function with_br_tooltips(escaped_text) {
	return escaped_text.replace(/BR-\d{3}/g, (code) => {
		const tip = BR_RULES[code];
		if (!tip) return code;
		return `<span class="epm-br" tabindex="0">${code}` +
			`<span class="epm-tip"><b>${code}</b> — ${frappe.utils.escape_html(__(tip))}</span></span>`;
	});
}

function chips(links) {
	return (links || []).map(([label, dt]) => {
		const s = slug(dt);
		return `<span class="epm-chip">
			<a href="/app/${s}" title="${__("Open list")}">${frappe.utils.escape_html(__(label))}</a>
			<a class="epm-new" href="/app/${s}/new" title="${__("Create new")}">＋</a>
		</span>`;
	}).join("");
}

function node_html(n, lane) {
	const pos = `grid-column:${n.lane};grid-row:${n.row}`;
	if (n.kind === "start" || n.kind === "end") {
		const bg = n.kind === "start" ? "#2e7d4f" : "#b91c1c";
		return `<div class="epm-node epm-pill" id="epm-${n.id}"
			style="${pos};background:${bg}">${frappe.utils.escape_html(__(n.title))}</div>`;
	}
	if (n.kind === "decision") {
		return `<div class="epm-node epm-decision-wrap" id="epm-${n.id}" style="${pos}">
			<div class="epm-decision" style="border-color:${lane.border};background:${lane.strong}">
				<span style="color:${lane.text}">${frappe.utils.escape_html(__(n.title)).replace(/\n/g, "<br>")}</span>
			</div></div>`;
	}
	if (n.kind === "note") {
		return `<div class="epm-node epm-note" id="epm-${n.id}"
			style="${pos};border-color:${lane.border};background:${lane.strong};color:${lane.text}">
			${frappe.utils.escape_html(__(n.title))}
			${n.links ? `<div class="epm-links">${chips(n.links)}</div>` : ""}
		</div>`;
	}
	return `<div class="epm-node epm-step" id="epm-${n.id}"
		style="${pos};border-color:${lane.border};background:${lane.tint}">
		<div class="epm-step-title" style="color:${lane.text}">
			${n.num}. ${frappe.utils.escape_html(__(n.title))}
		</div>
		<div class="epm-step-desc" style="color:${lane.text}">
			(${with_br_tooltips(frappe.utils.escape_html(__(n.desc || "")))})
		</div>
		<div class="epm-links">${chips(n.links)}</div>
	</div>`;
}

function render(page) {
	const lanes_head = LANES.map(l =>
		`<div class="epm-lane-head" style="background:${l.tint};color:${l.text}">
			<span class="epm-lane-icon">${l.icon}</span>
			${frappe.utils.escape_html(__(l.label))}</div>`).join("");
	const nodes = NODES.map(n => node_html(n, LANES[n.lane - 1])).join("");
	const lane_bgs = LANES.map(l =>
		`<div class="epm-lane-bg" style="grid-column:${l.key};background:${l.strong}"></div>`).join("");
	const outputs = KEY_OUTPUTS.map(o => {
		const l = LANES[o.lane];
		const items = o.items.map(([label, dt]) =>
			`<a class="epm-out-item" href="/app/${slug(dt)}">- ${frappe.utils.escape_html(__(label))}</a>`).join("");
		return `<div class="epm-out-card" style="background:${l.tint};border-color:${l.border}">
			<div class="epm-out-title" style="color:${l.text}">
				<span class="epm-out-num" style="background:${l.border}">${o.n}</span>
				${frappe.utils.escape_html(__(o.title))}</div>
			<div class="epm-out-items" style="color:${l.text}">${items}</div>
		</div>`;
	}).join("");

	$(page.body).html(`
		<style>
			.epm-wrap { padding: 8px 4px 40px; overflow-x: auto; }
			.epm-header { text-align: center; margin: 4px 0 14px; position: relative; }
			.epm-title { font-size: 24px; font-weight: 800; color: #1e3a5f; }
			.epm-subtitle { font-size: 14px; color: var(--text-muted); }
			.epm-brand { position: absolute; right: 8px; top: 4px; text-align: right;
				font-weight: 700; color: #1e3a5f; font-size: 13px; }
			.epm-heads, .epm-grid, .epm-outputs { display: grid;
				grid-template-columns: repeat(5, minmax(210px, 1fr)); gap: 0 10px;
				min-width: 1120px; }
			.epm-lane-head { padding: 12px 8px; text-align: center; font-weight: 700;
				border-radius: 8px 8px 0 0; font-size: 13px; position: sticky; top: 0;
				z-index: 3; display: flex; flex-direction: column; align-items: center;
				gap: 4px; }
			.epm-lane-icon { font-size: 22px; line-height: 1; }
			.epm-grid { position: relative; grid-auto-rows: minmax(50px, auto);
				row-gap: 30px; padding: 26px 0 14px; }
			.epm-lane-bg { grid-row: 1 / 22; }
			.epm-node { position: relative; z-index: 2; align-self: center;
				justify-self: center; width: 90%; }
			.epm-step { border: 1.5px solid; border-radius: 10px; padding: 8px 10px;
				box-shadow: 0 1px 3px rgba(0,0,0,.10); text-align: center; }
			.epm-step-title { font-weight: 700; font-size: 12.5px; line-height: 1.3; }
			.epm-step-desc { font-size: 11px; margin: 3px 0 6px; opacity: .9; }
			.epm-note { border: 1.5px solid; border-radius: 10px; padding: 7px 10px;
				font-size: 11.5px; font-weight: 700; text-align: center; width: 80%;
				box-shadow: 0 1px 3px rgba(0,0,0,.08); }
			.epm-links { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center;
				margin-top: 4px; }
			.epm-chip { display: inline-flex; border: 1px solid rgba(0,0,0,.18);
				border-radius: 999px; overflow: hidden; font-size: 11px; background: #fff; }
			.epm-chip a { padding: 2px 8px; text-decoration: none; font-weight: 600; }
			.epm-chip a.epm-new { border-left: 1px solid rgba(0,0,0,.18); font-weight: 800; }
			.epm-chip a:hover { background: rgba(0,0,0,.06); }
			.epm-pill { color: #fff; font-weight: 700; text-align: center;
				border-radius: 999px; padding: 8px 0; width: 120px;
				box-shadow: 0 1px 3px rgba(0,0,0,.15); }
			.epm-decision-wrap { display: flex; justify-content: center; }
			.epm-decision { width: 112px; height: 112px; border: 1.5px solid;
				transform: rotate(45deg); border-radius: 10px; display: flex;
				align-items: center; justify-content: center;
				box-shadow: 0 1px 3px rgba(0,0,0,.10); }
			.epm-decision span { transform: rotate(-45deg); font-size: 11px;
				font-weight: 700; text-align: center; line-height: 1.25; }
			.epm-svg { position: absolute; inset: 0; width: 100%; height: 100%;
				z-index: 1; pointer-events: none; }
			.epm-edge-label { font-size: 10.5px; font-weight: 800; fill: #333;
				paint-order: stroke; stroke: #fff; stroke-width: 3.5px; }
			.epm-outputs-title { font-weight: 800; font-size: 13px; margin: 18px 2px 8px;
				color: #1e3a5f; }
			.epm-out-card { border: 1.5px solid; border-radius: 10px; padding: 10px; }
			.epm-out-title { font-weight: 800; font-size: 12.5px; display: flex;
				align-items: center; gap: 6px; margin-bottom: 5px; }
			.epm-out-num { color: #fff; border-radius: 50%; min-width: 20px; height: 20px;
				display: inline-flex; align-items: center; justify-content: center;
				font-size: 11px; }
			.epm-out-items { display: flex; flex-direction: column; gap: 2px; }
			.epm-out-item { font-size: 11px; text-decoration: none; color: inherit; }
			.epm-out-item:hover { text-decoration: underline; color: inherit; }
			.epm-footnote { font-size: 11px; color: var(--text-muted); margin-top: 10px; }
			.epm-br { border-bottom: 1px dotted currentColor; cursor: help;
				position: relative; font-weight: 700; white-space: nowrap; outline: none; }
			.epm-tip { display: none; position: absolute; left: 50%;
				bottom: calc(100% + 8px); transform: translateX(-50%); width: 240px;
				background: #1f2937; color: #fff; font-size: 11px; font-weight: 400;
				line-height: 1.45; padding: 8px 10px; border-radius: 8px;
				box-shadow: 0 4px 14px rgba(0,0,0,.25); z-index: 50;
				white-space: normal; text-align: left; pointer-events: none; }
			.epm-tip::after { content: ""; position: absolute; top: 100%; left: 50%;
				transform: translateX(-50%); border: 6px solid transparent;
				border-top-color: #1f2937; }
			.epm-br:hover .epm-tip, .epm-br:focus .epm-tip { display: block; }
		</style>
		<div class="epm-wrap">
			<div class="epm-header">
				<div class="epm-title">${__("Engineering Project Process Flow Chart")}</div>
				<div class="epm-subtitle">${__("From Client Onboarding to Handover — click any step to open or create the transaction")}</div>
				<div class="epm-brand">NeoEngineering</div>
			</div>
			<div class="epm-heads">${lanes_head}</div>
			<div class="epm-grid" id="epm-grid">
				${lane_bgs}
				<svg class="epm-svg" id="epm-svg">
					<defs><marker id="epm-arrow" viewBox="0 0 10 10" refX="9" refY="5"
						markerWidth="7" markerHeight="7" orient="auto-start-reverse">
						<path d="M 0 0 L 10 5 L 0 10 z" fill="#333"></path>
					</marker></defs>
				</svg>
				${nodes}
			</div>
			<div class="epm-outputs-title">${__("Key Outputs at Each Stage:")}</div>
			<div class="epm-outputs">${outputs}</div>
			<div class="epm-footnote"><b>${__("Note:")}</b> ${__("The process may vary based on project type, client requirements, and contract terms. Hover any BR-0xx code for the exact system rule.")}</div>
		</div>`);

	const draw = () => draw_edges();
	setTimeout(draw, 60);
	$(window).off("resize.epm").on("resize.epm", frappe.utils.debounce(draw, 150));
}

function draw_edges() {
	const grid = document.getElementById("epm-grid");
	const svg = document.getElementById("epm-svg");
	if (!grid || !svg) return;
	const gb = grid.getBoundingClientRect();
	svg.setAttribute("width", grid.scrollWidth);
	svg.setAttribute("height", grid.scrollHeight);
	[...svg.querySelectorAll("path,text")].forEach(el => el.remove());

	const box = id => {
		const el = document.getElementById("epm-" + id);
		if (!el) return null;
		const r = el.getBoundingClientRect();
		return { l: r.left - gb.left, t: r.top - gb.top, w: r.width, h: r.height,
			cx: r.left - gb.left + r.width / 2, cy: r.top - gb.top + r.height / 2 };
	};
	const P = (d, dashed) => {
		const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
		p.setAttribute("d", d);
		p.setAttribute("fill", "none");
		p.setAttribute("stroke", "#333");
		p.setAttribute("stroke-width", "1.8");
		if (dashed) p.setAttribute("stroke-dasharray", "6 4");
		p.setAttribute("marker-end", "url(#epm-arrow)");
		svg.appendChild(p);
	};
	const T = (x, y, text) => {
		const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
		t.setAttribute("x", x); t.setAttribute("y", y);
		t.setAttribute("class", "epm-edge-label");
		t.textContent = text;
		svg.appendChild(t);
	};

	EDGES.forEach(([from, to, opt]) => {
		const a = box(from), b = box(to);
		if (!a || !b) return;
		const o = opt || {};
		let d, lx, ly;
		if (o.route === "loop") {
			const gx = Math.min(a.l, b.l) - 20;
			d = `M ${a.l} ${a.cy} H ${gx} V ${b.cy} H ${b.l}`;
			lx = gx + 5; ly = Math.min(a.cy, b.cy) - 8;
		} else if (o.route === "elbow-up") {
			// up-and-into-bottom of a node in an adjacent lane (send-back loop)
			const midx = (a.cx + b.cx) / 2;
			d = `M ${a.cx} ${a.t} V ${b.t + b.h + 14} H ${b.cx} V ${b.t + b.h}`;
			lx = midx; ly = b.t + b.h + 26;
		} else if (o.route === "side" && Math.abs(a.cy - b.cy) < 200) {
			const fromx = b.cx > a.cx ? a.l + a.w : a.l;
			const tox = b.cx > a.cx ? b.l : b.l + b.w;
			d = `M ${fromx} ${a.cy} H ${(fromx + tox) / 2} V ${b.cy} H ${tox}`;
			lx = fromx + (b.cx > a.cx ? 8 : -26); ly = a.cy - 6;
		} else if (o.route === "elbow" || Math.abs(a.cx - b.cx) > 40) {
			if (b.t > a.t + a.h) {
				const midy = a.t + a.h + Math.max(12, (b.t - a.t - a.h) / 2);
				d = `M ${a.cx} ${a.t + a.h} V ${midy} H ${b.cx} V ${b.t}`;
				lx = a.cx + 8; ly = a.t + a.h + 14;
			} else {
				const fromx = b.cx > a.cx ? a.l + a.w : a.l;
				const tox = b.cx > a.cx ? b.l : b.l + b.w;
				d = `M ${fromx} ${a.cy} H ${(fromx + tox) / 2} V ${b.cy} H ${tox}`;
				lx = (fromx + tox) / 2 + 6; ly = a.cy - 6;
			}
		} else {
			d = `M ${a.cx} ${a.t + a.h} V ${b.t}`;
			lx = a.cx + 8; ly = a.t + a.h + 14;
		}
		P(d, o.dashed);
		if (o.label) T(lx, ly, __(o.label));
	});
}
