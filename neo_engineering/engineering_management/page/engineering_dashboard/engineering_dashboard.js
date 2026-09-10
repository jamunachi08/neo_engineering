// NeoEngineering — Engineering Management Dashboard
// One API round-trip; bilingual via __(); frappe-charts for visuals.

frappe.pages["engineering-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Engineering Dashboard"),
		single_column: true,
	});
	page.set_secondary_action(__("Refresh"), () => load(page));
	page.add_menu_item(__("Process Map"), () => frappe.set_route("engineering-process-map"));
	load(page);
};

const CARD_DEFS = [
	["active_projects", "Active Projects", "#1e4e8c", "Project"],
	["open_submissions", "Design Submissions with Client", "#2e7d4f", "Design Submission"],
	["pending_reviews", "Pending Technical Reviews", "#b45309", "Technical Review"],
	["licenses_pending", "Licenses in Progress", "#b45309", "License Application"],
	["tenders_in_progress", "Tenders in Progress", "#6d28d9", "Tender Package"],
	["open_observations", "Open Site Observations", "#b91c1c", "Site Inspection"],
	["certified_this_month", "Certified This Month (SAR)", "#0e7490", "Contractor Progress Certificate"],
	["open_warranty", "Open Warranty Issues", "#b91c1c", "Issue"],
];

function load(page) {
	frappe.call("neo_engineering.api.dashboard.get_dashboard_data").then(r => {
		render(page, r.message || {});
	});
}

function fmt(v) {
	return frappe.format(v, { fieldtype: "Float", precision: 0 });
}

function render(page, data) {
	const cards = CARD_DEFS.map(([key, label, color, dt]) => {
		const raw = (data.cards || {})[key] || 0;
		const val = key === "certified_this_month" ? fmt(raw) : raw;
		return `<a class="edb-card" href="/app/${frappe.router.slug(dt)}"
			style="border-top-color:${color}">
			<div class="edb-card-val" style="color:${color}">${val}</div>
			<div class="edb-card-label">${frappe.utils.escape_html(__(label))}</div>
		</a>`;
	}).join("");

	const rows = (data.projects || []).map(p => `
		<tr>
			<td><a href="/app/project/${encodeURIComponent(p.name)}">
				${frappe.utils.escape_html(p.project_name || p.name)}</a></td>
			<td>${frappe.utils.escape_html(__(p.custom_project_stage || ""))}</td>
			<td>${frappe.utils.escape_html(__(p.custom_service_type || ""))}</td>
			<td class="edb-num">${flt_pct(p.custom_document_completion_pct)}</td>
			<td class="edb-num">${flt_pct(p.custom_site_progress_pct)}</td>
		</tr>`).join("");

	$(page.body).html(`
		<style>
			.edb-wrap { padding: 8px 4px 40px; }
			.edb-cards { display: grid; gap: 10px;
				grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); }
			.edb-card { border: 1px solid var(--border-color); border-top: 4px solid;
				border-radius: 10px; padding: 12px; background: var(--card-bg);
				text-decoration: none; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
			.edb-card:hover { box-shadow: 0 3px 8px rgba(0,0,0,.10); }
			.edb-card-val { font-size: 26px; font-weight: 800; line-height: 1.1; }
			.edb-card-label { font-size: 11.5px; color: var(--text-muted);
				margin-top: 4px; }
			.edb-charts { display: grid; gap: 12px; margin-top: 14px;
				grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
			.edb-panel { border: 1px solid var(--border-color); border-radius: 10px;
				padding: 10px 12px; background: var(--card-bg); }
			.edb-panel-title { font-weight: 700; font-size: 13px; margin-bottom: 4px; }
			.edb-table { width: 100%; font-size: 12px; border-collapse: collapse;
				margin-top: 4px; }
			.edb-table th, .edb-table td { padding: 6px 8px; text-align: start;
				border-bottom: 1px solid var(--border-color); }
			.edb-table th { color: var(--text-muted); font-weight: 600; }
			.edb-num { text-align: end; }
		</style>
		<div class="edb-wrap">
			<div class="edb-cards">${cards}</div>
			<div class="edb-charts">
				<div class="edb-panel">
					<div class="edb-panel-title">${__("Projects by Stage")}</div>
					<div id="edb-stage"></div>
				</div>
				<div class="edb-panel">
					<div class="edb-panel-title">${__("Engineering Documents by Status")}</div>
					<div id="edb-docs"></div>
				</div>
				<div class="edb-panel">
					<div class="edb-panel-title">${__("Certified Amounts — Last 6 Months")}</div>
					<div id="edb-trend"></div>
				</div>
			</div>
			<div class="edb-panel" style="margin-top:12px">
				<div class="edb-panel-title">${__("Recent Projects")}</div>
				<table class="edb-table">
					<thead><tr>
						<th>${__("Project")}</th><th>${__("Stage")}</th>
						<th>${__("Service Type")}</th>
						<th class="edb-num">${__("Docs %")}</th>
						<th class="edb-num">${__("Site %")}</th>
					</tr></thead>
					<tbody>${rows || `<tr><td colspan="5">${__("No projects yet")}</td></tr>`}</tbody>
				</table>
			</div>
		</div>`);

	chart("#edb-stage", "bar",
		(data.by_stage || []).map(r => __(r.stage)),
		(data.by_stage || []).map(r => r.qty), "#1e4e8c");
	chart("#edb-docs", "donut",
		(data.doc_status || []).map(r => __(r.status)),
		(data.doc_status || []).map(r => r.qty));
	chart("#edb-trend", "line",
		(data.certified_trend || []).map(r => r.month),
		(data.certified_trend || []).map(r => r.amount), "#0e7490");
}

function flt_pct(v) {
	return (v || v === 0) ? `${Math.round(v)}%` : "—";
}

function chart(sel, type, labels, values, color) {
	if (!labels.length) {
		$(sel).html(`<div style="color:var(--text-muted);font-size:12px;padding:18px 4px">
			${__("No data yet")}</div>`);
		return;
	}
	new frappe.Chart(sel, {
		type, height: 200,
		colors: color ? [color] : undefined,
		data: { labels, datasets: [{ values }] },
		axisOptions: { xIsSeries: type === "line" },
	});
}
