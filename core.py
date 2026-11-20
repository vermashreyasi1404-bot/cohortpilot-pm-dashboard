"""Pure business rules for CohortPilot. No Streamlit dependency."""
from __future__ import annotations

import copy
import re
from datetime import date, datetime
from typing import Any


def _req(rid: str, text: str, category: str, criteria: str, owner: str, priority: str = "High", status: str = "Approved") -> dict:
    return dict(id=rid, text=text, category=category, criteria=criteria, owner=owner,
                priority=priority, status=status)


def _task(tid: str, title: str, owner: str, due: str, status: str, progress: int,
          requirements: list[str], priority: str = "High", dependency: str = "") -> dict:
    return dict(id=tid, title=title, owner=owner, due=due, status=status,
                progress=progress, requirements=requirements, priority=priority,
                dependency=dependency)


def seed_data() -> dict:
    """Realistic but entirely fictional portfolios and project records."""
    primary = {
        "id": "PRJ-001", "name": "Leadership Excellence Programme", "client": "Asteria Retail (fictional)",
        "owner": "Shreyasi (demo PM)", "participants": 100, "cohorts": 4,
        "duration": "12 weeks", "start": "2026-11-23", "end": "2027-02-12",
        "budget": 800000, "spent": 275000,
        "objective": "Equip 100 people managers with practical leadership and coaching capabilities.",
        "notes": "Client: Asteria Retail. 100 managers from sales, merchandising and operations in 4 batches of 25. 12-week leadership excellence programme. Mix of live virtual learning and one in-person capstone per cohort. Client HR lead must approve content by Dec 4. Budget cap ₹8 lakh. 90% attendance target, feedback ≥4.3/5. Regional managers available after 2pm weekdays. Send weekly status report each Friday.",
        "requirements": [
            _req("REQ-001", "Train 100 managers in four cohorts of 25", "Audience", "Roster shows 4 cohorts of 25 participants", "Client L&D lead"),
            _req("REQ-002", "Blend live virtual sessions with an in-person capstone per cohort", "Format", "Delivery plan includes both formats for each cohort", "Programme manager"),
            _req("REQ-003", "Obtain client approval of content by Dec 4", "Approval", "Written client HR sign-off recorded by 2026-12-04", "Client HR lead", status="Pending approval"),
            _req("REQ-004", "Achieve at least 90% attendance", "Success metric", "Attendance report shows 90% or more", "Operations coordinator"),
            _req("REQ-005", "Achieve feedback score of at least 4.3 / 5", "Success metric", "Post-programme average feedback ≥4.3/5", "Programme manager", status="Pending approval"),
            _req("REQ-006", "Send weekly client status updates each Friday", "Communication", "Friday project update shared and logged", "Programme manager", priority="Medium"),
            _req("REQ-007", "Remain within ₹8,00,000 delivery budget", "Budget", "Actual expenditure at closure ≤₹8,00,000", "Programme manager"),
        ],
        "tasks": [
            _task("T-001", "Confirm scope and kickoff with client", "Shreyasi", "2026-11-24", "Done", 100, ["REQ-001", "REQ-002"]),
            _task("T-002", "Finalise module design and obtain HR sign-off", "Content lead", "2026-12-04", "Blocked", 70, ["REQ-002", "REQ-003"], dependency="Client HR approval"),
            _task("T-003", "Confirm facilitator availability", "Delivery coordinator", "2026-12-08", "In progress", 80, ["REQ-002"]),
            _task("T-004", "Validate four cohort rosters", "Client L&D lead", "2026-12-05", "Done", 100, ["REQ-001", "REQ-004"]),
            _task("T-005", "Run platform and classroom readiness checks", "Operations coordinator", "2026-12-11", "In progress", 55, ["REQ-002"]),
            _task("T-006", "Deliver cohort 1 live sessions", "Lead facilitator", "2026-12-18", "Not started", 0, ["REQ-001", "REQ-002", "REQ-004"], dependency="T-002, T-005"),
            _task("T-007", "Deliver cohorts 2–4 learning sessions", "Lead facilitator", "2027-01-22", "Not started", 0, ["REQ-001", "REQ-002", "REQ-004"], dependency="T-006"),
            _task("T-008", "Complete in-person cohort capstones", "Programme manager", "2027-02-02", "Not started", 0, ["REQ-002"]),
            _task("T-009", "Collect attendance and feedback evidence", "Operations coordinator", "2027-02-08", "Not started", 0, ["REQ-004", "REQ-005"]),
            _task("T-010", "Submit final outcomes and financial closure report", "Shreyasi", "2027-02-12", "Not started", 0, ["REQ-005", "REQ-006", "REQ-007"], dependency="T-009"),
        ],
        "stakeholders": [
            dict(name="Client HR sponsor", role="Executive sponsor", side="Client", influence="High", cadence="Biweekly steering review", engagement="Needs content sign-off", contact="Not provided"),
            dict(name="Client L&D lead", role="Requirement owner", side="Client", influence="High", cadence="Twice-weekly check-in", engagement="Cohort roster confirmed", contact="Not provided"),
            dict(name="Programme manager", role="Delivery accountable", side="Internal", influence="High", cadence="Daily stand-up", engagement="Monitoring all workstreams", contact="Not provided"),
            dict(name="Content lead", role="Learning designer", side="Internal", influence="Medium", cadence="Twice-weekly", engagement="Waiting for approval", contact="Not provided"),
            dict(name="Lead facilitator", role="Training delivery", side="Partner", influence="Medium", cadence="Weekly", engagement="Availability to confirm", contact="Not provided"),
            dict(name="Operations coordinator", role="Logistics and reporting", side="Internal", influence="Medium", cadence="Daily", engagement="Platform checks underway", contact="Not provided"),
        ],
        "risks": [
            dict(id="RISK-001", title="HR sign-off slips beyond December 4", likelihood=4, impact=5,
                 owner="Programme manager", mitigation="Escalate approval; present reduced-scope fallback for client decision", status="Open"),
            dict(id="RISK-002", title="Facilitator unavailable for a scheduled cohort", likelihood=3, impact=4,
                 owner="Delivery coordinator", mitigation="Confirm backup facilitator and handover material", status="Mitigating"),
            dict(id="RISK-003", title="Attendance falls below the 90% target", likelihood=3, impact=4,
                 owner="Client L&D lead", mitigation="Confirm manager schedules and send reminder cadence", status="Open"),
        ],
        "decisions": [
            dict(date="2026-12-09", decision="Escalate the content approval blocker; do not start cohort delivery without client sign-off.",
                 owner="Programme manager", rationale="Protect learning quality and avoid unapproved scope."),
        ],
        "raci": [
            dict(deliverable="Programme scope", responsible="Programme manager", accountable="Client HR sponsor", consulted="Client L&D lead", informed="Facilitators"),
            dict(deliverable="Content approval", responsible="Content lead", accountable="Client HR sponsor", consulted="Programme manager", informed="Operations"),
            dict(deliverable="Cohort scheduling", responsible="Operations coordinator", accountable="Programme manager", consulted="Client L&D lead", informed="Facilitators"),
            dict(deliverable="Outcome report", responsible="Programme manager", accountable="Client HR sponsor", consulted="Operations coordinator", informed="Client L&D lead"),
        ],
        "activity": [{"when": "2026-12-10 09:00", "description": "Sample scenario loaded · fictional project records"}],
    }

    def other(pid: str, name: str, client: str, people: int, budget: int, due: str) -> dict:
        q = copy.deepcopy(primary)
        q.update(id=pid, name=name, client=client, participants=people, cohorts=2,
                 budget=budget, spent=int(budget * 0.19), end=due,
                 objective="Deliver a measurable skills programme for a fictional client.",
                 notes="", requirements=[_req("REQ-001", f"Deliver programme to {people} participants", "Audience",
                                              f"Validated roster of {people} participants", "Client L&D lead")],
                 tasks=[_task("T-001", "Confirm client needs and scope", "Programme manager", "2026-12-07", "Done", 100, ["REQ-001"]),
                        _task("T-002", "Prepare delivery and facilitator plan", "Delivery coordinator", "2026-12-20", "In progress", 40, ["REQ-001"]),
                        _task("T-003", "Deliver programme and document outcomes", "Lead facilitator", due, "Not started", 0, ["REQ-001"])],
                 risks=[], decisions=[], activity=[{"when": "2026-12-10 09:00", "description": "Sample scenario loaded"}])
        return q

    return {"projects": [primary,
                         other("PRJ-002", "Frontline Coaching Sprint", "Northstar Services (fictional)", 60, 450000, "2027-01-30"),
                         other("PRJ-003", "Digital Sales Enablement", "Meridian Consumer (fictional)", 80, 600000, "2027-02-18")],
            "version": 1}


def project_health(project: dict, as_of: date) -> dict:
    tasks = project.get("tasks", [])
    complete = [t for t in tasks if t.get("status") == "Done"]
    blocked = [t for t in tasks if t.get("status") == "Blocked"]
    overdue = [t for t in tasks if t.get("status") != "Done" and t.get("due") and date.fromisoformat(t["due"]) < as_of]
    pending = [r for r in project.get("requirements", []) if r.get("status") != "Approved"]
    high_risks = [r for r in project.get("risks", []) if r.get("status") != "Closed" and int(r.get("likelihood", 1)) * int(r.get("impact", 1)) >= 12]
    spent, budget = float(project.get("spent", 0)), float(project.get("budget", 0))
    next_tasks = sorted([t for t in tasks if t.get("status") != "Done"], key=lambda t: t.get("due") or "9999-12-31")
    attention = bool(blocked or overdue or high_risks or pending or spent > budget)
    return {
        "completion": round(100 * len(complete) / len(tasks)) if tasks else 0,
        "completed_tasks": len(complete), "task_count": len(tasks), "blocked": blocked, "overdue": overdue,
        "pending": pending, "high_risks": high_risks, "budget_remaining": budget - spent,
        "status": "Needs attention" if attention else "On track", "next_task": next_tasks[0] if next_tasks else None,
    }


def extract_requirements(notes: str) -> list[dict]:
    """Transparent rule-based extraction; never interpret this as an LLM."""
    text = (notes or "").strip()
    if not text:
        return []
    lower = text.lower()
    out = []

    def add(description: str, category: str, criteria: str, priority: str = "High"):
        if not any(i["text"].lower() == description.lower() for i in out):
            out.append(dict(text=description, category=category, criteria=criteria, owner="Confirm with client",
                            priority=priority, status="Needs validation"))

    match = re.search(r"\b(\d{1,4})\s+(?:managers|participants|employees|leaders)\b", lower)
    groups = re.search(r"\b(\d{1,2})\s+(?:cohorts|batches|groups)\b", lower)
    if match:
        n = match.group(1)
        qualifier = f" across {groups.group(1)} cohorts" if groups else ""
        add(f"Deliver programme to {n} participants{qualifier}", "Audience", f"Approved participant roster includes {n} people{qualifier}")
    if "virtual" in lower or "online" in lower:
        add("Include live virtual learning sessions", "Format", "Virtual sessions appear in approved delivery plan")
    if "in-person" in lower or "in person" in lower or "capstone" in lower:
        add("Include in-person learning/capstone component", "Format", "An in-person activity is documented in the delivery plan")
    signoff = re.search(r"\b(?:approve|approval|sign.off)\b[^.\n]{0,65}", lower)
    if signoff:
        add("Obtain client approval of learning content before delivery", "Approval", "Client approval is logged", "High")
    attendance = re.search(r"\b(\d{2,3})\s*%\s*attendance", lower)
    if attendance:
        add(f"Reach at least {attendance.group(1)}% attendance", "Success metric", f"Final attendance >= {attendance.group(1)}%")
    rating = re.search(r"\b(\d(?:\.\d+)?)\s*/\s*5\b", lower)
    if rating:
        add(f"Achieve feedback score of at least {rating.group(1)}/5", "Success metric", f"Final survey average >= {rating.group(1)}/5")
    budget = re.search(r"(?:₹|rs\.?\s*)([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|crore)?", lower)
    if budget:
        value = float(budget.group(1).replace(",", ""))
        multiplier = 10000000 if budget.group(2) == "crore" else 100000 if budget.group(2) in {"lakh", "lakhs", "lac", "lacs"} else 1
        inr = round(value * multiplier)
        add(f"Keep programme spend within ₹{inr:,.0f}", "Budget", f"Recorded expenditure <= ₹{inr:,.0f}")
    if "weekly" in lower and ("report" in lower or "update" in lower):
        day = " each Friday" if "friday" in lower else ""
        add(f"Share weekly status updates{day}", "Communication", "Weekly update is prepared and shared", "Medium")
    if "after 2pm" in lower or "after 2 pm" in lower:
        add("Schedule manager-facing sessions after 2 PM", "Scheduling", "Session timetable starts no earlier than 2 PM")
    if not out:
        add("Review and clarify the client's supplied notes", "Discovery", "Client-validated requirement documented")
    return out


def missing_questions(notes: str) -> list[str]:
    lower = (notes or "").lower()
    q = [("facilitator", "How many facilitators are available, and who is the backup?"),
         ("venue", "What are the venue requirements and who books the space?"),
         ("escalation", "Who is the client's escalation owner for blocked approvals?")]
    return [question for trigger, question in q if trigger not in lower]


def pm_brief(project: dict, as_of: date) -> str:
    h = project_health(project, as_of)
    lines = [f"PROJECT HEALTH BRIEF | {project['name']}",
             f"Scenario reporting date: {as_of.isoformat()} | Status: {h['status']}",
             f"Client: {project['client']}",
             f"Progress: {h['completed_tasks']}/{h['task_count']} tasks complete ({h['completion']}%).",
             f"Budget: ₹{int(project.get('spent', 0)):,} spent of ₹{int(project.get('budget', 0)):,}; remaining ₹{int(h['budget_remaining']):,}.",
             f"Alerts: {len(h['blocked'])} blocked, {len(h['overdue'])} overdue, {len(h['pending'])} unapproved requirements, {len(h['high_risks'])} high risks.", ""]
    if h["blocked"]:
        lines.append("BLOCKERS:")
        lines.extend(f"• {t['id']} {t['title']} — owner: {t['owner']}; due {t['due']}" for t in h["blocked"])
    if h["overdue"]:
        lines.append("OVERDUE WORK:")
        lines.extend(f"• {t['id']} {t['title']} — due {t['due']}" for t in h["overdue"])
    if h["pending"]:
        lines.append("CLIENT VALIDATION REQUIRED:")
        lines.extend(f"• {r['id']} {r['text']} ({r['status']})" for r in h["pending"])
    if h["high_risks"]:
        lines.append("HIGH RISKS:")
        lines.extend(f"• {r['id']} {r['title']} — score {r['likelihood'] * r['impact']}/25; owner: {r['owner']}" for r in h["high_risks"])
    lines.append("NEXT ACTIONS (PM TO CONFIRM):")
    actions = []
    if h["blocked"]:
        t = h["blocked"][0]
        actions.append(f"Discuss resolution and escalation with {t['owner']} for {t['id']}.")
    if h["pending"]:
        actions.append(f"Seek validation/approval from {h['pending'][0]['owner']} for {h['pending'][0]['id']}.")
    if h["overdue"]:
        actions.append(f"Replan {h['overdue'][0]['id']} with owner {h['overdue'][0]['owner']} and agree a revised date.")
    if not actions and h["next_task"]:
        actions.append(f"Check readiness for next milestone {h['next_task']['id']} due {h['next_task']['due']}.")
    lines.extend(f"{n}. {a}" for n, a in enumerate(actions or ["Confirm current delivery plan with stakeholders."], 1))
    lines.append("\nNote: Generated from editable fictional project records, not independently verified delivery evidence.")
    return "\n".join(lines)


def client_update(project: dict, as_of: date) -> str:
    h = project_health(project, as_of)
    overdue = ", ".join(t["id"] for t in h["overdue"]) or "None recorded"
    blocked = ", ".join(t["id"] for t in h["blocked"]) or "None recorded"
    next_task = h["next_task"]
    upcoming = f"{next_task['id']} — {next_task['title']} (due {next_task['due']})" if next_task else "All tasks currently completed"
    asks = "; ".join(r["id"] + " (" + r["text"] + ")" for r in h["pending"]) or "No pending requirements approval in the register"
    return (f"Subject: {project['name']} | Delivery status as of {as_of.isoformat()}\n\n"
            f"Hello team,\n\nHere is the current programme update based on our delivery tracker.\n\n"
            f"Overall status: {h['status']}. {h['completed_tasks']} of {h['task_count']} tracked tasks completed ({h['completion']}%).\n"
            f"Work requiring attention: blocked tasks — {blocked}; overdue tasks — {overdue}.\n"
            f"Next planned milestone: {upcoming}.\n"
            f"Approvals / decisions requested: {asks}.\n"
            f"Budget recorded: ₹{int(project['spent']):,} of ₹{int(project['budget']):,} allocated.\n\n"
            f"Please review the open items and confirm owners and recovery actions.\n\nRegards,\nProgramme Manager\n\n"
            f"[Draft only — verify accuracy and approve before sending to the client.]")


def validate_import(payload: Any) -> bool:
    if not isinstance(payload, dict) or not isinstance(payload.get("projects"), list) or not payload["projects"]:
        return False
    required = {"id", "name", "client", "tasks", "requirements", "stakeholders", "risks", "decisions", "activity"}
    return all(isinstance(p, dict) and required.issubset(p) and
               all(isinstance(p[key], list) for key in ("tasks", "requirements", "stakeholders", "risks", "decisions", "activity"))
               for p in payload["projects"])


def next_id(items: list[dict], prefix: str) -> str:
    nums = [int(item["id"].split("-")[-1]) for item in items if re.fullmatch(re.escape(prefix) + r"\d+", item.get("id", ""))]
    return f"{prefix}{max(nums, default=0) + 1:03d}"


def add_activity(project: dict, description: str) -> None:
    project.setdefault("activity", []).insert(0, dict(when=datetime.now().strftime("%Y-%m-%d %H:%M"), description=description))
