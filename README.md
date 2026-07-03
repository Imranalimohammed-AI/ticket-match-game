# Cotiviti IT Ticket Triage Challenge

An interactive game that teaches staff how to correctly classify IT support tickets into the three ITSM categories:
**Incident**, **Generic Service Request**, and **Service Catalog Request**.

---

## Project Structure

```
ticket-match-game/
├── cotiviti_ticket_match.py      # Desktop triage game (Tkinter)
├── cotiviti_bubble_explorer.py   # Bubble explorer desktop app (Tkinter)
├── cotiviti_bubble_explorer.html # Bubble explorer — single-file, browser-based (share with all users)
├── web/
│   ├── app.py                    # Flask web server
│   ├── setup_admin.py            # One-time admin password setup
│   ├── requirements.txt
│   ├── .env                      # Secret keys (not committed)
│   ├── cotiviti_game.sqlite      # Player results database (not committed)
│   └── templates/
│       ├── game.html             # Web game UI
│       ├── dashboard.html        # Admin stats dashboard
│       └── login.html            # Admin login page
```

---

## Web Game (Flask)

### First-time setup

**1. Create and activate the virtual environment**

```powershell
cd AI-Vibecoding
.\.venv\Scripts\Activate.ps1
```

**2. Install dependencies**

```powershell
uv pip install flask python-dotenv
```

**3. Set the admin password (run once)**

```powershell
cd ticket-match-game\web
& c:\Users\Imranali.Mohammed\AI-Vibecoding\.venv\Scripts\python.exe setup_admin.py
```

Follow the prompts. This writes `ADMIN_PASSWORD_HASH` and `SECRET_KEY` to `.env`.

**4. Start the server**

```powershell
cd ticket-match-game\web
& c:\Users\Imranali.Mohammed\AI-Vibecoding\.venv\Scripts\python.exe app.py
```

### URLs

| Page | URL |
|---|---|
| Game (public) | http://192.168.0.116:5000/ |
| Admin Login | http://192.168.0.116:5000/admin/login |
| Admin Dashboard | http://192.168.0.116:5000/admin/dashboard |

The game is accessible to anyone on your local network via the `192.168.0.116` address.

---

## Desktop App — Ticket Triage (Tkinter)

```powershell
cd AI-Vibecoding
.\.venv\Scripts\Activate.ps1
& .\.venv\Scripts\python.exe ticket-match-game\cotiviti_ticket_match.py
```

---

## Bubble Explorer

An animated, educational tool that teaches staff which Cotiviti Service Portal items are **Service Catalog** items versus **Incident** or **Generic Service Request**. All 15 portal items from the screenshot float as 3-D bubbles. Click any bubble to reveal its type, a formal explanation, and a brief description.

### Browser version (recommended for sharing)

`cotiviti_bubble_explorer.html` is a **single self-contained file** — no server, no install, no internet required.

**How to share with all Cotiviti end users:**

| Method | Steps |
|---|---|
| **SharePoint** | Upload the `.html` file → right-click → Share → Copy link (set to *People in Cotiviti*) |
| **Teams** | Attach the file in any channel → members click to open in their browser |
| **Email** | Attach the `.html` file directly — recipients double-click to open |
| **Intranet** | Ask IT to drop the file in a web root folder and share the URL |

### Desktop version (Tkinter)

```powershell
cd AI-Vibecoding
.\.venv\Scripts\Activate.ps1
& .\.venv\Scripts\python.exe ticket-match-game\cotiviti_bubble_explorer.py
```

### How the Bubble Explorer works

- 15 animated 3-D bubbles float around the screen, one per Service Portal item.
- Hover over a bubble for a glow and perspective tilt effect.
- Click any bubble to reveal whether it is a **Service Catalog item** (✓) or **not** (✗).
- **Report An Incident Or Outage** and **Generic Service Request** display *"Not a Catalog item"* — all others confirm as Service Catalog items.
- A stamp appears on each discovered bubble; the bottom panel shows the full explanation.
- Discover all 15 to unlock the completion summary with key rules.

---

## How the Triage Game Works

- Players enter their name and email, then are shown IT scenarios one at a time.
- Each scenario must be dragged/clicked into the correct ticket bucket.
- **Scoring:** 10 base points per correct answer + streak bonus (×2 per streak level).
- A **flawless bonus** of +10 is awarded for getting all 9 scenarios correct.
- Maximum score: **100 points**.
- KB article explanations for each ticket type are shown at the end.

### Ticket Categories

| Category | Description |
|---|---|
| **Incident** | Unplanned interruption or degradation of a service |
| **Generic Service Request** | Ad-hoc request for information, advice, or access not in the catalog |
| **Service Catalog Request** | Standard, pre-approved service with a defined fulfillment process |

---

## Admin Dashboard

- Accessible only after logging in at `/admin/login`.
- Shows: total plays, unique players, average score, top score, perfect games, wrong attempts.
- Doughnut chart breaks scores into bands: Perfect (100), Excellent (80–99), Good (60–79), Needs Practice (<60).
- Full player table with email, score, correct/wrong counts, and timestamp.

---

## Security Notes

- Admin password is stored as a SHA-256 hash in `.env` — never in source code.
- `.env` and `cotiviti_game.sqlite` are excluded from version control via `.gitignore`.
- All database queries use parameterized statements (no SQL injection risk).
- Session cookies are `HttpOnly` and `SameSite=Lax`.
- Set `SESSION_COOKIE_SECURE = True` in `app.py` if serving over HTTPS.

---

## Environment

- Python 3.14 managed by [uv](https://github.com/astral-sh/uv)
- Flask 3.1.3
- SQLite (built-in)
- Chart.js 4.4.3 (CDN, dashboard only)
