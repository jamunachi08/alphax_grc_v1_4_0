# AlphaX GRC v1.4.4 — Hotfix: SACS-002 doctype rename

Saudi-first Governance, Risk & Compliance app for Frappe / ERPNext.
Published by IRSAA Business Solutions (support@irsaa.com).

## What's fixed in v1.4.4

**Hotfix for v1.4.3 install crash.** The doctype `GRC Aramco SACS-002
Control` failed to install because Frappe's module-name autoresolver
expects a hyphen in a doctype name to map to an underscore in the
folder path. The shipped folder was `grc_aramco_sacs002_control` (no
underscore between `sacs` and `002`), but Frappe was looking for
`grc_aramco_sacs_002_control` (with the underscore). Result: install
crashed at step 55 of 88 with `ImportError: No module named
'alphax_grc.alphax_grc.doctype.grc_aramco_sacs_002_control'`.

Fix: renamed the doctype itself from `GRC Aramco SACS-002 Control` to
`GRC Aramco SACS002 Control` (no hyphen). The folder name is now
correct as-is. Avoids any future special-character resolution issues
with this doctype.

User-facing labels still display "SACS-002" in menu items, error
messages, and READMEs — the rename only affects the internal doctype
identifier. The framework being assessed is still SACS-002.

## What's in this build

Everything from v1.4.3 — Aramco CCC complete process automation —
remains intact:

- 5 Aramco doctypes (Engagement, Certificate, SACS002 Control,
  Control Assessment, Audit Firm)
- 28 placeholder SACS-002 controls across 14 domains
- Renewal automation (180/90/30/0-day alerts) with per-cert send tracking
- Incident automation (4-hour initial + 72-hour final reports)
- Aramco CCC dashboard at `/app/grc-aramco-ccc` with the clickable
  8-stage process wheel and stage drilldown
- All v1.4.x NCA toolkit, multi-tenant, lifecycle features

## Install / Upgrade

If your v1.4.3 install crashed mid-sync (as the user's
`neoterminal.k.frappe.cloud` did), the database is in a partial state.
Recommended: uninstall and reinstall.

```bash
# Clean the partial v1.4.3 install:
bench --site neoterminal.k.frappe.cloud uninstall-app alphax_grc --force

# Get the v1.4.4 zip:
bench get-app alphax_grc <url-of-this-zip>

# Install fresh:
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
bench restart
```

If you're upgrading from a clean v1.4.1 or v1.4.2 (before v1.4.3's
crash), a normal migrate works:

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

## What's new in v1.4.3

This release builds out the **Saudi Aramco Cybersecurity Compliance
Certificate (CCC)** lifecycle: scoping, SACS-002 self-assessment, audit,
findings, remediation, certification, and renewal — all with email
automation and a dedicated dashboard.

### Honest scoping note

The full SACS-002 control catalog is not freely downloadable (it's a
licensed Aramco document). v1.4.3 ships **28 placeholder controls across
all 14 SACS-002 domains**, each marked `is_placeholder=True`. Once you
provide the licensed SACS-002 PDF/Excel, an admin action can replace the
placeholders with verbatim control text. The framework structure,
workflow, dashboard, and notification automation work fully today; only
the control text is placeholder.

Audit firm directory is also placeholder — populate from your knowledge
of Aramco-accredited firms.

### New doctypes

- **GRC Aramco CCC Engagement** — umbrella record per vendor per
  certification cycle. Status workflow: Scoping → Self-Assessment →
  Audit Scheduled → Audit In Progress → Findings → Remediation →
  Certified → Renewal Due → Lapsed. Auto-status transitions based on
  dates. Auto-computed compliance % from control assessments. Includes
  `populate_controls_from_library()` action that bulk-loads applicable
  SACS-002 controls based on the engagement's tier (Critical / High /
  Medium / Low).

- **GRC Aramco SACS-002 Control** — global control library scaffolded
  with 28 placeholder controls organised by 14 SACS-002 domains
  (Asset Management, Access Control, Cryptography, Physical Security,
  Operations, Communications, System Acquisition Development, Supplier
  Relationships, Incident Management, Business Continuity, Compliance,
  HR Security, Awareness & Training, Governance). Tier applicability,
  cross-mapping to NCA ECC and ISO 27001.

- **GRC Aramco Control Assessment** — child table of CCC Engagement.
  Per-control status (Not Started / In Progress / Compliant /
  Partially Compliant / Non-Compliant / N/A), score, evidence
  attachment, remediation plan, link to GRC Remediation Action.

- **GRC Aramco Certificate** — issued certificate record with
  certificate number, issue/expiry dates, certified scope, audit firm,
  certificate PDF attachment. Auto-computed days_to_expiry,
  renewal_kickoff_date (180 days before expiry), and status
  (Active / Expiring Soon / Pending Renewal / Expired / Revoked).
  Notification tracking fields prevent duplicate emails.

- **GRC Aramco Audit Firm** — accredited assessor directory with
  contact details, accreditation status, accreditation number/dates,
  service classes covered. Default status "Unverified" with a flag to
  verify with Aramco SCM before engaging.

### Renewal automation

Daily scheduler runs `notifications.check_aramco_certificate_renewals()`:

- **180 days before expiry** → "Renewal kickoff" advisory email to lead
  consultant + GRC Admin/Aramco Compliance Owner role users
- **90 days** → "Renewal must now be in progress" attention email
- **30 days** → "URGENT — confirm renewal status" escalation
- **0 days** → "EXPIRED" alert with non-compliance warning

Each tier's email tracks the send date on the certificate
(`last_180day_alert_sent` etc.) so the same alert never fires twice.

### Incident notification automation

- **On create**: `aramco_incident_on_update` doc-event sends an
  immediate "New Aramco-scope incident" email to the lead consultant
  + Aramco Compliance Owners. Marks `initial_notification_sent_on` so
  the 4-hour SLA timer can start.
- **Daily check**: `check_aramco_incident_escalation()` reviews open
  incidents. If 4-hour initial notification not sent, escalates. If
  72-hour final business and technical reports not on file, escalates
  again.

All 4-hour, 24-hour, and 72-hour Aramco SLAs from the CCC programme
are now enforced automatically.

### Aramco CCC dashboard — `/app/grc-aramco-ccc`

Branded dashboard (gradient hero in Aramco colours) showing:
- Hero stats: Engagements / Certificates / Active / Expiring 30 days /
  Expiring 90 days / Expired
- Engagements-by-stage grid (9 status buckets with colour coding)
- **Interactive 8-stage CCC lifecycle wheel** (Scoping → Self-Assessment
  → Audit Scheduled → Audit In Progress → Findings → Remediation →
  Certified → Renewal Due) with live engagement counts per stage,
  red/amber/green status colouring based on engagement distribution,
  and **clickable drilldown** — click any stage in the wheel (or the
  matching row in the side list) to navigate to a filtered list view
  of engagements in that stage, scoped to the active client picker.
- Hover any stage to read what it covers in the side detail panel
- Active engagements table with compliance %, open findings, lead
- Certificates table sorted by expiry, with colour-coded days-to-expiry

Client picker scopes to one engagement or shows firm-wide.

### Wiring

- `GRC Aramco CCC Engagement` and `GRC Aramco Certificate` added to
  `WATCHED_DOCTYPES` so dashboard snapshots refresh on save (live
  system from v1.3.2).
- `GRC Aramco Incident Notification` doc_events wire both notification
  email and dashboard invalidation.
- New page `grc-aramco-ccc` registered in PAGES.
- Workspace gains "Aramco CCC" shortcut tile and 5 new link entries.

### Sample data seeded for DEMO client

- 28 SACS-002 placeholder controls (across 14 domains)
- 1 sample CCC engagement (tier: High, status: Self-Assessment)
- 1 sample certificate (expires in 60 days — triggers the 90-day alert)
- 1 audit firm placeholder

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After upgrade:
1. Open `/app/grc-aramco-ccc` to see the dashboard with the sample
   certificate expiring in 60 days.
2. Open the sample engagement; on the form, click the **Populate
   Controls from Library** action (server method) to see all
   applicable SACS-002 controls loaded as assessment rows.
3. The renewal scheduler runs daily — to test it manually:
   `bench --site <site> execute alphax_grc.notifications.check_aramco_certificate_renewals`

## Email configuration

The renewal/incident emails use Frappe's `frappe.sendmail`. Make sure
SMTP / Mailgun / SES is configured at the site level
(/app/email-domain). Without email config, the functions queue silently
and log to `Error Log`.

## Roadmap (v1.5+)

- Replace SACS-002 placeholder controls with verbatim text once
  licensed PDF is provided
- NCA-conformant Excel print formats (Risk Register, Audit Plan,
  Vulnerability Register, KPI Report)
- Bulk replacement action for CCC controls (CSV / Excel import)
- Snapshot trend history for CCC compliance %

## What's new in v1.4.2

The NCA Templates page (`/app/grc-nca-templates`) is fully redesigned.
Same data, better UX.

**Hero stats strip** — gradient header with live counts: total templates,
breakdown by kind, and (when a client is selected) how many are adopted
by that client.

**Sticky toolbar** — search, client picker, and grid/list view toggle
that stays at the top as you scroll.

**Category chips with icons** — replaces the old dropdown filter.
Horizontally scrollable strip of clickable categories: Governance ⚖️,
Access 🔒, Asset 📦, Network 🌐, Application 🧩, Data 💾, Physical 🏛,
Third Party 🤝, Resilience 🛡️, Incident 🚨, Monitoring 📡,
Vulnerability 🐛, Cryptography 🔐. Active category highlights blue,
shows count badge.

**Card redesign** — bigger cards, category-coloured icon, ECC controls
shown as compact monospace chips (first 4 + "+N" indicator), bilingual
title (EN with AR underneath), hover-lift effect, primary action button
prominent.

**Adoption badges** — when a client is selected, cards already adopted
by that client show a green "✓ Adopted" badge in the top-right and a
green left border. The Adopt button for those cards becomes "✓ Adopted"
disabled. Saves the consultant from accidentally creating duplicates.

**"For this client" side panel** — pinned to the right (collapses below
on mobile). Shows the client name, country, sector, overall NCA library
coverage percentage with progress bar, per-kind breakdown (Policies
12/35, Standards 5/34, etc.), and a "Coverage gap analysis" button.

**Bulk action bar** — slides up from the bottom when you tick checkboxes.
Shows the count, plus "Adopt for client" and "Clear" buttons. Drops the
35-click onboarding into 35-checkboxes-and-one-button.

**Grid / list view toggle** — grid view shows responsive cards, list view
shows full-width rows. Useful when you want to scan many templates fast.

**Bilingual EN ⇄ AR toggle** — menu item that switches the page direction
to RTL and shows Arabic labels everywhere (category names, kind names,
hero text). Template names already had Arabic from v1.4.0; v1.4.2 makes
the chrome around them switch too.

**Mobile-responsive** — under ~900px the side panel moves to the top.
Cards reflow to a single column. The previous layout broke at narrow
widths; this one doesn't.

**Theme-aware** — uses Frappe's CSS variables (`--bg-color`,
`--text-color`, `--text-muted`, `--border-color`, `--card-bg`) so it
follows whatever theme the user has set. Hero gradient stays consistent
because it's intentionally branded.

## Backend additions

One new whitelisted endpoint:

- `alphax_grc...grc_nca_templates.get_client_adoption_status(client)` —
  returns the set of NCA template_codes already adopted by the given
  client. Used by the UI to show ✓ badges on cards and progress in the
  side panel. Best-effort name match between adopted Policy/ISMS records
  and library template_name.

All endpoints from v1.4.1 carry through unchanged: `get_template_library`
(self-healing), `force_seed_libraries`, `bulk_adopt_for_client`,
`get_client_policy_coverage`, `adopt_template_for_client`.

## Compatibility

- All 79 NCA templates from v1.4.0 still seeded (35 policies + 34
  standards + 4 procedures + 6 forms).
- Auto-adopt-on-Client-Profile-save from v1.4.1 still works.
- Self-heal on page load from v1.4.1 still works.
- All v1.3.x live dashboards, multi-tenant, lifecycle, etc. unchanged.

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After upgrade, navigate to `/app/grc-nca-templates`. You should see the
new gradient hero, category chips, and reorganised cards. Pick a client
in the toolbar dropdown to see adoption badges and the side panel
populate.

## What's new in v1.4.1

This release fixes the v1.4.0 "empty NCA library on upgrade" issue and
adds three productivity features for managing multiple policies per client.

**The fix: self-healing NCA Templates page**

In v1.4.0, when upgrading from v1.3.x via `bench migrate`, the new NCA
library doctypes were sometimes synced *after* the bootstrap seeders ran,
causing the seeders to bail (no doctype = no seed) and the NCA Templates
page to show 0/0/0/0 across all four tabs.

v1.4.1 fixes this three ways:
1. When an admin (System Manager / GRC Admin) opens
   `/app/grc-nca-templates`, the page server-side checks whether each
   library is empty and, if so, calls the seeder inline before rendering.
2. A new menu item **"Re-seed NCA library (admin)"** lets admins force a
   re-seed at any time. Idempotent — safe to run repeatedly.
3. A new whitelisted endpoint
   `alphax_grc...grc_nca_templates.force_seed_libraries` exposes the same
   action programmatically.

**New: Bulk adopt selected templates**

Each template card on the NCA Templates page now has a checkbox in the
top-right corner. Tick multiple templates, pick a client in the picker,
then **Menu → "Adopt selected for client…"** creates them all in one
server call. Drops the time to onboard a new client from ~35 clicks to
two checkboxes plus one menu item.

**New: Auto-adopt NCA library on Client Profile save (opt-in)**

`GRC Client Profile` gains 3 new checkboxes in a collapsible
**NCA Library Auto-Adopt** section:
- *Auto-adopt all NCA Policies on save* — creates 35 GRC Policy records
  in Draft status, one per NCA policy template
- *Auto-adopt all NCA Procedures on save* — creates 4 ISMS Document
  Register records for NCA procedures
- *Auto-adopt all NCA Forms on save* — creates 6 ISMS Document Register
  records for NCA forms

Tick the relevant box, save the client, and the system auto-creates
draft records pre-populated from the NCA library. Each checkbox auto-clears
after first use so subsequent saves don't re-trigger. An adoption_status
field shows the result (e.g. "Policy: 35 adopted | Procedure: 4 adopted").

Defaults to **opt-in** (off by default) so consultants stay in control —
turn on for a single client at creation time, leave off for clients
that need a custom subset.

**New: Coverage gap analysis per client**

Menu → **"Coverage gap analysis…"** on the NCA Templates page shows:
- Number of policies adopted for the selected client
- Number of NCA-mapped ECC controls covered
- Number of NCA-mapped ECC controls *not* covered (the gaps)
- Coverage percentage
- Expandable lists of covered and gap controls

Lets the consultant answer the regulator's question *"which ECC controls
do you have a written policy for?"* in one click.

**Confirms: multiple policies per client (this was already supported)**

Just to make this visible in the docs: `GRC Policy` autoname is
`POL-00001`, `POL-00002` and so on. There is no uniqueness constraint
on (client + policy_title) — a single client can have unlimited policies.
The v1.4.1 bulk-adopt and auto-adopt flows make creating many policies
per client effortless.

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
# Or upgrading from v1.4.0:
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After upgrade: open `/app/grc-nca-templates`. If the tabs show 0/0/0/0,
the self-heal will trigger automatically on first load. If for any reason
it doesn't, click Menu → **Re-seed NCA library (admin)**.

## What's new in v1.4.0

This is a major content release. The app now ships with the **complete
NCA Cybersecurity Toolkit** (~80 official Saudi NCA templates) pre-loaded
as a browsable, adoptable library, plus three new domain modules
(Vulnerability Register, KPI Reporting, Threat Catalogue) and significant
NCA-conformance enhancements to existing Risk Register and Audit Plan.

### NCA Cybersecurity Toolkit — full library, browsable & adoptable

Source: https://nca.gov.sa/en/regulatory-documents/guidelines-list/cybersecurity-toolkits/
Last NCA update: 26 November 2025

Four new catalogue doctypes seeded with every official template:
- **GRC NCA Policy Library** — 35 NCA Policy templates (Anti-Malware,
  Cloud, Cryptography, Email, IAM, Network, Patch, Penetration Testing,
  Physical, Risk Management, Vulnerabilities, Web Application, etc.)
- **GRC NCA Standard Library** — 34 NCA Standard templates (Cryptography,
  DLP, EDR, IAM, NDR, OT/ICS, Patch, Privileged Access Workstations,
  Web Application, Wireless, etc.)
- **GRC NCA Procedure Library** — 4 NCA Procedure templates
  (Vulnerability Assessment, Cybersecurity Audit, Document Development,
  Risk Management)
- **GRC NCA Form Library** — 6 NCA Forms / Programs / Reports
  (Confidentiality Agreement, Policy Undertaking, IT Project Checklist,
  Software Development Checklist, Awareness Program, Audit Report)

Every entry carries the official NCA Word + PDF download URLs, mapped
ECC controls, and category. Total: **79 official NCA templates** in
the library.

### NCA Templates Library page — `/app/grc-nca-templates`

Tabbed catalogue browser (Policy / Standard / Procedure / Form). Search
by name, ECC control, or category. Each card shows official Word + PDF
download links plus a one-click **Adopt for client** button: pick a
client, click Adopt, and the app creates a draft `GRC Policy` (or
`GRC ISMS Document Register` for non-policy types) pre-populated from
the NCA template.

This means: when a Saudi regulator asks your client *"show me your IAM
policy / your network security standard / your vulnerability assessment
procedure"*, you can produce one based on the official NCA template
within seconds rather than starting from a blank page.

### GRC Vulnerability — NCA Vulnerability Register

New doctype matching NCA's official Vulnerability Register Excel
template. Fields: vulnerability_id, title (EN+AR), CVE number, CVSS
score, vendor link, affected technology, affected assets, threat
analysis, threat severity (1-5), risk likelihood (1-5), risk severity
(1-5), auto-computed risk_level (Critical/High/Medium/Low/Very Low),
owner, status (Open/In Progress/On Hold/Resolved), first observation
date, due date, resolution date, linked_threat (to Threat Catalogue),
linked asset, linked remediation action.

Risk level auto-computes from severity × likelihood, falls back to
CVSS-based mapping when scores aren't entered. Resolution date
auto-fills when status flips to Resolved.

Five sample vulnerabilities seeded for the DEMO client: Zerologon,
ProxyLogon, Log4Shell, Heartbleed, MOVEit SQL injection — each with
correct CVE, CVSS, and threat-catalogue linkage.

### GRC KPI + Quarterly Measurement — NCA KPI Report

New doctype matching NCA's KPI Report Excel template. Parent fields:
kpi_id, indicator_name (EN+AR), cybersecurity_domain (15 NCA domains),
type, frequency, definition, data_source, owner. Child table for
quarterly measurements: year, Q1-Q4 target/actual/notes plus prior
year Q4 actual.

10 NCA cybersecurity domain KPIs seeded (Asset Management, Business
Continuity, Awareness, Event Monitoring, Compliance, IAM, Network
Security, Physical Security, Risk Management, Vulnerability
Management) each with a year of quarterly target/actual data.

### KPI Dashboard page — `/app/grc-kpi-dashboard`

Quarterly target-vs-actual visualisation per KPI. Cards show domain,
indicator, latest year's quarterly bars (actual fill, target marker,
green when meeting target, amber when below), and full numeric
breakdown. Client picker scopes to one engagement or shows firm-wide.

### GRC Threat Catalogue

Global reference doctype seeded with **all 22 NCA standard threats**:
Credential compromise, Insider threats, Asset compromise, Social
engineering, Data breach, Loss of business continuity, Data loss,
Mistaking compliance for protection, Regulatory fines, Outdated
hardware, Vulnerable software, Cloud vulnerabilities, Ransomware,
Malware, IoT attacks, Operational downtime, DDoS, Underestimation of
risk probability, Partial risk assessment, Improper risk management,
Improper incident response, Third party exposure.

Each threat has EN + AR name, category, description, and is_nca_standard
flag. Risk Register and Vulnerability records can link to threats from
this catalogue.

### Enhanced GRC Risk Register (NCA Risk Register conformance)

Added 9 new fields matching NCA's Risk Register Excel template:
- `risk_cause` — description of the inherent risk's cause
- `threat` — Link to GRC Threat Catalogue
- `risk_analysis_consequences` — possible consequences and timescale
- `date_of_risk_identification`
- `date_of_risk_analysis`
- `last_evaluation_date`
- `inherent_rating_accepted` — risk owner acceptance flow (Yes/No)
- `inherent_rating_override_reason` — text shown when accepted=No
- `manual_rating_override` — rating override when accepted=No

Risk rating options extended from 4 levels to NCA's 6 levels:
Critical, High, Medium, Low, **Very Low**, **N/A**.

### Enhanced GRC Audit Plan (NCA Audit Plan conformance)

Added 11 new fields matching NCA's Audit Plan Excel template:
- `audit_id` — A001/A002 for audits, R001/R002 for reviews
- `audit_or_review` — Audit / Review type
- `lead_auditor` — separate from `audit_owner` (sponsor)
- `team_responsible` — Cybersecurity Org / Internal Audit / Third Party
- `audit_methods` — Inquiry, Inspection, Re-performance
- `criteria` — reference framework / control list
- `sampling` — sampling approach
- `evidence_needed`
- `duration_estimate`
- `schedule_notes`
- `cost`

### Live dashboards extended

`GRC Dashboard Snapshot` gains 6 new fields:
`vulnerabilities_open`, `vulnerabilities_critical`, `vulnerabilities_overdue`,
`vulnerabilities_total`, `kpis_total`, `kpis_on_target`.

`dashboards_live.py` updated to compute these on every snapshot
refresh. The 15-minute cron, the realtime-on-save invalidation, and
the 30s client auto-refresh from v1.3.2 all carry through to the new
fields. Vulnerability and KPI saves trigger snapshot rebuilds via
`doc_events`.

### Workspace refresh

New top-row shortcut tiles: **NCA Templates**, **KPI Dashboard**,
**Vulnerabilities**. New links section entries for all 8 new doctypes
and 2 new pages.

### Migration & data safety

Per the **wipe-and-reseed cleanly** decision:
- Existing data on `neoterminal.k.frappe.cloud` is preserved by the
  Frappe migration (not wiped) but new fields default to NULL.
- All v1.4.0 seed data lands under the **DEMO** client.
- 79 NCA template library entries are global (not client-scoped) and
  read-only for non-admin roles.

If you want a true clean wipe, drop the alphax_grc tables and
reinstall — the `bootstrap_grc` 38 step list is fully resilient and
will re-create everything.

### Compatibility

All v1.3.0–v1.3.2 features carry through unchanged: multi-tenant
Client Profile, lifecycle dashboard, consultant timesheet, NCA ECC
trackers (Document Register, Tool Mapping, Review Calendar), BIA, RCM,
Live Snapshot system.

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
# Or upgrading from v1.3.x:
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
bench restart
```

After install:
1. Open `/app/grc-nca-templates` to browse the 79-template NCA library.
2. Open `/app/grc-kpi-dashboard` to see quarterly KPI charts.
3. Open `/app/grc-vulnerability` (List view) — 5 sample vulnerabilities pre-loaded.
4. Live dashboards now include vulnerability counts in the snapshot.

## Roadmap (v1.5+)

- NCA-conformant Excel print formats (export Risk Register, Audit Plan,
  Vulnerability Register, KPI Report in NCA's exact Excel layouts).
- UAE controls fully built out (TDRA, DIFC, ADGM, DHA detail).
- Bahrain, Qatar, Kuwait, Oman framework controls.
- Snapshot trend history (compliance score over 90 days).

## What's new in v1.3.2

Dashboards are now **always live** — no more snapshot-until-reload.
Three layers of liveness, all working together:

**Layer 1 — Materialized snapshot table** (`GRC Dashboard Snapshot`)
A scheduler job runs every 15 minutes and pre-computes 16 KPIs plus 7
JSON detail blobs (heatmap, top risks, frameworks, KRIs, severities,
findings, ratings) for every active client. Dashboards read from this
single row instead of running 12+ aggregation queries per page load.
A firm-wide read merges the snapshots across clients in Python.
- Source: `alphax_grc/dashboards_live.py:refresh_all_snapshots`
- Cron: `*/15 * * * *` via `hooks.py:scheduler_events`

**Layer 2 — Realtime push on data changes** (Frappe WebSocket bus)
When a Risk, Finding, KRI, Assessment, Control, Asset, Incident,
Remediation, Framework, Exception, Risk Acceptance, Maturity Assessment,
Vendor, Vendor Assessment, or Consultant Timesheet record is saved,
`invalidate_dashboards()` immediately:
1. Recomputes the snapshot for that client (cheap — one client only).
2. Broadcasts `grc.dashboard.refresh` over `frappe.realtime`.
Every open dashboard for that client (or firm-wide) re-fetches within
~1 second of the save. No polling needed for typical interactive use.

**Layer 3 — 30-second auto-refresh** (client-side timer, fallback)
Every dashboard page wires up `frappe.alphaxGRC.live({...})` which polls
every 30 seconds — but pauses when the browser tab is hidden, so we
don't burn server cycles for tabs no one's looking at. Also doubles as
the heartbeat that keeps the "Live · updated Xs ago" indicator fresh.

**Live status indicator**
Every dashboard now shows a small pill in the page header:
`● Live · updated 14s ago` (green when fresh, amber after 60s, red on
error). Tooltip shows the exact snapshot timestamp. There's also a
manual "Refresh now" button for impatient users.

**Cleanup**
- Removed hardcoded fallback constants from `grc_command_center.js`
  (`'68%'` compliance, `'4'` critical, `'7'` findings, `'3'` overdue,
  fake heatmap pattern). When the database returns nothing, dashboards
  now show `0` or `—` instead of fake numbers.
- Risk Dashboard's framework section now derives compliance score
  correctly (carried over from v1.3.1).

**Schema**
One new doctype:
- `GRC Dashboard Snapshot` — one row per client, autoname = client code.
  Read-only to non-admin roles. Auto-created on first install for the
  DEMO client; refreshed every 15 minutes thereafter.

**API surface (whitelisted)**
- `alphax_grc.dashboards_live.get_live_dashboard(client=None)` — main
  read endpoint; returns the snapshot or computes inline if missing.
- `alphax_grc.dashboards_live.force_refresh(client=None)` — manual
  recompute, bypasses staleness check.

**Compatibility**
- All v1.3.0 doctypes (Client Profile, Consultant Timesheet, NCA ECC
  trackers, BIA, RCM) carry through unchanged.
- All v1.3.1 fixes (compliance_score derivation) carry through.
- Multi-tenant model unchanged.
- Existing dashboards (Command Centre, Risk Dashboard, Lifecycle) all
  rewired to the live system; existing endpoints still work but are now
  routed through the snapshot layer where applicable.

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
# OR upgrade from v1.3.x:
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
```

After install, the bootstrap will:
1. Create the `GRC Dashboard Snapshot` doctype.
2. Compute the first snapshot for every active client (DEMO + any you've
   created), so dashboards show data immediately.
3. The 15-minute cron schedule activates automatically.

## How to verify it's working

1. Open `/app/grc-lifecycle` or `/app/grc-risk-dashboard`. You should
   see a "● Live · updated Xs ago" pill in the page header.
2. Open `/app/grc-risk-register`, create a new risk, save.
3. Switch back to the dashboard tab — it should refresh within ~1 second
   without you clicking anything. The new risk should appear in the
   counts and heatmap.
4. If realtime isn't working (rare — usually a websocket config issue),
   the 30-second timer takes over as fallback.

## Roadmap (v1.4+)

- UAE controls fully built out (TDRA, DIFC, ADGM, DHA detail)
- Bahrain, Qatar, Kuwait, Oman framework controls
- Snapshot history table for trending ("compliance score over 90 days")
- Engagement profitability dashboard

## What's new in v1.3.1

**Bug fix: Risk Dashboard crash with `Unknown column 'compliance_score'`**

The Risk Dashboard's `get_risk_dashboard_data` endpoint and the Client
Profile's `_refresh_summary` method were querying `compliance_score` from
`GRC Framework`, but that column never existed on the Framework doctype.
The code was inherited from v1.2.3 and went unnoticed because the path
was only hit when a user opened the Risk Dashboard with at least one
GRC Framework record present.

`compliance_score` actually lives on `GRC Assessment`, not `GRC Framework`
(also on `GRC Board Report`, `GRC NCA ECC Control`, `GRC Vendor Assessment`,
and `GRC Client Profile` — all correctly).

Fix: both endpoints now derive a framework's compliance score by averaging
the `compliance_score` of GRC Assessment records linked to each framework
— the same approach `api.py:get_command_center_data` already uses.

A schema-mismatch sweep was also run across `api.py`, `notifications.py`,
and all page Python files; no other field references are misaligned with
their target doctype schemas.

No other changes from v1.3.0. Multi-tenant Client Profile, Lifecycle
dashboard, Consultant Timesheet, NCA ECC trackers, BIA, RCM all carry
through unchanged.

## What's new in v1.3.0

This is a major release. The app moves from single-tenant to **multi-client
consulting platform**: every record is now scoped to a client engagement,
country and sector intelligence drives framework selection, and the new
Lifecycle dashboard is the central UI.

**Multi-tenant architecture**
- New `GRC Client Profile` doctype — central tenant record. Holds the
  client name (EN+AR), country, sector, engagement type and dates, lead
  consultant, applicable frameworks, default hourly rate.
- Country + sector → applicable frameworks intelligence: KSA Government
  loads NCA ECC, NCA CSCC, PDPL, NCA Data Cybersecurity, SDAIA AI Ethics;
  KSA Banking loads SAMA CSF, SAMA CTI, PDPL; Aramco supply chain loads
  TPCSP and SACS-002; etc. Picking country and sector on a new Client
  Profile auto-suggests the right framework set.
- 34 existing doctypes plumbed with a `client` Link field: Risk Register,
  Audit Finding, Control, KRI, Framework, Asset Inventory, Incident,
  Vendor, etc. Every record is now scoped to a client engagement.
- Country coverage in v1.3.0:
  - 🇸🇦 **Saudi Arabia** — fully built (Government, Banking, Aramco
    Supply Chain, Healthcare, Energy & Utilities, Telecom, Education,
    General Private)
  - 🇦🇪 **UAE** — scaffolded (Government/TDRA, Banking/DIFC/ADGM/DFSA,
    Healthcare/DHA/DoH)
  - 🇧🇭 🇶🇦 🇰🇼 🇴🇲 🇪🇬 🇯🇴 — framework names listed; deeper content
    planned for v1.4

**Lifecycle dashboard** — `/app/grc-lifecycle`
- 8-stage process cycle visualisation: Setup → Register → Assess →
  Control → Audit → Remediate → Report → Review (loops back to setup)
- Client picker at the top; pick a client to scope the wheel to that
  engagement. Pick "Firm-wide overview" to see roll-ups across all clients
- Each stage shows live progress percentage and red/amber/green status
  based on completion vs total
- Clickable stages deep-link into the relevant module
- KPI tiles, framework pills, sortable stage list

**Consultant time-tracking**
- New `GRC Consultant Timesheet` doctype: client + consultant + date +
  hours + billable + activity type + linked module + reference document
  + auto-computed amount from client hourly rate
- 14 activity types: Risk Assessment, Framework Assessment, Audit
  Fieldwork, Finding Review, Remediation Support, Document Review,
  Policy Drafting, Workshop / Training, Client Meeting, Report Writing,
  Project Management, Research, Travel, Other
- API endpoints: `get_client_hours_summary` (per-client roll-up),
  `get_my_timesheet_summary` (current user's weekly view)

**NCA ECC compliance trackers** (from Axidian NCA ECC Compliance Guide)
- `GRC NCA ECC Document` — 28 mandatory documents (1-1-1 Cybersecurity
  Strategy, 1-2-3 Steering Committee Charter, etc.). Status workflow:
  To Do / In Progress / Awaiting Approval / Approved / Needs Review.
  EN + AR titles. Evidence attachment, approval authority, review cycle.
- `GRC NCA ECC Tool Mapping` — 28 tooling-required ECC controls mapped
  to recommended solution categories (GRC, IAM, PAM, DLP, SIEM, MDM,
  NGFW, MFA, etc.). Coverage status per control.
- `GRC NCA ECC Review Calendar` — 29 periodic review cycles with
  frequency, next-scheduled date, last-review results, evidence
  attachment. Auto-flags overdue.

**Business Impact Analysis** (BIA infographic methodology)
- `GRC Business Impact Analysis` doctype with full BIA dimensions:
  RTO, RPO, MTPD, dependencies child table (5 dependency types),
  5 impact dimensions (Financial, Operational, Regulatory, Reputational,
  Customer) on a 1-5 severity scale
- 5 sample BIA records seeded: Customer-facing online services,
  Financial close & reporting, Payroll processing, IT operations &
  service desk, Regulatory reporting

**Risk Control Matrix** (PMO-Government template)
- `GRC Risk Control Matrix` doctype with `GRC RCM Line` child rows:
  domain, risk, impact, control, control type
  (Preventive/Detective/Corrective), owner, frequency, KPI
- 11 RCM domains: Strategic Alignment, Project Governance, Portfolio
  Management, Budget & Financial Control, Risk Management, Compliance
  & Regulatory, Vendor & Contract, Performance Reporting, Change
  Management, Benefits Realization
- Sample PMO-Government RCM seeded with 6 lines

**Migration & data safety**
- Per the "wipe-and-reseed cleanly" decision: this release auto-creates
  a **DEMO** client on first install, then backfills `client = DEMO`
  on any existing seeded data so nothing is orphaned. Real engagement
  data should be created under fresh Client Profile records.
- All existing v1.2.x fixes carry through: workspace `content` populated,
  empty `grc_pages.json` shipped, resilient `bootstrap_grc`, all 17
  whitelisted endpoints permission-gated.

**Workspace refresh**
- New shortcuts: Lifecycle, Clients, Timesheets
- New links section: GRC Client Profile, Consultant Timesheet, all 5
  new NCA ECC / BIA / RCM doctypes
- Updated `content` layout puts Lifecycle as the primary entry point

## Install / Upgrade

```bash
bench get-app alphax_grc <url-of-this-zip>
bench --site neoterminal.k.frappe.cloud install-app alphax_grc
# OR for upgrade from v1.2.5:
bench --site neoterminal.k.frappe.cloud migrate
bench --site neoterminal.k.frappe.cloud clear-cache
```

After install, navigate to `/app/grc-lifecycle` to see the new dashboard.
The DEMO client comes pre-loaded with sample NCA ECC documents, tool
mappings, review calendar, BIA records and the PMO-Government RCM.

To create a real engagement, click "+ New Client" from the Lifecycle
dashboard, pick country and sector, and the app will suggest the right
framework bundle automatically.

## Roadmap (v1.4+)

- UAE controls fully built out (TDRA, DIFC, ADGM, DHA detail)
- Bahrain, Qatar, Kuwait, Oman framework controls
- Cross-client benchmark dashboards (compare your KSA Banking clients
  against each other)
- Engagement profitability dashboard (timesheet hours × rate vs fixed-fee
  contract value)
- Rename `owner` field on `GRC Audit Finding` (collides with Frappe's
  reserved column) — held because it's a destructive migration

## What was claimed for v1.2.x (kept for history)

**Actual fix for the workspace `onboarding_list` crash on Frappe v15.106+**

v1.2.4 attempted to fix this by changing the `onboarding` field, but that
field was unrelated. The real cause is a NULL `content` field on the
Workspace document.

In `frappe/desk/desktop.py` (Frappe v15), `Workspace.__init__` only assigns
`self.onboarding_list = [...]` inside an `if self.doc.content:` branch.
If `content` is NULL, the attribute is never created — and the later
`if self.onboarding_list:` in `get_onboardings()` raises
`AttributeError: 'Workspace' object has no attribute 'onboarding_list'`.

Two-part fix:
- The shipped workspace JSON now includes a populated `content` field with
  a default layout (welcome header, 8 shortcut tiles, 9 module cards).
- `ensure_workspace()` self-heals existing installs whose DB row was
  created without `content` — on `bench migrate` it injects the default
  layout if the field is NULL or empty.

If you previously installed v1.2.3 or v1.2.4, upgrading to v1.2.5 and
running `bench migrate` will repair the workspace automatically and the
crash will stop on next page load.

No other changes. Risk Dashboard, theme presets, permission gates, report
fixes, KRI breach-direction, resilient `bootstrap_grc`, all carry over.

## What was claimed for v1.2.4 (incorrect — kept for history)

**Frappe v15.106+ workspace fix**
Fixes `AttributeError: 'Workspace' object has no attribute 'onboarding_list'`
that prevented the AlphaX GRC workspace from loading on Frappe v15.106 and
later. Root cause is a Frappe core bug where an empty-string `onboarding`
field on a Workspace document skips initialization of `onboarding_list`,
which `get_onboardings()` then references.
See https://github.com/frappe/erpnext/issues/43234

Two-part fix:
- Workspace JSON now ships with `"onboarding": null` instead of `""` so
  fresh installs avoid the broken Frappe code branch entirely.
- `ensure_workspace()` now self-heals existing installs: on `bench migrate`
  it detects an empty-string `onboarding` value in the Workspace row and
  rewrites it to NULL.

No other changes — Risk Dashboard, permission gates, report fixes, KRI
breach-direction, and all v1.2.3 features carry over unchanged.

## What's new in v1.2.3

**New page: GRC Risk Dashboard** (`/app/grc-risk-dashboard`)
A live, theme-able risk dashboard with:
- 4 KPI tiles (critical risks, open findings, avg compliance score, overdue actions)
- 5×5 risk heatmap driven by `GRC Risk Register.impact` × `likelihood`
- Top open risks table with deep-link to each risk
- Framework compliance progress bars (reads `GRC Framework.compliance_score`)
- KRI status panel (reads `GRC KRI` with live status badges)
- Findings-by-severity breakdown (reads `GRC Audit Finding`)
- Interactive theme panel: 5 presets (AlphaX Navy / Saudi Green / Corporate Blue / Dark Mode / Sand & Gold) + individual colour pickers for global, risk-level and heatmap-cell colours
- **Per-user theme persistence** via `frappe.defaults` — each user keeps their own colour preferences
- Bilingual (EN/AR) labels via Frappe's `__()`
- All text content passed through `frappe.utils.escape_html` (no XSS risk from risk titles, KRI names, framework names, etc.)

Workspace includes a new "Risk Dashboard" shortcut tile (red) and a link in the "Dashboards & Pages" group.

Access is gated via the existing role list (System Manager / GRC Admin / GRC Executive / Compliance Officer / GRC Assessor / GRC Auditor / Risk Owner / Privacy Officer).

## What's new in v1.2.2

**Install reliability**
- Ships an empty `fixtures/grc_pages.json` to overwrite any legacy
  `standard:Yes` Page records that triggered "Not in Developer Mode"
  on Frappe Cloud during `bench install-app`.
- `before_install` runs a defensive `neutralize_legacy_page_fixtures()` pass
  that rewrites stale fixture files to `[]` for re-install / migrate scenarios.

**Bug fixes (script reports)**
- `grc_risk_summary` rewritten to use the actual schema fields
  (`inherent_score`, `residual_score`, `risk_rating`, `linked_framework`,
  `next_review_date`).
- `grc_audit_findings_report` rewritten with correct columns
  (`owner`, `due_date`, `root_cause`) plus a computed `days_open`.
- `grc_compliance_status` rewritten with a real `JOIN` against
  `tabGRC Framework` for friendly framework names.

**Security hardening**
- New role-based gate `_require_grc_role()` covering all 17 whitelisted
  endpoints in `api.py`, the page controllers, and the ITGC seeder method.
- `start_assessment_run` no longer uses `ignore_permissions=True`; it now
  calls `frappe.has_permission("GRC Assessment Run", "create")`.
- `get_assessment_summary` checks per-document read permission.
- KRI alert email HTML is now `frappe.utils.escape_html`-escaped.

**Data model**
- `GRC KRI` gains a `breach_direction` field (`Above` / `Below`) so KRIs like
  patch-SLA-met-% breach when the value falls below the threshold instead of
  above it. Default `Above` preserves existing behaviour.
- `risk_rating` added to `GRC Risk Register.field_order` so it actually
  renders in the form.

**Notifications**
- `_admin_emails()` no longer returns the literal string `"Administrator"`
  when no GRC Admin role users exist; falls back to the real Administrator
  user email or `[]`.
- `check_kri_breaches()` honours `breach_direction` and reports it in the
  alert table.

**Cleanup**
- Removed ~380 lines of dead v1 seeder code
  (`seed_nca_ecc_controls`, `seed_asset_inventory`, `seed_nca_ecc_controls_full`).
  Bootstrap calls only the `_v2` versions.
- Version stamps unified to 1.2.2 across `__init__.py`, `hooks.py`, install logs.

## Install

```bash
bench get-app alphax_grc <git-or-zip-url>
bench --site <your-site> install-app alphax_grc
```

If a previous install partially completed and left a stale
`apps/alphax_grc/alphax_grc/fixtures/grc_pages.json` on disk, this version
will overwrite it during `bench update`. If you're stuck on a different
app version and can't update yet, the manual one-liner is:

```bash
echo '[]' > apps/alphax_grc/alphax_grc/fixtures/grc_pages.json
bench --site <your-site> install-app alphax_grc
```

## What's still on the roadmap

- Rename the `owner` field on `GRC Audit Finding` (collides with Frappe's
  reserved `owner` system column). Requires a migration patch on existing
  sites — held for v1.3.
- Flesh out the stub manuals under `manuals/`.

Licence: MIT
