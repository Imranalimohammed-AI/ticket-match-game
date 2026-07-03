# Architecture — Cotiviti IT Ticket Triage Challenge

## Variants

Two delivery modes for the same game content:

```
ticket-match-game/
  ├── cotiviti_ticket_match.py       Desktop game (Tkinter, no server)
  ├── cotiviti_bubble_explorer.py    Bubble explorer desktop (Tkinter)
  ├── cotiviti_bubble_explorer.html  Bubble explorer browser (zero-install, share directly)
  └── web/                           Multi-player web game (Flask + SQLite)
        ├── app.py                   Flask routes: game, admin login, dashboard
        ├── setup_admin.py           One-time admin password hash setup
        ├── templates/
        │   ├── game.html            Player UI (drag-and-drop triage)
        │   ├── dashboard.html       Admin stats (Chart.js doughnut)
        │   └── login.html           Admin login
        └── cotiviti_game.sqlite     Player results (auto-created)
```

## Web game — request flow

```
Player (browser)
  └─► GET /                     serve game.html
        └─► POST /submit        record name, email, score, answers
              └─► SQLite INSERT (parameterized — no SQL injection)
                    └─► redirect to results

Admin (browser)
  └─► GET /admin/login          serve login.html
        └─► POST /admin/login   check SHA-256 hash from .env
              └─► session set   redirect to dashboard
                    └─► GET /admin/dashboard   aggregate stats + Chart.js
```

## Scoring

```
Per scenario:
  base  = 10 points if correct
  bonus = base × streak_multiplier  (streak_multiplier doubles per level)

End of game:
  flawless_bonus = +10 if all 9 scenarios correct

Maximum = 100 points
```

## Security

| Control | Implementation |
|---|---|
| Admin password | SHA-256 hash stored in `.env` — `setup_admin.py` writes it once |
| Session auth | `flask.session` with `SECRET_KEY` from `.env` |
| SQL injection | All queries use parameterized statements |
| Cookie flags | `HttpOnly`, `SameSite=Lax`; set `SESSION_COOKIE_SECURE=True` for HTTPS |
| Secrets excluded | `.env` and `cotiviti_game.sqlite` listed in `.gitignore` |
