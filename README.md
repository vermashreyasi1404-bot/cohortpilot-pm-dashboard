# CohortPilot — AI-Assisted Project Delivery Workspace

**Portfolio case study (ongoing)** · Python + Streamlit · *Fictional sample data*

CohortPilot is an interactive Streamlit dashboard built to demonstrate practical project-consulting workflows for an enterprise learning program serving **100 managers across 4 cohorts**, with an illustrative **₹8,00,000 budget**. It is an independent project, not an official product of or commissioned project for Enparadigm or any other company.

## Functionality

- Portfolio of three fictional programs and an editable program workspace.
- Meeting-note-to-requirement draft extraction (currently **rules-based**); explicit human approval and requirement-to-task traceability.
- Editable delivery work packages, task ownership, deadlines, dependencies, budgets and project health.
- Stakeholder mapping and RACI matrix.
- Risk register, likelihood × impact scoring, and decision log.
- PM health briefs and editable client status updates generated from current project data.
- Optional API-enabled LLM intervention suggestions (requires your own API key, separate billing, and permission to send non-sensitive data to OpenAI).
- JSON workspace backup/restore and CSV exports.

## Run on your computer

Use Python 3.11+ (recommended) in your terminal:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Upload to GitHub and deploy to Streamlit Community Cloud

1. Visit https://github.com/new, create a public repository named `cohortpilot-pm-dashboard`. Do not upload private/client information; all included case-study data is fictional.
2. On the empty repository, click **uploading an existing file** (or **Add file → Upload files**). **Extract the ZIP first.** Upload the *contents* of this folder into the repo root (not the ZIP and not an extra enclosing folder): `app.py`, `core.py`, `requirements.txt`, `README.md`, `.gitignore`, `tests/` and `.streamlit/`.
3. Commit the files to the main branch. GitHub must show **`app.py` and `requirements.txt` at repository root**.
4. Visit https://share.streamlit.io/ and sign in with GitHub. Select **Create app** / **Deploy an app from GitHub**.
5. Choose repository `YOUR_GITHUB_USERNAME/cohortpilot-pm-dashboard`, branch `main`, entrypoint `app.py` (not `core.py`). Select an available Python 3.11+ runtime in Advanced settings if asked.
6. Select **Deploy**. Community Cloud will install the requirements and start your dashboard. The published link usually ends in `.streamlit.app`.
7. Optional AI: open the deployed app's settings → **Secrets**, enter `OPENAI_API_KEY = "..."` there. Never commit real secrets into GitHub. Live API usage may cost money.

You can update the app later by editing your GitHub repo and committing the changes; Community Cloud generally redeploys when the tracked branch changes.

## Important data persistence limitation

This version stores edits in **Streamlit `st.session_state`**, not a durable server-side database. Interactivity works during an active session, but refreshes, disconnections, browser session changes, redeploys or server restarts may reset it. To preserve changes, open **Data & Export → Download entire portfolio (.json)**, and use **Restore workspace from file** on your next visit. For a permanent multi-user PM dashboard, add user authentication and database-backed persistence (e.g., Supabase or another managed database) in a later iteration. Avoid assuming that a local SQLite file on Community Cloud is reliable long-term persistent storage.

## Run built-in logic checks

```bash
python -m unittest discover -s tests -v
```

These check the pure-Python business rules. They do **not** replace UI testing in a real browser or deployed Streamlit environment.

## 2-minute recruiter demo

1. Portfolio → select **Leadership Excellence Programme**.
2. Requirements → paste the simulated client notes; extract, edit, and approve a draft.
3. Delivery Plan → link a requirement to a task and update its status.
4. Overview → show the calculated project health change.
5. PM Copilot → regenerate the brief and discuss your next actions and human approval controls.

**Project status:** Ongoing independent portfolio prototype. All sample clients, schedules, numbers, and results are illustrative.
