frappe.pages["engineering-process-map"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Engineering Process Map"),
		single_column: true,
	});
	page.set_secondary_action(__("Refresh"), () => render(page));
	render(page);
};

const LANES = [
	{ key: 1, label: "Client & Business Development", tint: "#eaf2fb", border: "#3b6fb5" },
	{ key: 2, label: "Design Department", tint: "#eaf6ec", border: "#3d7a4a" },
	{ key: 3, label: "Technical Department", tint: "#fdf6e3", border: "#c98a2d" },
	{ key: 4, label: "Tendering / Supervision", tint: "#f1ecfa", border: "#6f4fb0" },
	{ key: 5, label: "PM, Finance & Close-out", tint: "#fdeeee", border: "#b04a4a" },
];

// kind: start | end | step | decision | note
// links: [[label, doctype]] — first link is the primary transaction
const NODES = [
	{ id: "start", lane: 1, row: 1, kind: "start", title: "Start" },
	{ id: "s1", lane: 1, row: 2, kind: "step", num: 1, title: "Client Inquiry",
		desc: "Record the enquiry and first meeting", links: [["Lead", "Lead"]] },
	{ id: "s2", lane: 1, row: 3, kind: "step", num: 2, title: "Opportunity & Requirements",
		desc: "Qualify scope, budget, services", links: [["Opportunity", "Opportunity"]] },
	{ id: "s3", lane: 2, row: 4, kind: "step", num: 3, title: "Project Brief",
		desc: "Requirements baseline — get it Approved", links: [["Project Brief", "Project Brief"]] },
	{ id: "s4", lane: 2, row: 5, kind: "step", num: 4, title: "Technical & Financial Proposal",
		desc: "Pick Service Type on the quotation", links: [["Quotation", "Quotation"]] },
	{ id: "d1", lane: 1, row: 6, kind: "decision", title: "Client\napproves?" },
	{ id: "s5", lane: 5, row: 7, kind: "step", num: 5, title: "Contract & Project Kick-off",
		desc: "Create the Project · fill Engineering Control tab (BR-001)",
		links: [["Project", "Project"]] },
	{ id: "s6", lane: 2, row: 8, kind: "step", num: 6, title: "Site Visit & Data Collection",
		desc: "Observations, attendees, follow-ups", links: [["Site Visit", "Engineering Site Visit"]] },
	{ id: "s7", lane: 2, row: 9, kind: "step", num: 7, title: "Prepare Design",
		desc: "Register drawings, add revisions Rev A, B… (BR-004)",
		links: [["Engineering Document", "Engineering Document"]] },
	{ id: "s8", lane: 2, row: 10, kind: "step", num: 8, title: "Submit Design for Client Review",
		desc: "Needs ≥1 current revision (BR-003)",
		links: [["Design Submission", "Design Submission"]] },
	{ id: "d2", lane: 1, row: 11, kind: "decision", title: "Client\napproval?" },
	{ id: "s9", lane: 3, row: 12, kind: "step", num: 9, title: "Technical Review",
		desc: "Check drawings, log comments", links: [["Technical Review", "Technical Review"]] },
	{ id: "d3", lane: 3, row: 13, kind: "decision", title: "Any mandatory\nremarks open?" },
	{ id: "s10", lane: 3, row: 14, kind: "step", num: 10, title: "Approve BOQ",
		desc: "Baseline quantities — valid UOM & qty (BR-006)",
		links: [["Project BOQ", "Project BOQ"]] },
	{ id: "s11", lane: 2, row: 15, kind: "step", num: 11, title: "Permits / Licensing",
		desc: "Runs in parallel — mandatory documents gate submission",
		links: [["License Application", "License Application"]] },
	{ id: "s12", lane: 4, row: 16, kind: "step", num: 12, title: "Tendering & Award",
		desc: "Needs approved BOQ (BR-007) · evaluation before award (BR-009)",
		links: [["Tender Package", "Tender Package"], ["Tender Evaluation", "Tender Evaluation"],
			["RFQ", "Request for Quotation"], ["Purchase Order", "Purchase Order"]] },
	{ id: "s13", lane: 4, row: 17, kind: "step", num: 13, title: "Execution & Supervision",
		desc: "Inspections (BR-010) · certify ≤100% (BR-011) · invoice ≤ certified (BR-012)",
		links: [["Site Inspection", "Site Inspection"],
			["Progress Certificate", "Contractor Progress Certificate"],
			["Purchase Invoice", "Purchase Invoice"]] },
	{ id: "s14", lane: 5, row: 18, kind: "step", num: 14, title: "Handover",
		desc: "Mandatory documents delivered or waived (BR-013)",
		links: [["Project Handover", "Project Handover"]] },
	{ id: "s15", lane: 5, row: 19, kind: "step", num: 15, title: "Closure",
		desc: "Checklist + clearances (BR-014) → Project auto-Completed (BR-015)",
		links: [["Project Closure", "Project Closure"]] },
	{ id: "end", lane: 5, row: 20, kind: "end", title: "End" },
	{ id: "s16", lane: 5, row: 21, kind: "step", num: 16, title: "Warranty & Defects",
		desc: "After completion — verified close-out (BR-016)",
		links: [["Warranty Issue", "Issue"]] },
];

// [from, to, {label, route, dashed}] — route: v (vertical), h (horizontal),
// elbow (down then across), loop (back up via left gutter)
const EDGES = [
	["start", "s1", {}],
	["s1", "s2", {}],
	["s2", "s3", { route: "elbow" }],
	["s3", "s4", {}],
	["s4", "d1", { route: "elbow" }],
	["d1", "s4", { label: "No — revise", route: "loop", dashed: 1 }],
	["d1", "s5", { label: "Yes", route: "elbow" }],
	["s5", "s6", { route: "elbow" }],
	["s6", "s7", {}],
	["s7", "s8", {}],
	["s8", "d2", { route: "elbow" }],
	["d2", "s7", { label: "No — new revision", route: "loop", dashed: 1 }],
	["d2", "s9", { label: "Yes", route: "elbow" }],
	["s9", "d3", {}],
	["d3", "s7", { label: "Yes — send back", route: "loop", dashed: 1 }],
	["d3", "s10", { label: "No" }],
	["s8", "s11", { label: "in parallel", route: "elbow", dashed: 1 }],
	["s10", "s12", { route: "elbow" }],
	["s12", "s13", {}],
	["s13", "s14", { route: "elbow" }],
	["s14", "s15", {}],
	["s15", "end", {}],
	["end", "s16", { label: "after completion", dashed: 1 }],
];

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

function with_br_tooltips(escaped_text) {
	return escaped_text.replace(/BR-\d{3}/g, (code) => {
		const tip = BR_RULES[code];
		if (!tip) return code;
		return `<span class="epm-br" tabindex="0">${code}` +
			`<span class="epm-tip"><b>${code}</b> — ${frappe.utils.escape_html(tip)}</span></span>`;
	});
}

function slug(dt) {
	return frappe.router.slug(dt);
}

function node_html(n, lane) {
	if (n.kind === "start" || n.kind === "end") {
		const bg = n.kind === "start" ? "#2e7d4f" : "#b04a4a";
		return `<div class="epm-node epm-pill" id="epm-${n.id}"
			style="grid-column:${n.lane};grid-row:${n.row};background:${bg}">${n.title}</div>`;
	}
	if (n.kind === "decision") {
		return `<div class="epm-node epm-decision-wrap" id="epm-${n.id}"
			style="grid-column:${n.lane};grid-row:${n.row}">
			<div class="epm-decision" style="border-color:${lane.border}">
				<span>${frappe.utils.escape_html(n.title).replace(/\n/g, "<br>")}</span>
			</div></div>`;
	}
	const links = (n.links || []).map(([label, dt], i) => {
		const s = slug(dt);
		return `<span class="epm-chip">
			<a class="epm-open" href="/app/${s}" title="${__("Open list")}">${frappe.utils.escape_html(label)}</a>
			<a class="epm-new" href="/app/${s}/new" title="${__("Create new")}">＋</a>
		</span>`;
	}).join("");
	return `<div class="epm-node epm-step" id="epm-${n.id}"
		style="grid-column:${n.lane};grid-row:${n.row};border-color:${lane.border};background:#fff">
		<div class="epm-step-title">
			<span class="epm-num" style="background:${lane.border}">${n.num}</span>
			${frappe.utils.escape_html(n.title)}
		</div>
		<div class="epm-step-desc">${with_br_tooltips(frappe.utils.escape_html(n.desc || ""))}</div>
		<div class="epm-links">${links}</div>
	</div>`;
}

function render(page) {
	const lanes_head = LANES.map(l =>
		`<div class="epm-lane-head" style="background:${l.tint};border-top:4px solid ${l.border}">
			${frappe.utils.escape_html(l.label)}</div>`).join("");
	const nodes = NODES.map(n => node_html(n, LANES[n.lane - 1])).join("");
	const lane_bgs = LANES.map(l =>
		`<div class="epm-lane-bg" style="grid-column:${l.key};background:${l.tint}55"></div>`).join("");

	$(page.body).html(`
		<style>
			.epm-wrap { padding: 8px 4px 40px; overflow-x: auto; }
			.epm-heads, .epm-grid { display: grid;
				grid-template-columns: repeat(5, minmax(215px, 1fr)); gap: 0 14px;
				min-width: 1150px; }
			.epm-lane-head { padding: 10px 8px; text-align: center; font-weight: 700;
				border-radius: 8px 8px 0 0; font-size: 13px; position: sticky; top: 0; z-index: 3; }
			.epm-grid { position: relative; grid-auto-rows: minmax(58px, auto);
				row-gap: 34px; padding: 26px 0 10px; }
			.epm-lane-bg { grid-row: 1 / 22; border-radius: 0 0 8px 8px; }
			.epm-node { position: relative; z-index: 2; align-self: center; justify-self: center;
				width: 92%; }
			.epm-step { border: 2px solid; border-radius: 10px; padding: 8px 10px;
				box-shadow: 0 1px 3px rgba(0,0,0,.08); }
			.epm-step-title { font-weight: 700; font-size: 12.5px; display: flex;
				gap: 6px; align-items: center; }
			.epm-num { color: #fff; border-radius: 50%; min-width: 20px; height: 20px;
				display: inline-flex; align-items: center; justify-content: center;
				font-size: 11px; }
			.epm-step-desc { font-size: 11px; color: var(--text-muted); margin: 4px 0 6px; }
			.epm-links { display: flex; flex-wrap: wrap; gap: 4px; }
			.epm-chip { display: inline-flex; border: 1px solid var(--gray-300);
				border-radius: 999px; overflow: hidden; font-size: 11px; background: var(--gray-50); }
			.epm-chip a { padding: 2px 8px; text-decoration: none; }
			.epm-chip a.epm-new { border-left: 1px solid var(--gray-300); font-weight: 700; }
			.epm-chip a:hover { background: var(--gray-200); }
			.epm-pill { color: #fff; font-weight: 700; text-align: center;
				border-radius: 999px; padding: 8px 0; width: 130px; }
			.epm-decision-wrap { display: flex; justify-content: center; }
			.epm-decision { width: 120px; height: 120px; background: #fff; border: 2px solid;
				transform: rotate(45deg); border-radius: 12px; display: flex;
				align-items: center; justify-content: center;
				box-shadow: 0 1px 3px rgba(0,0,0,.08); }
			.epm-decision span { transform: rotate(-45deg); font-size: 11px;
				font-weight: 700; text-align: center; line-height: 1.25; }
			.epm-svg { position: absolute; inset: 0; width: 100%; height: 100%;
				z-index: 1; pointer-events: none; }
			.epm-edge-label { font-size: 10px; font-weight: 700; fill: #555;
				paint-order: stroke; stroke: #fff; stroke-width: 3px; }
			.epm-legend { font-size: 12px; color: var(--text-muted); margin: 6px 2px 12px; }
			.epm-br { border-bottom: 1px dotted var(--text-muted); cursor: help;
				position: relative; font-weight: 700; white-space: nowrap; outline: none; }
			.epm-tip { display: none; position: absolute; left: 50%; bottom: calc(100% + 8px);
				transform: translateX(-50%); width: 240px; background: #1f2937; color: #fff;
				font-size: 11px; font-weight: 400; line-height: 1.45; padding: 8px 10px;
				border-radius: 8px; box-shadow: 0 4px 14px rgba(0,0,0,.25);
				z-index: 50; white-space: normal; text-align: left; pointer-events: none; }
			.epm-tip::after { content: ""; position: absolute; top: 100%; left: 50%;
				transform: translateX(-50%); border: 6px solid transparent;
				border-top-color: #1f2937; }
			.epm-br:hover .epm-tip, .epm-br:focus .epm-tip { display: block; }
		</style>
		<div class="epm-wrap">
			<div class="epm-legend">${__("Follow the arrows top to bottom. On any step: click the name to open the list, or ＋ to create the transaction. Dashed arrows are loops / parallel paths.")}</div>
			<div class="epm-heads">${lanes_head}</div>
			<div class="epm-grid" id="epm-grid">
				${lane_bgs}
				<svg class="epm-svg" id="epm-svg">
					<defs><marker id="epm-arrow" viewBox="0 0 10 10" refX="9" refY="5"
						markerWidth="7" markerHeight="7" orient="auto-start-reverse">
						<path d="M 0 0 L 10 5 L 0 10 z" fill="#4a5568"></path>
					</marker></defs>
				</svg>
				${nodes}
			</div>
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
	// clear previous paths/labels (keep defs)
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
		p.setAttribute("stroke", "#4a5568");
		p.setAttribute("stroke-width", "2");
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
			// back up via the left gutter of the source lane
			const gx = Math.min(a.l, b.l) - 22;
			d = `M ${a.l} ${a.cy} H ${gx} V ${b.cy} H ${b.l}`;
			lx = gx + 6; ly = Math.min(a.cy, b.cy) - 8;
		} else if (o.route === "elbow" || Math.abs(a.cx - b.cx) > 40) {
			if (b.t > a.t + a.h) {
				// down, across, into the top of the target
				const midy = a.t + a.h + Math.max(14, (b.t - a.t - a.h) / 2);
				d = `M ${a.cx} ${a.t + a.h} V ${midy} H ${b.cx} V ${b.t}`;
				lx = a.cx + 8; ly = a.t + a.h + 14;
			} else {
				// roughly level — horizontal into the near side
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
