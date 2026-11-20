"""CohortPilot — independent, fictional enterprise learning PM case study.
Run: streamlit run app.py
"""
from __future__ import annotations

import csv
import io
import json
import os
from datetime import date

import streamlit as st

from core import (add_activity, client_update, extract_requirements, missing_questions,
                  next_id, pm_brief, project_health, seed_data, validate_import)

st.set_page_config(page_title="CohortPilot | Project Delivery Workspace", page_icon="🧭",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
/* CohortPilot accessible, consistent LIGHT appearance across all pages. */
:root { color-scheme: light; }
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
  background: #F8FAFD !important; color: #17263D !important;
}
[data-testid="stHeader"] { background: #F8FAFD !important; }
.block-container { padding-top: 1.65rem; max-width: 1440px; }
h1,h2,h3,h4,h5,h6 { letter-spacing:-.025em; color:#17263D !important; }
h1 { font-weight:750 !important; }
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] div[data-testid="stMarkdownContainer"] {
  color: #243650;
}
[data-testid="stSidebar"] {
  background: #EAF0F8 !important;
  border-right:1px solid #D5DEEA;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
  color: #20334E !important;
}
[data-testid="stSidebar"] .stButton button {width:100%;}
[data-testid="stSidebar"] [role="radiogroup"] label {
  padding: .2rem .3rem; border-radius: .4rem;
}
[data-testid="stMetric"] {
  background:#FFFFFF !important; border:1px solid #DAE3EF;
  border-radius:14px; padding:15px 18px;
  box-shadow:0 3px 14px rgba(20,45,80,.04);
}
[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"] {
  color: #17263D !important;
}
[data-testid="stMetric"] [data-testid="stMetricDelta"] { color:#496078 !important; }
[data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stExpander"] {
  border-color: #D9E2ED;
}
[data-testid="stExpander"] details, [data-testid="stExpander"] summary {
  color: #17263D !important;
}
[data-testid="stExpander"] summary:hover { background:#F0F4FA; }
[data-testid="stTabs"] [role="tab"] { color:#405574 !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color:#2445BA !important; border-bottom-color:#3154CB !important;
}
[data-testid="stWidgetLabel"] p {color:#243650 !important;font-weight:550;}
/* Form widgets and dropdown content must be readable regardless of OS dark mode. */
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="select"] input,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] > div,
[data-baseweb="popover"] [role="option"],
[data-testid="stDateInput"] input {
  background:#FFFFFF !important; color:#17263D !important;
}
[data-baseweb="select"] svg { fill:#425774 !important; }
input::placeholder, textarea::placeholder {color:#65758D !important; opacity:1;}
.stButton > button[kind="primary"] {
  background:#3154CB !important; border-color:#3154CB !important;
  color:#FFFFFF !important; font-weight:650;
}
.stButton > button[kind="primary"] p {color:#FFFFFF !important;}
.stButton > button[kind="secondary"],
.stDownloadButton > button {
  background:#FFFFFF !important; color:#213D72 !important;
  border-color:#CBD8EA !important;
}
.stButton > button[kind="secondary"] p,
.stDownloadButton > button p {color:#213D72 !important;}
[data-testid="stAlert"] {border-radius:12px;}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {background:#FFFFFF;}
.note {
  padding:14px 16px;border-radius:12px;background:#EAF0FF;
  border:1px solid #C6D6FF; color:#213D70 !important;
}
.note b {color:#172F63 !important;}
.soft {color:#51627A !important;font-size:.96rem;line-height:1.55;}
.pill {display:inline-block;border:1px solid #D1DCEC;border-radius:100px;
  padding:3px 10px;font-size:.8rem;color:#3C526D !important;}
@media(max-width:780px) {
  .block-container {padding:1rem .85rem 2rem;}
  h1 {font-size:1.7rem !important;}
  [data-testid="stMetric"] {padding:11px 12px;}
}
</style>
""", unsafe_allow_html=True)

PAGES = ["Portfolio", "Overview", "Requirements", "Delivery Plan", "Stakeholders",
         "Risks & Decisions", "PM Copilot", "Activity Log", "Data & Export"]
STATUSES = ["Not started", "In progress", "Blocked", "Done"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]
REQ_STATUSES = ["Needs validation", "Pending approval", "Approved", "Rejected"]
RISK_STATUSES = ["Open", "Mitigating", "Closed"]

if "workspace" not in st.session_state:
    st.session_state.workspace = seed_data()
if "active_id" not in st.session_state:
    st.session_state.active_id = st.session_state.workspace["projects"][0]["id"]
if "page" not in st.session_state:
    st.session_state.page = "Portfolio"


def current_project() -> dict:
    for p in st.session_state.workspace["projects"]:
        if p["id"] == st.session_state.active_id:
            return p
    st.session_state.active_id = st.session_state.workspace["projects"][0]["id"]
    return st.session_state.workspace["projects"][0]


def goto(page: str, project_id: str | None = None) -> None:
    if project_id:
        st.session_state.active_id = project_id
    st.session_state.page = page
    st.rerun()


def header(title: str, eyebrow: str = "PROJECT DELIVERY WORKSPACE", subtitle: str = "") -> None:
    st.caption(eyebrow)
    st.title(title)
    if subtitle:
        st.markdown(f"<p class='soft'>{subtitle}</p>", unsafe_allow_html=True)


def csv_bytes(items: list[dict]) -> bytes:
    if not items:
        return b""
    keys = list(dict.fromkeys(k for row in items for k in row.keys()))
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=keys)
    writer.writeheader()
    writer.writerows({k: ", ".join(str(i) for i in v) if isinstance(v, list) else v
                      for k, v in item.items()} for item in items)
    return buffer.getvalue().encode("utf-8-sig")


def valid_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


def badge_text(p: dict, asof: date) -> str:
    h = project_health(p, asof)
    return f"{h['status']} · {h['completion']}% complete"


def get_api_key() -> str:
    if os.getenv("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        return ""


with st.sidebar:
    st.markdown("## 🧭 CohortPilot")
    st.caption("Project Consultant · portfolio case study")
    projects = st.session_state.workspace["projects"]
    options = {f"{p['id']} · {p['name']}": p["id"] for p in projects}
    selected_label = st.selectbox("Active programme", list(options),
                                  index=list(options.values()).index(st.session_state.active_id))
    if options[selected_label] != st.session_state.active_id:
        st.session_state.active_id = options[selected_label]
        st.rerun()
    chosen_page = st.radio("Navigate", PAGES, index=PAGES.index(st.session_state.page), label_visibility="collapsed")
    if chosen_page != st.session_state.page:
        st.session_state.page = chosen_page
        st.rerun()
    st.divider()
    as_of = st.date_input("Scenario reporting date", value=date(2026, 12, 10),
                          help="This is a fictional reporting date used to assess overdue work; it does not claim to be today's date.")
    st.caption("⚑ Sample data are fictional. The date above is a demo control.")
    st.divider()
    st.caption("Prototype storage: your current browser session. Export JSON to keep a copy.")

p = current_project()
h = project_health(p, as_of)

if st.session_state.page == "Portfolio":
    header("Your programme portfolio", subtitle="One home for client requirements, project execution and reporting. Interactive demo · fictional data.")
    st.markdown("<div class='note'>💡 <b>Case-study goal:</b> demonstrate a consultant's workflow from client discovery → validated requirements → task ownership → delivery monitoring → human-reviewed reporting.</div>", unsafe_allow_html=True)
    st.write("")
    cols = st.columns(3)
    for i, proj in enumerate(st.session_state.workspace["projects"]):
        with cols[i % 3]:
            with st.container(border=True):
                st.caption(proj["id"])
                st.subheader(proj["name"])
                st.caption(proj["client"])
                st.write(f"**{proj['participants']} participants** · {proj['cohorts']} cohorts")
                st.write(f"Budget: **₹{proj['budget']:,}**")
                st.progress(project_health(proj, as_of)["completion"] / 100,
                            text=badge_text(proj, as_of))
                st.caption(f"End date: {proj['end']}")
                if st.button("Open workspace", key=f"open_{proj['id']}", type="primary", use_container_width=True):
                    goto("Overview", proj["id"])
    st.subheader("What a recruiter can explore")
    st.markdown("**Traceability:** link each client requirement to delivery actions.  \\n"
                "**Governance:** document approvals, stakeholder owners, RAID risks and decisions.  \\n"
                "**Execution:** update work and watch the dashboard respond.  \\n"
                "**Reporting:** generate a fact-grounded brief and editable client email.")

elif st.session_state.page == "Overview":
    header(p["name"], eyebrow=f"{p['id']}  /  PROGRAMME OVERVIEW",
           subtitle=f"{p['client']}  ·  {p['participants']} participants across {p['cohorts']} cohorts  ·  {p['duration']}  ·  {p['start']} to {p['end']}")
    st.info(f"**Status: {h['status']}** · assessed against the simulated reporting date {as_of.isoformat()}.")
    cols = st.columns(5)
    with cols[0]: st.metric("Tasks complete", f"{h['completion']}%", f"{h['completed_tasks']} / {h['task_count']}", delta_color="off")
    with cols[1]: st.metric("Budget left", f"₹{int(h['budget_remaining']):,}")
    with cols[2]: st.metric("Blocked", len(h["blocked"]))
    with cols[3]: st.metric("Overdue", len(h["overdue"]))
    with cols[4]: st.metric("Pending approvals", len(h["pending"]))
    st.write("")
    left, right = st.columns([1.45, 1])
    with left:
        st.subheader("Delivery workstreams")
        for t in sorted(p["tasks"], key=lambda x: x["due"]):
            a, b, c = st.columns([4, 1.7, 2])
            with a:
                st.write(f"**{t['id']} · {t['title']}**")
                st.caption(f"Owner: {t['owner']} · Due: {t['due']}")
            with b: st.progress(int(t["progress"]) / 100, text=f"{t['progress']}%")
            with c:
                new_status = st.selectbox("Status", STATUSES, index=valid_index(STATUSES, t["status"]),
                                          key=f"ov_status_{p['id']}_{t['id']}", label_visibility="collapsed")
                if new_status != t["status"]:
                    old = t["status"]
                    t["status"] = new_status
                    if new_status == "Done": t["progress"] = 100
                    add_activity(p, f"Task {t['id']} moved from {old} to {new_status}")
                    st.rerun()
            st.divider()
        if st.button("Edit delivery plan", use_container_width=True):
            goto("Delivery Plan")
    with right:
        st.subheader("Needs your attention")
        issues = ([f"⛔ {t['id']}: {t['title']} — blocked" for t in h["blocked"]]
                  + [f"⏳ {t['id']}: overdue since {t['due']}" for t in h["overdue"]]
                  + [f"✍️ {r['id']}: awaiting approval" for r in h["pending"]]
                  + [f"⚠️ {r['id']}: risk score {r['likelihood']*r['impact']}/25" for r in h["high_risks"]])
        if not issues: st.success("No open alerts from the current tracker.")
        else:
            for item in list(dict.fromkeys(issues))[:8]: st.warning(item)
        st.subheader("Project snapshot")
        st.write(f"**Budget utilisation:** ₹{int(p['spent']):,} / ₹{int(p['budget']):,}")
        st.progress(min(float(p["spent"]) / max(float(p["budget"]), 1), 1))
        st.write(f"**Cohort plan:** {p['cohorts']} cohorts · approximately {p['participants']//max(1,p['cohorts'])} people each")
        nxt = h["next_task"]
        st.write(f"**Next open milestone:** {nxt['id']} · {nxt['title']} ({nxt['due']})" if nxt else "All tracked tasks complete")
        st.caption("Cohort progress is tracked through linked delivery tasks, not invented attendance figures.")
        with st.form("edit_budget"):
            new_spent = st.number_input("Update recorded spend (₹)", min_value=0.0, value=float(p["spent"]), step=5000.0)
            if st.form_submit_button("Save budget update"):
                old = p["spent"]
                p["spent"] = new_spent
                add_activity(p, f"Recorded spend changed from ₹{old:,.0f} to ₹{new_spent:,.0f}")
                st.rerun()
        st.subheader("Latest changes")
        for event in p["activity"][:4]:
            st.caption(f"{event['when']} · {event['description']}")

elif st.session_state.page == "Requirements":
    header("Client requirements & traceability", subtitle="Capture client input, validate each requirement, and connect it to delivery work. Nothing is approved automatically.")
    a, b = st.columns([1.1, 1])
    with a:
        st.subheader("Discovery notes")
        notes = st.text_area("Paste meeting notes or a client brief", value=p.get("notes", ""), height=180,
                             key=f"notes_{p['id']}")
        if st.button("Extract draft requirements", type="primary"):
            p["notes"] = notes
            st.session_state[f"drafts_{p['id']}"] = extract_requirements(notes)
            add_activity(p, "Discovery notes reviewed with rule-based draft extraction")
            st.success("Drafts extracted for review — not added or approved yet.")
    with b:
        st.subheader("Clarifications to request")
        questions = missing_questions(notes)
        if questions:
            for item in questions: st.warning(item)
        else:
            st.success("No default discovery-question gaps detected. Human review still required.")
        st.caption("Extraction uses transparent pattern rules, not a generative AI model.")
    drafts_key = f"drafts_{p['id']}"
    drafts = st.session_state.get(drafts_key, [])
    if drafts:
        st.subheader(f"Drafts awaiting your validation ({len(drafts)})")
        for ix, draft in enumerate(list(drafts)):
            with st.expander(f"Draft {ix+1}: {draft['text']}"):
                with st.form(f"draft_form_{p['id']}_{ix}"):
                    text = st.text_input("Client requirement", value=draft["text"])
                    cat = st.text_input("Category", value=draft["category"])
                    criteria = st.text_input("Acceptance criteria", value=draft["criteria"])
                    owner = st.text_input("Accountable owner", value=draft["owner"])
                    priority = st.selectbox("Priority", PRIORITIES, index=valid_index(PRIORITIES, draft["priority"]))
                    submit = st.form_submit_button("Approve & add to register", type="primary")
                    if submit:
                        if not text.strip() or not criteria.strip():
                            st.error("Description and measurable acceptance criteria are required.")
                        else:
                            rid = next_id(p["requirements"], "REQ-")
                            p["requirements"].append(dict(id=rid, text=text, category=cat,
                                                           criteria=criteria, owner=owner, priority=priority,
                                                           status="Approved"))
                            drafts.pop(ix)
                            st.session_state[drafts_key] = drafts
                            add_activity(p, f"Approved and added {rid}: {text}")
                            st.rerun()
                if st.button("Discard draft", key=f"discard_{p['id']}_{ix}"):
                    drafts.pop(ix)
                    st.session_state[drafts_key] = drafts
                    st.rerun()
    st.subheader("Requirements register")
    with st.expander("➕ Add requirement manually"):
        with st.form(f"add_req_{p['id']}"):
            text = st.text_input("Requirement statement")
            cat = st.selectbox("Category", ["Audience", "Format", "Approval", "Success metric", "Budget", "Communication", "Scheduling", "Other"])
            criteria = st.text_input("Measurable acceptance criteria")
            owner = st.text_input("Accountable stakeholder")
            priority = st.selectbox("Priority", PRIORITIES, index=1)
            if st.form_submit_button("Add as needs validation"):
                if not text.strip() or not criteria.strip():
                    st.error("Requirement and acceptance criteria are required.")
                else:
                    rid = next_id(p["requirements"], "REQ-")
                    p["requirements"].append(dict(id=rid, text=text, category=cat, criteria=criteria,
                                                  owner=owner, priority=priority, status="Needs validation"))
                    add_activity(p, f"Added requirement {rid} for validation")
                    st.rerun()
    for r in p["requirements"]:
        linked = [t["id"] for t in p["tasks"] if r["id"] in t.get("requirements", [])]
        with st.expander(f"{r['id']} · {r['text']} · {r['status']} · {len(linked)} linked task(s)"):
            st.caption(f"Linked deliverables: {', '.join(linked) or 'None — add a link in Delivery Plan'}")
            with st.form(f"edit_req_{p['id']}_{r['id']}"):
                new_text = st.text_input("Statement", value=r["text"])
                new_criteria = st.text_input("Acceptance criteria", value=r["criteria"])
                c1,c2,c3 = st.columns(3)
                with c1: new_owner = st.text_input("Owner", value=r["owner"])
                with c2: new_priority = st.selectbox("Priority", PRIORITIES, index=valid_index(PRIORITIES, r["priority"]))
                with c3: new_status = st.selectbox("Approval status", REQ_STATUSES, index=valid_index(REQ_STATUSES, r["status"]))
                if st.form_submit_button("Save requirement"):
                    if not new_text.strip() or not new_criteria.strip():
                        st.error("Statement and criteria cannot be blank.")
                    else:
                        r.update(text=new_text, criteria=new_criteria, owner=new_owner,
                                 priority=new_priority, status=new_status)
                        add_activity(p, f"Updated requirement {r['id']} (status: {new_status})")
                        st.rerun()
    st.caption("Traceability is two-way: select requirements on each task, then return here to see the linked task IDs.")

elif st.session_state.page == "Delivery Plan":
    header("Delivery plan & milestones", subtitle="Work breakdown, owners, deadlines, dependencies and linked client requirements.")
    with st.expander("➕ Add a delivery task"):
        with st.form(f"add_task_{p['id']}"):
            title = st.text_input("Task / work package name")
            col1, col2, col3 = st.columns(3)
            with col1: owner = st.text_input("Responsible owner")
            with col2: due = st.date_input("Due date", value=date(2026, 12, 18))
            with col3: priority = st.selectbox("Priority", PRIORITIES, index=1)
            linked = st.multiselect("Linked client requirements", [r["id"] for r in p["requirements"]])
            dependency = st.text_input("Dependencies (task IDs / approvals)")
            if st.form_submit_button("Create task", type="primary"):
                if not title.strip() or not owner.strip():
                    st.error("Task title and owner are required.")
                else:
                    tid = next_id(p["tasks"], "T-")
                    p["tasks"].append(dict(id=tid, title=title, owner=owner, due=due.isoformat(),
                                           status="Not started", progress=0, requirements=linked,
                                           priority=priority, dependency=dependency))
                    add_activity(p, f"Created task {tid}: {title}")
                    st.rerun()
    for t in sorted(p["tasks"], key=lambda x: x["due"]):
        late = t["status"] != "Done" and date.fromisoformat(t["due"]) < as_of
        with st.expander(f"{'⛔' if t['status']=='Blocked' else '⏳' if late else '✅' if t['status']=='Done' else '◻️'} {t['id']} · {t['title']}   |   {t['status']}   |   {t['due']}"):
            with st.form(f"task_{p['id']}_{t['id']}"):
                title = st.text_input("Task name", value=t["title"])
                a,b,c = st.columns(3)
                with a: owner = st.text_input("Owner", value=t["owner"])
                with b: due = st.date_input("Due date", value=date.fromisoformat(t["due"]))
                with c: status = st.selectbox("Status", STATUSES, index=valid_index(STATUSES, t["status"]))
                d,e = st.columns(2)
                with d: progress = st.slider("Progress %", 0, 100, int(t["progress"]), step=5)
                with e: priority = st.selectbox("Priority", PRIORITIES, index=valid_index(PRIORITIES, t["priority"]))
                linked = st.multiselect("Requirements fulfilled / supported by this task",
                                        [r["id"] for r in p["requirements"]], default=t["requirements"])
                dep = st.text_input("Dependencies", value=t.get("dependency", ""))
                if st.form_submit_button("Save task changes"):
                    if not title.strip() or not owner.strip():
                        st.error("Task and owner are required.")
                    else:
                        t.update(title=title, owner=owner, due=due.isoformat(), status=status,
                                 progress=100 if status == "Done" else progress,
                                 priority=priority, requirements=linked, dependency=dep)
                        add_activity(p, f"Updated task {t['id']} · status {status}; linked {', '.join(linked) or 'none'}")
                        st.rerun()
    st.caption("Tasks marked Done contribute to the completion percentage. Partial task progress is separately recorded and displayed.")

elif st.session_state.page == "Stakeholders":
    header("Stakeholders & governance", subtitle="Clarify who owns decisions, who executes work, and who needs updates.")
    for i, person in enumerate(p["stakeholders"]):
        with st.expander(f"{person['name']} · {person['role']} · {person['side']}"):
            with st.form(f"person_{p['id']}_{i}"):
                a,b,c = st.columns(3)
                with a: name = st.text_input("Name or role placeholder", value=person["name"])
                with b: role = st.text_input("Role", value=person["role"])
                with c: influence = st.selectbox("Influence", ["High", "Medium", "Low"], index=valid_index(["High","Medium","Low"],person["influence"]))
                cadence = st.text_input("Communication cadence", value=person["cadence"])
                engagement = st.text_input("Engagement / current ask", value=person["engagement"])
                if st.form_submit_button("Save stakeholder"):
                    person.update(name=name, role=role, influence=influence, cadence=cadence, engagement=engagement)
                    add_activity(p, f"Updated stakeholder: {name}")
                    st.rerun()
    with st.expander("➕ Add stakeholder"):
        with st.form(f"new_person_{p['id']}"):
            name = st.text_input("Stakeholder name / placeholder")
            role = st.text_input("Role")
            side = st.selectbox("Organisation", ["Client", "Internal", "Partner"])
            if st.form_submit_button("Add stakeholder"):
                if name.strip():
                    p["stakeholders"].append(dict(name=name, role=role, side=side, influence="Medium",
                                                  cadence="To confirm", engagement="To confirm", contact="Not provided"))
                    add_activity(p, f"Added stakeholder {name}")
                    st.rerun()
                else: st.error("Name or role placeholder required.")
    st.subheader("RACI matrix")
    st.caption("R: Responsible · A: Accountable · C: Consulted · I: Informed. Edit below and save.")
    matrix = st.data_editor(p["raci"], num_rows="dynamic", hide_index=True, use_container_width=True,
                            key=f"raci_{p['id']}")
    if st.button("Save RACI matrix"):
        p["raci"] = matrix
        add_activity(p, "Updated RACI responsibilities")
        st.success("RACI matrix saved for this session.")

elif st.session_state.page == "Risks & Decisions":
    header("Risks, issues & decision log", subtitle="Rate delivery risk on a 1–5 likelihood × 1–5 impact scale; record mitigations and accountable owners.")
    with st.expander("➕ Register a new risk"):
        with st.form(f"add_risk_{p['id']}"):
            title = st.text_input("Risk / issue statement")
            a,b,c = st.columns(3)
            with a: likelihood = st.slider("Likelihood", 1, 5, 3)
            with b: impact = st.slider("Impact", 1, 5, 4)
            with c: owner = st.text_input("Risk owner")
            mitigation = st.text_area("Mitigation / response")
            if st.form_submit_button("Add risk"):
                if title.strip():
                    rid = next_id(p["risks"], "RISK-")
                    p["risks"].append(dict(id=rid, title=title, likelihood=likelihood, impact=impact,
                                           mitigation=mitigation, owner=owner, status="Open"))
                    add_activity(p, f"Registered {rid}: {title}")
                    st.rerun()
                else: st.error("Provide a risk title.")
    for risk in p["risks"]:
        score = risk["likelihood"] * risk["impact"]
        with st.expander(f"{risk['id']} · {risk['title']} · score {score}/25 · {risk['status']}"):
            with st.form(f"edit_risk_{p['id']}_{risk['id']}"):
                title = st.text_input("Risk", value=risk["title"])
                a,b,c = st.columns(3)
                with a: likelihood = st.slider("Likelihood", 1, 5, int(risk["likelihood"]))
                with b: impact = st.slider("Impact", 1, 5, int(risk["impact"]))
                with c: status = st.selectbox("Status", RISK_STATUSES, index=valid_index(RISK_STATUSES, risk["status"]))
                owner = st.text_input("Owner", value=risk["owner"])
                mitigation = st.text_area("Mitigation", value=risk["mitigation"])
                if st.form_submit_button("Save risk"):
                    risk.update(title=title, likelihood=likelihood, impact=impact, status=status,
                                owner=owner, mitigation=mitigation)
                    add_activity(p, f"Updated {risk['id']} · score {likelihood * impact}/25 · {status}")
                    st.rerun()
    st.subheader("Decision log")
    for d in p["decisions"]:
        st.markdown(f"**{d['date']} · {d['decision']}**")
        st.caption(f"Owner: {d['owner']} · Rationale: {d['rationale']}")
    with st.expander("➕ Log a decision"):
        with st.form(f"add_decision_{p['id']}"):
            decision = st.text_area("Decision taken or proposed")
            owner = st.text_input("Decision owner")
            rationale = st.text_area("Trade-off / rationale")
            if st.form_submit_button("Log decision"):
                if decision.strip():
                    p["decisions"].insert(0, dict(date=as_of.isoformat(), decision=decision,
                                                  owner=owner, rationale=rationale))
                    add_activity(p, f"Logged decision: {decision[:80]}")
                    st.rerun()
                else: st.error("A decision description is required.")

elif st.session_state.page == "PM Copilot":
    header("PM Copilot", subtitle="A human-in-control assistant for project health, blockers and stakeholder communication.")
    st.markdown("<div class='note'><b>How it works:</b> The two generators below are rules-based and use the project's live records. They are not powered by an LLM. Optional genuine AI analysis is available only when you configure an OpenAI API key. Review every suggestion before acting.</div>", unsafe_allow_html=True)
    st.write("")
    tab1,tab2,tab3 = st.tabs(["Project health brief", "Client status email", "Optional AI analysis"])
    with tab1:
        if st.button("Refresh health brief", type="primary"):
            st.session_state[f"brief_editor_{p['id']}"] = pm_brief(p, as_of)
        brief = st.text_area("Editable PM summary", value=pm_brief(p, as_of),
                             height=440, key=f"brief_editor_{p['id']}")
        st.download_button("Download brief (.txt)", brief, file_name="cohortpilot_health_brief.txt", mime="text/plain")
    with tab2:
        if st.button("Regenerate client draft", type="primary"):
            st.session_state[f"client_draft_{p['id']}"] = client_update(p, as_of)
        draft = st.text_area("Editable draft — confirm before sending", value=client_update(p, as_of),
                             height=430, key=f"client_draft_{p['id']}")
        st.download_button("Download client draft (.txt)", draft, file_name="cohortpilot_client_update.txt", mime="text/plain")
    with tab3:
        key = get_api_key()
        if not key:
            st.info("Optional live AI is not configured. To enable: put OPENAI_API_KEY in Streamlit secrets (or environment). The rest of CohortPilot works without it.")
        else:
            st.warning("Live AI uses a paid external API. This sends the selected project's records to OpenAI; do not include real confidential client information.")
            if st.button("Ask AI for an evidence-grounded intervention plan", type="primary"):
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=key, timeout=25)
                    snapshot = {k: p[k] for k in ("name", "client", "requirements", "tasks", "risks", "decisions", "budget", "spent")}
                    answer = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a cautious project-management co-pilot. Use ONLY the supplied project records. Do not invent deadlines, approvals, data, names, or outcomes. Flag missing evidence. Give 3-5 actionable prioritised recommendations with exact task/requirement IDs and owners where present. All actions require human approval."},
                            {"role": "user", "content": f"Scenario reporting date: {as_of.isoformat()}\nData: {json.dumps(snapshot, ensure_ascii=False)}"},
                        ], temperature=0.2,
                    )
                    st.session_state[f"ai_{p['id']}"] = answer.choices[0].message.content or "No output received."
                except Exception as exc:
                    st.error(f"AI request failed ({type(exc).__name__}). Check your key, network and API billing settings.")
            if st.session_state.get(f"ai_{p['id']}"):
                st.markdown(st.session_state[f"ai_{p['id']}"])
    st.caption("AI does not automatically approve client requirements, modify the delivery plan or send communications.")

elif st.session_state.page == "Activity Log":
    header("Activity log", subtitle="An audit-style log of edits made in this demo session.")
    for event in p["activity"]:
        st.write(f"**{event['when']}**  ·  {event['description']}")
    st.caption("This log is a prototype convenience, not a tamper-proof enterprise audit trail.")

elif st.session_state.page == "Data & Export":
    header("Data, export & backups", subtitle="Bring your project data back later by downloading JSON and re-uploading it in a new session.")
    st.warning("This MVP stores edits only in the current Streamlit session. Refreshes/server restarts or Cloud redeploys may lose changes. Export a JSON backup before closing.")
    backup = json.dumps(st.session_state.workspace, ensure_ascii=False, indent=2)
    st.download_button("Download entire portfolio (.json)", backup, file_name="cohortpilot_portfolio.json",
                       mime="application/json", type="primary")
    a,b = st.columns(2)
    with a:
        st.download_button("Export current tasks (.csv)", csv_bytes(p["tasks"]), file_name="tasks.csv", mime="text/csv")
    with b:
        st.download_button("Export current requirements (.csv)", csv_bytes(p["requirements"]), file_name="requirements.csv", mime="text/csv")
    st.subheader("Import saved workspace")
    uploaded = st.file_uploader("Upload a CohortPilot JSON backup", type=["json"])
    if uploaded is not None and st.button("Restore workspace from file"):
        try:
            payload = json.load(uploaded)
            if not validate_import(payload):
                st.error("File is not a valid CohortPilot portfolio backup.")
            else:
                st.session_state.workspace = payload
                st.session_state.active_id = payload["projects"][0]["id"]
                st.success("Backup restored.")
                st.rerun()
        except (ValueError, UnicodeDecodeError):
            st.error("Invalid JSON file.")
    st.subheader("Reset sample demo")
    confirm = st.checkbox("I understand this will discard my unsaved edits")
    if st.button("Reset demo", disabled=not confirm):
        st.session_state.workspace = seed_data()
        st.session_state.active_id = "PRJ-001"
        for k in list(st.session_state.keys()):
            if k.startswith(("drafts_", "notes_", "brief_", "brief_editor_", "update_", "client_draft_", "ai_", "raci_", "ov_status_")):
                del st.session_state[k]
        goto("Portfolio")

st.divider()
st.caption("CohortPilot · Independent PGDM portfolio case study · All clients, stakeholders, budgets, timelines and results are illustrative. Not an official Enparadigm system.")
