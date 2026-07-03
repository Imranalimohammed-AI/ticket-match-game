<div align="center">

# IT Ticket Triage Challenge

**Interactive training game that teaches staff to correctly classify IT support tickets**

[![Python](https://img.shields.io/badge/Python-3.14-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-003b57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Branch](https://img.shields.io/badge/branch-main-3b82f6?style=flat-square&logo=git&logoColor=white)](https://github.com/Imranalimohammed-AI/ticket-match-game)

*Cotiviti IT Engineering · Staff Training Tool*

</div>

---

## Overview

An ITSM training game that challenges staff to drag and classify IT scenarios into the correct ticket category. Built for Cotiviti IT to reduce misclassification rates and improve first-contact resolution.

---

## Ticket Categories

| Category | Description |
|----------|-------------|
| **Incident** | Unplanned interruption or degradation of a service |
| **Generic Service Request** | Ad-hoc request for information, advice, or access not in the catalog |
| **Service Catalog Request** | Standard, pre-approved service with a defined fulfilment process |

---

## Scoring

- **10 base points** per correct answer
- **Streak bonus** — multiplier increases with consecutive correct answers
- **Flawless bonus** — +10 for a perfect round
- **Maximum score: 100 points**

---

## Components

| Component | Description |
|-----------|-------------|
| **Web Game** | Flask app with player leaderboard (recommended) |
| **Admin Dashboard** | Stats, score distribution chart, full player table |
| **Desktop Game** | Tkinter drag-and-drop triage game |
| **Bubble Explorer** | Animated 3D bubble explorer (web + desktop) |

---

## Branch Strategy

```
main          ← production, protected (PR-only)
  └── develop ← integration, all PRs target here
        ├── feature/<name>
        ├── fix/<name>
        └── hotfix/<name>
```

---

## Quick Start — Web Game

```powershell
# Clone
git clone git@github.com:Imranalimohammed-AI/ticket-match-game.git
cd ticket-match-game

# Use the shared venv (or create one)
cd AI-Vibecoding
.\.venv\Scripts\Activate.ps1

# Install Flask if not already installed
uv pip install flask python-dotenv

# Set up admin password (run once)
cd ticket-match-game\web
& ..\..\AI-Vibecoding\.venv\Scripts\python.exe setup_admin.py

# Start the server
& ..\..\AI-Vibecoding\.venv\Scripts\python.exe app.py
```

Open **http://localhost:5000**

---

## Quick Start — Desktop Game

```powershell
cd AI-Vibecoding
.\.venv\Scripts\Activate.ps1
python ticket-match-game\cotiviti_ticket_match.py
```

---

## Admin Dashboard

URL: `/admin/login`

- Total plays, unique players, average score, top score, perfect games
- Score band doughnut chart: Perfect / Excellent / Good / Needs Practice
- Full player table with email, score, correct/wrong counts, and timestamp

---

## Security

| Control | Implementation |
|---------|---------------|
| Admin password | SHA-256 hash in `.env` — never in source code |
| Database | All queries parameterised — SQL injection prevented |
| Session cookies | `HttpOnly`, `SameSite=Lax` |
| Secrets | `.env` and `*.sqlite` excluded from version control |

See [SECURITY.md](SECURITY.md) for the full policy.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branching strategy and PR guidelines.

## License

MIT © 2026 Imranali Mohammed — see [LICENSE](LICENSE)
