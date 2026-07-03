"""
app.py — Flask server for the Cotiviti IT Ticket Triage web game.

Routes
------
GET  /                      Public game page
POST /api/save-result       Save a completed-game result to SQLite
GET|POST /admin/login       Password-protected login
GET  /admin/logout          Clears session
GET  /admin/dashboard       Admin stats dashboard
GET  /admin/api/stats       JSON stats for Chart.js (admin only)
"""

import hashlib
import hmac
import os
import sqlite3
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

load_dotenv()

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # set True behind HTTPS in production

DB_PATH = os.path.join(os.path.dirname(__file__), "cotiviti_game.sqlite")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    """Return a per-request SQLite connection (stored on Flask's g object)."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            email            TEXT    NOT NULL,
            name             TEXT    NOT NULL DEFAULT '',
            score            INTEGER NOT NULL DEFAULT 0,
            total_correct    INTEGER NOT NULL DEFAULT 0,
            total_wrong      INTEGER NOT NULL DEFAULT 0,
            is_perfect       INTEGER NOT NULL DEFAULT 0,
            played_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
        )
        """
    )
    db.commit()


# Initialise schema when the app context starts (works for dev server and WSGI)
with app.app_context():
    init_db()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def _admin_configured() -> bool:
    return bool(os.environ.get("ADMIN_PASSWORD_HASH"))


def _check_password(plain: str) -> bool:
    expected = os.environ.get("ADMIN_PASSWORD_HASH", "")
    actual = hashlib.sha256(plain.encode("utf-8")).hexdigest()
    # Constant-time comparison to resist timing attacks
    return hmac.compare_digest(actual, expected)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _admin_configured():
            return (
                "Admin not configured — run setup_admin.py",
                503,
            )
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return render_template("game.html")


@app.post("/api/save-result")
def save_result():
    """Persist a game result.  All inputs are validated before touching the DB."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    email = str(data.get("email", "")).strip()
    name = str(data.get("name", "")).strip()

    # Basic email sanity check (not a full RFC validator — just guards DB)
    if not email or "@" not in email or len(email) > 254:
        return jsonify({"error": "Invalid email"}), 400

    # Numeric fields — clamp to safe range
    try:
        score = max(0, min(100, int(data.get("score", 0))))
        total_correct = max(0, min(100, int(data.get("correct", 0))))
        total_wrong = max(0, min(100, int(data.get("wrong", 0))))
        is_perfect = 1 if data.get("is_perfect") else 0
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid numeric field"}), 400

    db = get_db()
    db.execute(
        """
        INSERT INTO sessions (email, name, score, total_correct, total_wrong, is_perfect)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (email, name, score, total_correct, total_wrong, is_perfect),
    )
    db.commit()
    return jsonify({"ok": True}), 201


# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if not _admin_configured():
        return "Admin not configured — run setup_admin.py", 503

    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if _check_password(password):
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Incorrect password."

    return render_template("login.html", error=error)


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db()

    rows = db.execute(
        "SELECT id, name, email, score, total_correct, total_wrong, is_perfect, played_at "
        "FROM sessions ORDER BY played_at DESC"
    ).fetchall()

    stats = db.execute(
        """
        SELECT
            COUNT(*)                          AS total_plays,
            COUNT(DISTINCT email)             AS unique_players,
            ROUND(AVG(score), 1)              AS avg_score,
            MAX(score)                        AS top_score,
            SUM(is_perfect)                   AS perfect_games,
            SUM(total_wrong)                  AS total_wrong_attempts
        FROM sessions
        """
    ).fetchone()

    return render_template("dashboard.html", rows=rows, stats=stats)


@app.get("/admin/api/stats")
@admin_required
def admin_api_stats():
    db = get_db()
    rows = db.execute("SELECT score FROM sessions").fetchall()
    scores = [r["score"] for r in rows]

    bands = {"perfect": 0, "excellent": 0, "good": 0, "needs_practice": 0}
    for s in scores:
        if s == 100:
            bands["perfect"] += 1
        elif s >= 80:
            bands["excellent"] += 1
        elif s >= 60:
            bands["good"] += 1
        else:
            bands["needs_practice"] += 1

    return jsonify(bands)


if __name__ == "__main__":
    print("\n=== Cotiviti IT Ticket Triage - Web Game ===")
    print("  Game:      http://192.168.0.116:5000/")
    print("  Dashboard: http://localhost:5000/admin/dashboard\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
