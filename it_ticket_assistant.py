"""
Cotiviti — AI-Powered IT Ticket Triage Assistant
Claude triages tickets: priority, category, resolution path, fix steps, KB article, email draft
"""

import csv
import json
import os
import threading
from collections import Counter
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext
import tkinter as tk
from tkinter import ttk

import anthropic

# ── Cotiviti Brand Palette ─────────────────────────────────────────────────────
C_PRIMARY   = "#002855"
C_SECONDARY = "#0A4D8C"
C_ACCENT    = "#F7941D"
C_BG        = "#F0F4F8"
C_CARD      = "#FFFFFF"
C_TEXT      = "#002855"
C_MUTED     = "#64748B"
C_SELECTED  = "#0096D6"
C_HOVER     = "#E6F2FA"
C_SUCCESS   = "#00875A"
C_DANGER    = "#D63B2F"
FONT        = "Segoe UI"

PRIORITY_COLORS: dict[str, tuple[str, str]] = {
    "P1": ("#D63B2F", "#FDF0EF"),
    "P2": ("#F7941D", "#FEF7EC"),
    "P3": ("#0096D6", "#E6F4FA"),
    "P4": ("#00875A", "#E6F5F0"),
}
PRIORITY_LABELS = {
    "P1": "P1 — CRITICAL",
    "P2": "P2 — HIGH",
    "P3": "P3 — MEDIUM",
    "P4": "P4 — LOW",
}
RESOLUTION_COLORS = {
    "Auto-Resolve":    C_SUCCESS,
    "Assign to Agent": C_SELECTED,
    "Escalate":        C_DANGER,
}
CATEGORIES = [
    "Network", "Auth/Identity", "Hardware", "Software",
    "Email/Calendar", "Database", "Access/Permissions", "Other",
]

EXAMPLE_TICKETS = [
    ("VPN Down",        "GlobalProtect VPN shows 'Gateway not responding' — entire team can't connect to the corporate network since 8 AM."),
    ("Locked Out",      "Okta MFA stopped working after I replaced my phone. I'm locked out of all SSO applications including email and JIRA."),
    ("Laptop BSOD",     "My laptop blue-screens every time I open Visual Studio. Started after the Windows update pushed overnight."),
    ("Software Install","I need Adobe Acrobat Pro installed — I'm a paralegal and it's required for my daily document review workflow."),
    ("DB Down",         "Production database is throwing connection errors. All staff transactions blocked. Direct revenue impact."),
    ("Printer Setup",   "Need to add the HP LaserJet on Floor 3 to my workstation. It's listed in the Service Portal hardware catalog."),
]

# Mock agent roster — in production this would come from an HR/directory API
MOCK_AGENTS: list[dict] = [
    {"id": "A01", "name": "Alice Johnson",   "email": "alice.johnson@cotiviti.com",
     "specializations": ["Network", "Infrastructure", "VPN"],
     "work_start": 8,  "work_end": 17, "tz": "ET", "load": 2, "max_load": 5},
    {"id": "A02", "name": "Bob Smith",       "email": "bob.smith@cotiviti.com",
     "specializations": ["Auth/Identity", "Okta", "Active Directory"],
     "work_start": 9,  "work_end": 18, "tz": "ET", "load": 1, "max_load": 5},
    {"id": "A03", "name": "Carol Martinez",  "email": "carol.martinez@cotiviti.com",
     "specializations": ["Hardware", "Laptop", "Peripherals"],
     "work_start": 7,  "work_end": 16, "tz": "ET", "load": 3, "max_load": 5},
    {"id": "A04", "name": "David Patel",     "email": "david.patel@cotiviti.com",
     "specializations": ["Software", "Database", "Applications"],
     "work_start": 10, "work_end": 19, "tz": "ET", "load": 0, "max_load": 5},
    {"id": "A05", "name": "Emma Wilson",     "email": "emma.wilson@cotiviti.com",
     "specializations": ["Email/Calendar", "Outlook", "Exchange"],
     "work_start": 8,  "work_end": 17, "tz": "ET", "load": 4, "max_load": 5},
]

SYSTEM_PROMPT = """You are an expert IT helpdesk triage assistant for Cotiviti, a healthcare analytics company.
Analyze the IT ticket and respond with a JSON object ONLY — no markdown, no explanation, no code fences.

JSON schema (all fields required):
{
  "priority": "P1|P2|P3|P4",
  "priority_reason": "one concise sentence",
  "category": "Network|Auth/Identity|Hardware|Software|Email/Calendar|Database|Access/Permissions|Other",
  "resolution_path": "Auto-Resolve|Assign to Agent|Escalate",
  "resolution_reason": "one concise sentence",
  "fix_steps": ["step 1", "step 2", "step 3"],
  "kb_article_title": "Title for a KB article to prevent this issue recurring",
  "estimated_resolution_time": "e.g. 15 minutes",
  "email_draft": {
    "subject": "RE: [Ticket] Brief issue title",
    "body": "Professional acknowledgement and next-steps email to the user (3-5 sentences)"
  }
}

Priority guide:
P1 CRITICAL — complete service outage, data loss risk, security breach, multi-user blocking, revenue impact
P2 HIGH — significant degradation, 2-5 users affected, deadline-sensitive work blocked
P3 MEDIUM — single user affected, workaround available, standard request needing agent review
P4 LOW — informational query, cosmetic issue, catalog item, no operational urgency

Resolution path:
Auto-Resolve — standard Service Catalog items, well-documented self-service steps
Assign to Agent — needs hands-on support, specialist knowledge, but not emergency
Escalate — P1 incidents, security events, widespread outages, unknown root cause"""


class ITTicketAssistant:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Cotiviti — AI Ticket Triage Assistant")
        self.root.geometry("1200x820")
        self.root.configure(bg=C_BG)
        self.root.minsize(1000, 700)

        self._client: anthropic.Anthropic | None = None
        self.tickets: list[dict] = []
        self.agents:  list[dict] = [a.copy() for a in MOCK_AGENTS]
        self._counter = 0

        self._configure_styles()
        self._build_ui()
        self._check_api_key()

    # ── Styles ─────────────────────────────────────────────────────────────────

    def _configure_styles(self) -> None:
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Coti.Horizontal.TProgressbar",
                    background=C_ACCENT, troughcolor="#D0D8E4",
                    borderwidth=0, thickness=6)
        s.configure("Coti.TNotebook", background=C_PRIMARY, borderwidth=0)
        s.configure("Coti.TNotebook.Tab",
                    background=C_SECONDARY, foreground="white",
                    font=(FONT, 10, "bold"), padding=(16, 8))
        s.map("Coti.TNotebook.Tab",
              background=[("selected", C_ACCENT)],
              foreground=[("selected", "white")])

    # ── API key ────────────────────────────────────────────────────────────────

    def _check_api_key(self) -> None:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if key:
            self._client = anthropic.Anthropic(api_key=key)
        else:
            self._prompt_api_key()

    def _prompt_api_key(self) -> None:
        ov = tk.Toplevel(self.root)
        ov.title("API Key Required")
        ov.configure(bg=C_PRIMARY)
        ov.resizable(False, False)
        ov.transient(self.root)
        ov.grab_set()
        ov.geometry("440x290")
        self.root.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - 440) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - 290) // 2
        ov.geometry(f"440x290+{rx}+{ry}")

        tk.Label(ov, text="Anthropic API Key",
                 font=(FONT, 16, "bold"), bg=C_PRIMARY, fg=C_ACCENT).pack(pady=(24, 4))
        tk.Label(ov, text="Enter your ANTHROPIC_API_KEY to enable AI triage.",
                 font=(FONT, 10), bg=C_PRIMARY, fg="#AAC4E8").pack(pady=(0, 12))

        key_var = tk.StringVar()
        entry = tk.Entry(ov, textvariable=key_var, show="*", width=44,
                         font=(FONT, 11), relief="flat", bd=6)
        entry.pack(padx=30)
        entry.focus_set()

        err_lbl = tk.Label(ov, text="", font=(FONT, 9), bg=C_PRIMARY, fg=C_DANGER)
        err_lbl.pack(pady=4)

        def _save() -> None:
            k = key_var.get().strip()
            if not k.startswith("sk-"):
                err_lbl.config(text="Key must start with 'sk-'")
                return
            self._client = anthropic.Anthropic(api_key=k)
            ov.destroy()

        tk.Button(ov, text="  Connect  ", font=(FONT, 12, "bold"),
                  bg=C_ACCENT, fg="white", relief="flat", padx=16, pady=8,
                  cursor="hand2", command=_save).pack(pady=14)
        ov.bind("<Return>", lambda _: _save())

    # ── Main layout ────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        hdr = tk.Frame(self.root, bg=C_PRIMARY, height=76)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Accent side bar — Cotiviti brand mark
        tk.Frame(hdr, bg=C_ACCENT, width=6).pack(side="left", fill="y")

        logo_frame = tk.Frame(hdr, bg=C_PRIMARY)
        logo_frame.pack(side="left", padx=(16, 8), pady=10)
        tk.Label(logo_frame, text="COTIVITI", font=(FONT, 14, "bold"),
                 bg=C_PRIMARY, fg=C_ACCENT).pack(anchor="w")
        tk.Label(logo_frame, text="Healthcare Analytics", font=(FONT, 7),
                 bg=C_PRIMARY, fg="#6A8FAD").pack(anchor="w")

        tk.Frame(hdr, bg=C_SECONDARY, width=1).pack(side="left", fill="y", pady=14)

        tk.Label(hdr, text="AI-Powered IT Ticket Triage Assistant",
                 font=(FONT, 16, "bold"), bg=C_PRIMARY, fg="white").pack(side="left", padx=16)

        self._status_lbl = tk.Label(hdr, text="● Ready", font=(FONT, 10),
                                    bg=C_PRIMARY, fg=C_SUCCESS)
        self._status_lbl.pack(side="right", padx=18)

        # Accent bottom border
        tk.Frame(self.root, bg=C_ACCENT, height=3).pack(fill="x")

        sub = tk.Frame(self.root, bg=C_SECONDARY, height=26)
        sub.pack(fill="x")
        sub.pack_propagate(False)
        tk.Label(sub,
                 text="Paste a ticket → Claude assigns priority · category · fix steps · KB article · email draft",
                 font=(FONT, 9), bg=C_SECONDARY, fg="#C8DFFB").pack(side="left", padx=16, pady=4)

        nb = ttk.Notebook(self.root, style="Coti.TNotebook")
        nb.pack(fill="both", expand=True)

        t_analyze = tk.Frame(nb, bg=C_BG)
        t_bulk    = tk.Frame(nb, bg=C_BG)
        t_dash    = tk.Frame(nb, bg=C_BG)
        t_agents  = tk.Frame(nb, bg=C_BG)

        nb.add(t_analyze, text="  Analyze Ticket  ")
        nb.add(t_bulk,    text="  Bulk Upload  ")
        nb.add(t_dash,    text="  Dashboard  ")
        nb.add(t_agents,  text="  Agents  ")

        self._build_analyze_tab(t_analyze)
        self._build_bulk_tab(t_bulk)
        self._build_dashboard_tab(t_dash)
        self._build_agents_tab(t_agents)

    # ══════════════════════════════════════════════════════════════════════════
    # Tab: Analyze Ticket
    # ══════════════════════════════════════════════════════════════════════════

    def _build_analyze_tab(self, parent: tk.Frame) -> None:
        left = tk.Frame(parent, bg=C_BG, width=410)
        left.pack(side="left", fill="y", padx=(16, 8), pady=14)
        left.pack_propagate(False)

        right = tk.Frame(parent, bg=C_BG)
        right.pack(side="right", fill="both", expand=True, padx=(0, 16), pady=14)

        # ── Input ──────────────────────────────────────────────────────────────
        tk.Label(left, text="Ticket Description",
                 font=(FONT, 11, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w")
        tk.Label(left, text="Paste a real ticket or try a quick example",
                 font=(FONT, 9), bg=C_BG, fg=C_MUTED).pack(anchor="w", pady=(0, 6))

        self._ticket_input = scrolledtext.ScrolledText(
            left, height=9, font=(FONT, 10), relief="groove", bd=1,
            wrap="word", bg=C_CARD, fg=C_TEXT,
        )
        self._ticket_input.pack(fill="x")

        self._analyze_btn = tk.Button(
            left, text="  Analyze with Claude  →",
            font=(FONT, 12, "bold"), bg=C_ACCENT, fg="white",
            relief="flat", padx=14, pady=10, cursor="hand2",
            command=self._run_analyze,
        )
        self._analyze_btn.pack(fill="x", pady=(10, 0))

        self._analyze_pb = ttk.Progressbar(
            left, mode="indeterminate",
            style="Coti.Horizontal.TProgressbar", length=390,
        )

        # ── Examples ──────────────────────────────────────────────────────────
        tk.Label(left, text="Quick Examples",
                 font=(FONT, 10, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w", pady=(12, 4))
        eg = tk.Frame(left, bg=C_BG)
        eg.pack(fill="x")
        for i, (label, text) in enumerate(EXAMPLE_TICKETS):
            b = tk.Button(
                eg, text=f"⚡  {label}", font=(FONT, 9),
                bg=C_CARD, fg=C_SECONDARY, relief="groove", bd=1,
                cursor="hand2", padx=8, pady=5,
                command=lambda t=text: self._load_example(t),
            )
            b.grid(row=i // 2, column=i % 2, padx=3, pady=3, sticky="ew")
            b.bind("<Enter>", lambda _, b=b: b.config(bg=C_HOVER))
            b.bind("<Leave>", lambda _, b=b: b.config(bg=C_CARD))
        eg.columnconfigure(0, weight=1)
        eg.columnconfigure(1, weight=1)

        # ── Recent tickets tracker ─────────────────────────────────────────────
        tk.Label(left, text="Recent Tickets",
                 font=(FONT, 10, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w", pady=(14, 4))
        self._recent_frame = tk.Frame(left, bg=C_BG)
        self._recent_frame.pack(fill="x")
        self._pattern_lbl = tk.Label(
            left, text="", font=(FONT, 9, "italic"),
            bg=C_BG, fg=C_ACCENT, wraplength=390, justify="left",
        )
        self._pattern_lbl.pack(anchor="w", pady=(4, 0))

        # ── Results panel ──────────────────────────────────────────────────────
        tk.Label(right, text="Triage Results",
                 font=(FONT, 11, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w")
        tk.Label(right, text="Claude's analysis will appear here",
                 font=(FONT, 9), bg=C_BG, fg=C_MUTED).pack(anchor="w", pady=(0, 6))

        r_canvas = tk.Canvas(right, bg=C_BG, highlightthickness=0)
        r_scroll = ttk.Scrollbar(right, orient="vertical", command=r_canvas.yview)
        r_canvas.configure(yscrollcommand=r_scroll.set)
        r_scroll.pack(side="right", fill="y")
        r_canvas.pack(fill="both", expand=True)

        self._res_inner = tk.Frame(r_canvas, bg=C_BG)
        r_win = r_canvas.create_window((0, 0), window=self._res_inner, anchor="nw")

        self._res_inner.bind("<Configure>",
            lambda e: r_canvas.configure(scrollregion=r_canvas.bbox("all")))
        r_canvas.bind("<Configure>",
            lambda e: r_canvas.itemconfig(r_win, width=e.width))
        r_canvas.bind_all("<MouseWheel>",
            lambda e: r_canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self._show_placeholder()

    def _show_placeholder(self) -> None:
        for w in self._res_inner.winfo_children():
            w.destroy()
        ph = tk.Frame(self._res_inner, bg=C_CARD, relief="groove", bd=1)
        ph.pack(fill="x", pady=8, padx=4)
        tk.Label(ph, text="🎫", font=(FONT, 36), bg=C_CARD).pack(pady=(28, 8))
        tk.Label(ph,
                 text="Paste a ticket description and click\n\"Analyze with Claude\" to get started.",
                 font=(FONT, 11), bg=C_CARD, fg=C_MUTED, justify="center").pack(pady=(0, 28))

    def _load_example(self, text: str) -> None:
        self._ticket_input.delete("1.0", "end")
        self._ticket_input.insert("1.0", text)

    def _run_analyze(self) -> None:
        desc = self._ticket_input.get("1.0", "end").strip()
        if not desc:
            messagebox.showwarning("Empty Ticket", "Please enter a ticket description first.")
            return
        if not self._client:
            self._prompt_api_key()
            return
        self._set_busy(True)
        threading.Thread(target=self._analyze_thread, args=(desc,), daemon=True).start()

    def _set_busy(self, active: bool) -> None:
        if active:
            self._analyze_btn.config(state="disabled", text="  Analyzing…  ")
            self._analyze_pb.pack(fill="x", pady=(4, 0))
            self._analyze_pb.start(12)
            self._status_lbl.config(text="● Analyzing…", fg=C_ACCENT)
        else:
            self._analyze_btn.config(state="normal", text="  Analyze with Claude  →")
            self._analyze_pb.stop()
            self._analyze_pb.pack_forget()
            self._status_lbl.config(text="● Ready", fg=C_SUCCESS)

    def _analyze_thread(self, desc: str) -> None:
        try:
            result = self._call_claude(desc)
            self.root.after(0, lambda: self._on_result(desc, result))
        except Exception as exc:
            self.root.after(0, lambda: self._show_error(str(exc)))
        finally:
            self.root.after(0, lambda: self._set_busy(False))

    def _call_claude(self, desc: str) -> dict:
        resp = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=[{
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": f"Ticket: {desc}"}],
        )
        raw = resp.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)

    def _on_result(self, desc: str, r: dict) -> None:
        self._counter += 1
        ticket = {
            "id":       f"TKT-{self._counter:04d}",
            "ts":       datetime.now().strftime("%H:%M"),
            "desc":     desc[:80],
            "priority": r.get("priority", "P3"),
            "category": r.get("category", "Other"),
            "path":     r.get("resolution_path", "Assign to Agent"),
            "full":     r,
            "assigned": None,
        }
        assigned = self._auto_assign(ticket)
        if assigned:
            ticket["assigned"] = assigned["name"]
            assigned["load"] = min(assigned["load"] + 1, assigned["max_load"])

        self.tickets.append(ticket)
        self._render_result_card(r, ticket)
        self._update_recent()
        self._check_patterns()
        self._refresh_dashboard()
        self._refresh_agents_tab()

    def _render_result_card(self, r: dict, ticket: dict) -> None:
        for w in self._res_inner.winfo_children():
            w.destroy()

        pri = r.get("priority", "P3")
        fg, bg = PRIORITY_COLORS.get(pri, (C_TEXT, C_CARD))

        # Priority / category header bar
        hdr = tk.Frame(self._res_inner, bg=fg)
        hdr.pack(fill="x", padx=4, pady=(4, 0))
        tk.Label(hdr, text=PRIORITY_LABELS.get(pri, pri),
                 font=(FONT, 13, "bold"), bg=fg, fg="white", padx=14, pady=10).pack(side="left")
        tk.Label(hdr, text=f"🏷  {r.get('category','')}",
                 font=(FONT, 10), bg=fg, fg="white").pack(side="left", padx=8)
        tk.Label(hdr, text=f"#{ticket['id']}",
                 font=(FONT, 9), bg=fg, fg="white").pack(side="right", padx=14)
        tk.Label(hdr, text=f"⏱ {r.get('estimated_resolution_time','')}",
                 font=(FONT, 10), bg=fg, fg="white").pack(side="right", padx=4)

        # Reason
        reason = tk.Frame(self._res_inner, bg=bg)
        reason.pack(fill="x", padx=4)
        tk.Label(reason, text=r.get("priority_reason", ""),
                 font=(FONT, 9, "italic"), bg=bg, fg=fg,
                 padx=14, pady=6, anchor="w", wraplength=680, justify="left").pack(fill="x")

        # Resolution path
        rpath = r.get("resolution_path", "Assign to Agent")
        rc    = RESOLUTION_COLORS.get(rpath, C_TEXT)
        path_row = tk.Frame(self._res_inner, bg=C_CARD, relief="groove", bd=1)
        path_row.pack(fill="x", padx=4, pady=(6, 0))
        tk.Label(path_row, text="🗂  Resolution Path:",
                 font=(FONT, 9, "bold"), bg=C_CARD, fg=C_MUTED, padx=14, pady=6).pack(side="left")
        tk.Label(path_row, text=f"  {rpath}  ",
                 font=(FONT, 10, "bold"), bg=rc, fg="white", pady=4, padx=8).pack(side="left")
        tk.Label(path_row, text=r.get("resolution_reason", ""),
                 font=(FONT, 9), bg=C_CARD, fg=C_MUTED, padx=8,
                 wraplength=380).pack(side="left", fill="x", expand=True)
        if ticket.get("assigned"):
            tk.Label(path_row, text=f"→ {ticket['assigned']}",
                     font=(FONT, 9, "bold"), bg=C_CARD, fg=C_SELECTED, padx=10).pack(side="right")

        # Fix steps
        self._section_label(self._res_inner, "🔧  Step-by-Step Fix")
        steps = tk.Frame(self._res_inner, bg=C_CARD, relief="groove", bd=1)
        steps.pack(fill="x", padx=4, pady=(0, 6))
        for i, step in enumerate(r.get("fix_steps", []), 1):
            row = tk.Frame(steps, bg=C_CARD)
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(row, text=str(i), font=(FONT, 9, "bold"),
                     width=2, bg=C_ACCENT, fg="white").pack(side="left", padx=(0, 8))
            tk.Label(row, text=step, font=(FONT, 10), bg=C_CARD, fg=C_TEXT,
                     anchor="w", wraplength=600, justify="left").pack(side="left", fill="x", expand=True)

        # KB article
        self._section_label(self._res_inner, "📚  Suggested KB Article")
        kb = tk.Frame(self._res_inner, bg="#EBF3FB", relief="groove", bd=1)
        kb.pack(fill="x", padx=4, pady=(0, 6))
        tk.Label(kb, text=r.get("kb_article_title", ""),
                 font=(FONT, 10, "bold"), bg="#EBF3FB", fg=C_SECONDARY,
                 padx=14, pady=10, anchor="w", wraplength=660, justify="left").pack(fill="x")

        # Email draft
        ed = r.get("email_draft", {})
        if ed:
            self._section_label(self._res_inner, "✉️  Draft Response Email")
            email = tk.Frame(self._res_inner, bg=C_CARD, relief="groove", bd=1)
            email.pack(fill="x", padx=4, pady=(0, 10))
            tk.Label(email, text=f"Subject: {ed.get('subject','')}",
                     font=(FONT, 9, "bold"), bg=C_CARD, fg=C_PRIMARY,
                     padx=14, pady=6, anchor="w").pack(fill="x")
            tk.Frame(email, bg="#D0D8E4", height=1).pack(fill="x")
            body_txt = scrolledtext.ScrolledText(
                email, height=6, font=(FONT, 9), bg=C_CARD, fg=C_TEXT,
                relief="flat", wrap="word",
            )
            body_txt.insert("1.0", ed.get("body", ""))
            body_txt.config(state="disabled")
            body_txt.pack(fill="x", padx=10, pady=(4, 4))
            tk.Button(
                email, text="  Copy Email  ",
                font=(FONT, 9), bg=C_SECONDARY, fg="white",
                relief="flat", padx=10, pady=4, cursor="hand2",
                command=lambda s=ed.get("subject",""), b=ed.get("body",""): self._copy_email(s, b),
            ).pack(anchor="e", padx=10, pady=(0, 8))

    def _section_label(self, parent: tk.Frame, title: str) -> None:
        tk.Label(parent, text=title, font=(FONT, 10, "bold"),
                 bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=4, pady=(8, 2))

    def _copy_email(self, subject: str, body: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(f"Subject: {subject}\n\n{body}")
        messagebox.showinfo("Copied", "Email draft copied to clipboard.")

    def _show_error(self, msg: str) -> None:
        for w in self._res_inner.winfo_children():
            w.destroy()
        err = tk.Frame(self._res_inner, bg="#FDF0EF", relief="groove", bd=1)
        err.pack(fill="x", padx=4, pady=8)
        tk.Label(err, text="⚠️  Analysis Failed",
                 font=(FONT, 11, "bold"), bg="#FDF0EF", fg=C_DANGER).pack(pady=(12, 4))
        tk.Label(err, text=msg, font=(FONT, 9), bg="#FDF0EF", fg=C_TEXT,
                 wraplength=620, justify="center").pack(padx=16, pady=(0, 14))

    # ── Recent + pattern ───────────────────────────────────────────────────────

    def _update_recent(self) -> None:
        for w in self._recent_frame.winfo_children():
            w.destroy()
        for t in reversed(self.tickets[-6:]):
            pc, _ = PRIORITY_COLORS.get(t["priority"], (C_MUTED, C_CARD))
            row = tk.Frame(self._recent_frame, bg=C_CARD, relief="groove", bd=1)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=t["priority"], font=(FONT, 8, "bold"),
                     bg=pc, fg="white", width=3, padx=4, pady=3).pack(side="left")
            short = t["desc"][:48] + "…" if len(t["desc"]) > 48 else t["desc"]
            tk.Label(row, text=f"[{t['ts']}] {short}",
                     font=(FONT, 8), bg=C_CARD, fg=C_TEXT,
                     anchor="w", padx=6, pady=3).pack(side="left", fill="x", expand=True)

    def _check_patterns(self) -> None:
        if len(self.tickets) < 2:
            self._pattern_lbl.config(text="")
            return
        recent_cats = Counter(t["category"] for t in self.tickets[-10:])
        top_cat, top_n = recent_cats.most_common(1)[0]
        if top_n >= 2:
            self._pattern_lbl.config(
                text=f"⚠ Pattern detected: {top_n} recent '{top_cat}' tickets — possible systemic issue."
            )
        else:
            self._pattern_lbl.config(text="")

    # ── Auto-assign ────────────────────────────────────────────────────────────

    def _auto_assign(self, ticket: dict) -> dict | None:
        if ticket["path"] == "Auto-Resolve":
            return None
        cat      = ticket.get("category", "")
        now_hour = datetime.now().hour
        avail = [
            a for a in self.agents
            if a["work_start"] <= now_hour < a["work_end"] and a["load"] < a["max_load"]
        ]
        if not avail:
            return None

        def _score(a: dict) -> tuple:
            match = any(s.lower() in cat.lower() or cat.lower() in s.lower()
                        for s in a["specializations"])
            return (0 if match else 1, a["load"])

        return min(avail, key=_score)

    # ══════════════════════════════════════════════════════════════════════════
    # Tab: Bulk Upload
    # ══════════════════════════════════════════════════════════════════════════

    def _build_bulk_tab(self, parent: tk.Frame) -> None:
        top = tk.Frame(parent, bg=C_BG)
        top.pack(fill="x", padx=16, pady=14)

        tk.Label(top, text="Bulk Ticket Upload",
                 font=(FONT, 12, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w")
        tk.Label(top, text="One ticket per line — or upload a .csv file (first column used as description)",
                 font=(FONT, 9), bg=C_BG, fg=C_MUTED).pack(anchor="w", pady=(0, 8))

        self._bulk_input = scrolledtext.ScrolledText(
            top, height=8, font=(FONT, 10), relief="groove", bd=1,
            wrap="word", bg=C_CARD, fg=C_TEXT,
        )
        self._bulk_input.pack(fill="x")
        self._bulk_input.insert("1.0",
            "My laptop won't start after the Windows update this morning\n"
            "Need Adobe Acrobat Pro installed — required for my daily document review\n"
            "Outlook calendar not syncing — meetings missing since 9 AM\n"
            "Request a new ergonomic chair via the Service Portal\n"
            "Production DB connection errors blocking all transactions"
        )

        btn_row = tk.Frame(top, bg=C_BG)
        btn_row.pack(fill="x", pady=(8, 0))

        tk.Button(btn_row, text="  Analyze All  →",
                  font=(FONT, 11, "bold"), bg=C_ACCENT, fg="white",
                  relief="flat", padx=14, pady=9, cursor="hand2",
                  command=self._run_bulk).pack(side="left")
        tk.Button(btn_row, text="  Upload CSV  ",
                  font=(FONT, 10), bg=C_SECONDARY, fg="white",
                  relief="flat", padx=12, pady=8, cursor="hand2",
                  command=self._upload_csv).pack(side="left", padx=8)
        tk.Button(btn_row, text="  Export Results  ",
                  font=(FONT, 10), bg=C_SECONDARY, fg="white",
                  relief="flat", padx=12, pady=8, cursor="hand2",
                  command=self._export_csv).pack(side="right")

        self._bulk_status = tk.StringVar(value="")
        tk.Label(btn_row, textvariable=self._bulk_status,
                 font=(FONT, 9), bg=C_BG, fg=C_MUTED).pack(side="left", padx=8)

        # Results table
        cols = ("ID", "Priority", "Category", "Resolution Path", "Assigned", "Description")
        self._bulk_tree = ttk.Treeview(parent, columns=cols, show="headings", height=18)
        col_widths = {"ID": 75, "Priority": 80, "Category": 120,
                      "Resolution Path": 130, "Assigned": 140, "Description": 380}
        for col in cols:
            self._bulk_tree.heading(col, text=col)
            self._bulk_tree.column(col, width=col_widths[col],
                                   anchor="w" if col == "Description" else "center")
        for p, (fc, bg) in PRIORITY_COLORS.items():
            self._bulk_tree.tag_configure(p, background=bg)

        bs = ttk.Scrollbar(parent, orient="vertical", command=self._bulk_tree.yview)
        self._bulk_tree.configure(yscrollcommand=bs.set)
        bs.pack(side="right", fill="y", padx=(0, 16))
        self._bulk_tree.pack(fill="both", expand=True, padx=(16, 0), pady=(8, 14))

    def _run_bulk(self) -> None:
        lines = [l.strip() for l in self._bulk_input.get("1.0", "end").splitlines() if l.strip()]
        if not lines:
            messagebox.showwarning("Empty", "No tickets to analyze.")
            return
        if not self._client:
            self._prompt_api_key()
            return
        for row in self._bulk_tree.get_children():
            self._bulk_tree.delete(row)
        threading.Thread(target=self._bulk_thread, args=(lines,), daemon=True).start()

    def _bulk_thread(self, lines: list[str]) -> None:
        for i, desc in enumerate(lines, 1):
            self.root.after(0, lambda i=i, n=len(lines):
                self._bulk_status.set(f"Analyzing {i}/{n}…"))
            try:
                r = self._call_claude(desc)
                self.root.after(0, lambda d=desc, r=r: self._bulk_add_row(d, r))
            except Exception as exc:
                self.root.after(0, lambda d=desc, e=str(exc): self._bulk_add_error(d, e))
        self.root.after(0, lambda n=len(lines): [
            self._bulk_status.set(f"Done — {n} tickets analyzed"),
            self._refresh_dashboard(),
            self._refresh_agents_tab(),
        ])

    def _bulk_add_row(self, desc: str, r: dict) -> None:
        self._counter += 1
        pri  = r.get("priority", "P3")
        path = r.get("resolution_path", "Assign to Agent")
        ticket = {
            "id":       f"TKT-{self._counter:04d}",
            "ts":       datetime.now().strftime("%H:%M"),
            "desc":     desc[:80],
            "priority": pri,
            "category": r.get("category", "Other"),
            "path":     path,
            "full":     r,
            "assigned": None,
        }
        assigned = self._auto_assign(ticket)
        if assigned:
            ticket["assigned"] = assigned["name"]
            assigned["load"] = min(assigned["load"] + 1, assigned["max_load"])
        self.tickets.append(ticket)
        self._bulk_tree.insert("", "end",
            values=(ticket["id"], pri, ticket["category"], path,
                    ticket.get("assigned") or "—", desc[:80]),
            tags=(pri,),
        )

    def _bulk_add_error(self, desc: str, msg: str) -> None:
        self._bulk_tree.insert("", "end",
            values=("ERROR", "—", "—", "—", "—", f"[FAILED] {desc[:60]}"))

    def _upload_csv(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8") as f:
                lines = [row[0] for row in csv.reader(f) if row]
            self._bulk_input.delete("1.0", "end")
            self._bulk_input.insert("1.0", "\n".join(lines))
        except Exception as exc:
            messagebox.showerror("CSV Error", str(exc))

    def _export_csv(self) -> None:
        rows = [self._bulk_tree.item(r)["values"]
                for r in self._bulk_tree.get_children()]
        if not rows:
            messagebox.showwarning("No Data", "No results to export yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ID", "Priority", "Category", "Resolution Path", "Assigned", "Description"])
            w.writerows(rows)
        messagebox.showinfo("Exported", f"Saved to {path}")

    # ══════════════════════════════════════════════════════════════════════════
    # Tab: Dashboard
    # ══════════════════════════════════════════════════════════════════════════

    def _build_dashboard_tab(self, parent: tk.Frame) -> None:
        self._dash_parent = parent

        d_canvas = tk.Canvas(parent, bg=C_BG, highlightthickness=0)
        d_scroll = ttk.Scrollbar(parent, orient="vertical", command=d_canvas.yview)
        d_canvas.configure(yscrollcommand=d_scroll.set)
        d_scroll.pack(side="right", fill="y")
        d_canvas.pack(fill="both", expand=True)

        self._dash_inner = tk.Frame(d_canvas, bg=C_BG)
        dw = d_canvas.create_window((0, 0), window=self._dash_inner, anchor="nw")
        self._dash_inner.bind("<Configure>",
            lambda e: d_canvas.configure(scrollregion=d_canvas.bbox("all")))
        d_canvas.bind("<Configure>",
            lambda e: d_canvas.itemconfig(dw, width=e.width))

        self._refresh_dashboard()

    def _refresh_dashboard(self) -> None:
        if not hasattr(self, "_dash_inner"):
            return
        for w in self._dash_inner.winfo_children():
            w.destroy()

        total       = len(self.tickets)
        p_counts    = Counter(t["priority"] for t in self.tickets)
        c_counts    = Counter(t["category"] for t in self.tickets)
        path_counts = Counter(t["path"]     for t in self.tickets)

        tk.Label(self._dash_inner, text="Ticket Dashboard",
                 font=(FONT, 14, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=16, pady=(14, 4))

        # ── Import Data ────────────────────────────────────────────────────────
        import_row = tk.Frame(self._dash_inner, bg=C_BG)
        import_row.pack(fill="x", padx=16, pady=(0, 10))

        # Tickets import card
        t_card = tk.Frame(import_row, bg=C_CARD, relief="groove", bd=1)
        t_card.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tk.Label(t_card, text="Import Tickets",
                 font=(FONT, 10, "bold"), bg=C_CARD, fg=C_PRIMARY).pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(t_card,
                 text="CSV — one ticket description per row (first column used)",
                 font=(FONT, 8), bg=C_CARD, fg=C_MUTED).pack(anchor="w", padx=12)
        t_btn_row = tk.Frame(t_card, bg=C_CARD)
        t_btn_row.pack(anchor="w", padx=12, pady=8)
        tk.Button(t_btn_row, text="  Upload Tickets CSV  ",
                  font=(FONT, 9, "bold"), bg=C_ACCENT, fg="white",
                  relief="flat", padx=10, pady=6, cursor="hand2",
                  command=self._import_tickets_dashboard).pack(side="left")
        tk.Button(t_btn_row, text="  Download Template  ",
                  font=(FONT, 9), bg=C_CARD, fg=C_SECONDARY,
                  relief="groove", bd=1, padx=8, pady=5, cursor="hand2",
                  command=self._download_tickets_template).pack(side="left", padx=(8, 0))

        # Agents import card
        a_card = tk.Frame(import_row, bg=C_CARD, relief="groove", bd=1)
        a_card.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(a_card, text="Import Agent Roster",
                 font=(FONT, 10, "bold"), bg=C_CARD, fg=C_PRIMARY).pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(a_card,
                 text="CSV columns: name, email, specializations (;-separated), work_start, work_end, tz, max_load",
                 font=(FONT, 8), bg=C_CARD, fg=C_MUTED, wraplength=340, justify="left").pack(anchor="w", padx=12)
        a_btn_row = tk.Frame(a_card, bg=C_CARD)
        a_btn_row.pack(anchor="w", padx=12, pady=8)
        tk.Button(a_btn_row, text="  Upload Agents CSV  ",
                  font=(FONT, 9, "bold"), bg=C_SECONDARY, fg="white",
                  relief="flat", padx=10, pady=6, cursor="hand2",
                  command=self._import_agents_csv).pack(side="left")
        tk.Button(a_btn_row, text="  Download Template  ",
                  font=(FONT, 9), bg=C_CARD, fg=C_SECONDARY,
                  relief="groove", bd=1, padx=8, pady=5, cursor="hand2",
                  command=self._download_agents_template).pack(side="left", padx=(8, 0))

        tk.Frame(self._dash_inner, bg="#D0D8E4", height=1).pack(fill="x", padx=16, pady=(0, 8))

        # Stat cards
        cards = tk.Frame(self._dash_inner, bg=C_BG)
        cards.pack(fill="x", padx=16, pady=4)
        for label, value, color in [
            ("Total Tickets",   str(total),                        C_PRIMARY),
            ("P1 Critical",     str(p_counts.get("P1", 0)),        C_DANGER),
            ("P2 High",         str(p_counts.get("P2", 0)),        "#F7941D"),
            ("Auto-Resolved",   str(path_counts.get("Auto-Resolve", 0)), C_SUCCESS),
            ("Escalated",       str(path_counts.get("Escalate", 0)), C_SECONDARY),
        ]:
            card = tk.Frame(cards, bg=C_CARD, relief="groove", bd=1)
            card.pack(side="left", fill="both", expand=True, padx=4, pady=4)
            tk.Label(card, text=value, font=(FONT, 22, "bold"),
                     bg=C_CARD, fg=color).pack(pady=(14, 2))
            tk.Label(card, text=label, font=(FONT, 8),
                     bg=C_CARD, fg=C_MUTED).pack(pady=(0, 10))

        if total > 0:
            tk.Label(self._dash_inner, text="Tickets by Priority",
                     font=(FONT, 11, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=16, pady=(12, 2))
            self._bar_chart(
                {p: p_counts.get(p, 0) for p in ["P1", "P2", "P3", "P4"]},
                {p: c[0] for p, c in PRIORITY_COLORS.items()},
                height=90,
            )
            tk.Label(self._dash_inner, text="Tickets by Category",
                     font=(FONT, 11, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=16, pady=(12, 2))
            self._bar_chart(
                dict(c_counts.most_common(8)),
                {c: C_SELECTED for c in CATEGORIES},
                height=110,
            )

        tk.Label(self._dash_inner, text="Recent Activity",
                 font=(FONT, 11, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=16, pady=(12, 4))
        log = tk.Frame(self._dash_inner, bg=C_CARD, relief="groove", bd=1)
        log.pack(fill="x", padx=16, pady=(0, 16))
        if not self.tickets:
            tk.Label(log, text="No tickets analyzed yet.",
                     font=(FONT, 10), bg=C_CARD, fg=C_MUTED, pady=16).pack()
        else:
            for t in reversed(self.tickets[-12:]):
                pc, _ = PRIORITY_COLORS.get(t["priority"], (C_MUTED, C_CARD))
                tk.Frame(log, bg="#D0D8E4", height=1).pack(fill="x")
                row = tk.Frame(log, bg=C_CARD)
                row.pack(fill="x")
                tk.Label(row, text=t["priority"], font=(FONT, 8, "bold"),
                         bg=pc, fg="white", width=4, padx=4, pady=4).pack(side="left")
                tk.Label(row, text=t["id"], font=(FONT, 8),
                         bg=C_CARD, fg=C_MUTED, width=9, padx=4).pack(side="left")
                tk.Label(row, text=t["category"], font=(FONT, 8),
                         bg=C_CARD, fg=C_SECONDARY, width=18, anchor="w").pack(side="left")
                tk.Label(row, text=t["desc"][:65], font=(FONT, 8),
                         bg=C_CARD, fg=C_TEXT, anchor="w").pack(
                         side="left", fill="x", expand=True, padx=6)
                tk.Label(row, text=t.get("assigned") or "—", font=(FONT, 8),
                         bg=C_CARD, fg=C_MUTED, width=16, anchor="e", padx=6).pack(side="right")

    def _bar_chart(self, data: dict, colors: dict, height: int = 90) -> None:
        frame = tk.Frame(self._dash_inner, bg=C_CARD, relief="groove", bd=1)
        frame.pack(fill="x", padx=16, pady=(0, 4))
        canvas = tk.Canvas(frame, bg=C_CARD, height=height + 30, highlightthickness=0)
        canvas.pack(fill="x", padx=10, pady=8)

        def _draw(event=None) -> None:
            canvas.delete("all")
            cw = canvas.winfo_width() or 600
            if not data:
                return
            max_v = max(data.values()) or 1
            n     = len(data)
            bw    = max(10, (cw - 40) // n - 10)
            x     = 20
            for key, val in data.items():
                bar_color = colors.get(key, C_SELECTED)
                bh = int((val / max_v) * height) if max_v else 0
                y1, y2 = height - bh + 10, height + 10
                canvas.create_rectangle(x, y1, x + bw, y2, fill=bar_color, outline="")
                canvas.create_text(x + bw // 2, y2 + 4, text=key,
                                   font=(FONT, 7), anchor="n", fill=C_MUTED)
                if val > 0:
                    canvas.create_text(x + bw // 2, y1 - 2, text=str(val),
                                       font=(FONT, 7, "bold"), anchor="s", fill=bar_color)
                x += bw + 10

        canvas.bind("<Configure>", _draw)
        canvas.after(60, _draw)

    # ══════════════════════════════════════════════════════════════════════════
    # Tab: Agents
    # ══════════════════════════════════════════════════════════════════════════

    def _build_agents_tab(self, parent: tk.Frame) -> None:
        self._agents_parent = parent
        self._refresh_agents_tab()

    def _refresh_agents_tab(self) -> None:
        if not hasattr(self, "_agents_parent"):
            return
        parent = self._agents_parent
        for w in parent.winfo_children():
            w.destroy()

        a_canvas = tk.Canvas(parent, bg=C_BG, highlightthickness=0)
        a_scroll = ttk.Scrollbar(parent, orient="vertical", command=a_canvas.yview)
        a_canvas.configure(yscrollcommand=a_scroll.set)
        a_scroll.pack(side="right", fill="y")
        a_canvas.pack(fill="both", expand=True)

        inner = tk.Frame(a_canvas, bg=C_BG)
        aw = a_canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
            lambda e: a_canvas.configure(scrollregion=a_canvas.bbox("all")))
        a_canvas.bind("<Configure>",
            lambda e: a_canvas.itemconfig(aw, width=e.width))

        tk.Label(inner, text="Agent Roster & Ticket Distribution",
                 font=(FONT, 13, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=16, pady=(14, 2))
        tk.Label(inner, text="Auto-assigned by specialization match · work hours · current load",
                 font=(FONT, 9), bg=C_BG, fg=C_MUTED).pack(anchor="w", padx=16, pady=(0, 10))

        now_hour = datetime.now().hour

        for a in self.agents:
            available = a["work_start"] <= now_hour < a["work_end"]
            load_pct  = a["load"] / a["max_load"] if a["max_load"] else 0
            border    = C_SUCCESS if available else C_MUTED

            outer = tk.Frame(inner, bg=border)
            outer.pack(fill="x", padx=16, pady=4)
            card = tk.Frame(outer, bg=C_CARD)
            card.pack(fill="x", padx=2, pady=2)

            top = tk.Frame(card, bg=C_CARD)
            top.pack(fill="x", padx=12, pady=(10, 2))

            dot = "🟢" if available else "🔴"
            tk.Label(top, text=f"{dot}  {a['name']}",
                     font=(FONT, 11, "bold"), bg=C_CARD, fg=C_TEXT).pack(side="left")
            tk.Label(top, text=f"  {a['email']}  ({a['tz']}: {a['work_start']}:00–{a['work_end']}:00)",
                     font=(FONT, 9), bg=C_CARD, fg=C_MUTED).pack(side="left", padx=4)

            # Load bar
            lb_frame = tk.Frame(top, bg=C_CARD)
            lb_frame.pack(side="right")
            tk.Label(lb_frame, text=f"Load: {a['load']}/{a['max_load']}",
                     font=(FONT, 9), bg=C_CARD, fg=C_MUTED).pack(side="right", padx=(0, 6))
            bar_bg = tk.Frame(lb_frame, bg="#D0D8E4", width=80, height=10)
            bar_bg.pack(side="right", pady=6)
            bar_bg.pack_propagate(False)
            lc = C_DANGER if load_pct > 0.8 else (C_ACCENT if load_pct > 0.5 else C_SUCCESS)
            fill_w = max(1, int(80 * load_pct))
            tk.Frame(bar_bg, bg=lc, width=fill_w, height=10).place(x=0, y=0)

            spec_row = tk.Frame(card, bg=C_CARD)
            spec_row.pack(fill="x", padx=12, pady=(0, 8))
            for sp in a["specializations"]:
                tk.Label(spec_row, text=sp, font=(FONT, 8),
                         bg=C_HOVER, fg=C_SECONDARY, padx=6, pady=2).pack(side="left", padx=2)

            assigned = [t for t in self.tickets if t.get("assigned") == a["name"]]
            if assigned:
                tk.Label(card, text=f"→ {len(assigned)} ticket(s) assigned this session",
                         font=(FONT, 8, "italic"), bg=C_CARD, fg=C_SELECTED,
                         padx=12, pady=(0, 6), anchor="w").pack(fill="x")

        # Manual assignment for unassigned tickets
        unassigned = [t for t in self.tickets if not t.get("assigned")]
        if unassigned:
            tk.Label(inner, text="Unassigned Tickets",
                     font=(FONT, 11, "bold"), bg=C_BG, fg=C_PRIMARY).pack(anchor="w", padx=16, pady=(16, 4))
            for t in unassigned[:8]:
                row = tk.Frame(inner, bg=C_CARD, relief="groove", bd=1)
                row.pack(fill="x", padx=16, pady=2)
                pc, _ = PRIORITY_COLORS.get(t["priority"], (C_MUTED, C_CARD))
                tk.Label(row, text=t["priority"], font=(FONT, 8, "bold"),
                         bg=pc, fg="white", width=4, padx=4, pady=6).pack(side="left")
                tk.Label(row, text=f"{t['id']} · {t['desc'][:55]}",
                         font=(FONT, 9), bg=C_CARD, fg=C_TEXT,
                         anchor="w", padx=8).pack(side="left", fill="x", expand=True)
                avail_names = [
                    a["name"] for a in self.agents
                    if a["work_start"] <= now_hour < a["work_end"]
                    and a["load"] < a["max_load"]
                ]
                if avail_names:
                    var = tk.StringVar(value=avail_names[0])
                    ttk.Combobox(row, textvariable=var, values=avail_names,
                                 width=18, state="readonly", font=(FONT, 8)).pack(side="right", padx=4)
                    tk.Button(row, text="Assign", font=(FONT, 8),
                              bg=C_ACCENT, fg="white", relief="flat",
                              padx=6, pady=3, cursor="hand2",
                              command=lambda t=t, v=var: self._manual_assign(t, v.get()),
                              ).pack(side="right", padx=4)
        elif self.tickets:
            tk.Label(inner, text="✅  All tickets assigned.",
                     font=(FONT, 10), bg=C_BG, fg=C_SUCCESS).pack(anchor="w", padx=16, pady=(16, 4))

    def _manual_assign(self, ticket: dict, agent_name: str) -> None:
        ticket["assigned"] = agent_name
        for a in self.agents:
            if a["name"] == agent_name:
                a["load"] = min(a["load"] + 1, a["max_load"])
                break
        self._refresh_agents_tab()
        self._refresh_dashboard()
        self._update_recent()

    # ── Dashboard imports ──────────────────────────────────────────────────────

    def _download_tickets_template(self) -> None:
        dest = filedialog.asksaveasfilename(
            title="Save Tickets Template",
            initialfile="tickets_template.csv",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not dest:
            return
        rows = [
            ["description"],
            ["VPN shows 'Gateway not responding' — entire team cannot connect since 8 AM"],
            ["Okta MFA stopped working after phone replacement — locked out of all SSO apps"],
            ["Laptop blue-screens every time Visual Studio is opened after Windows update"],
            ["Need Adobe Acrobat Pro installed — required for daily document review workflow"],
            ["Production database throwing connection errors — all transactions blocked"],
            ["Need to add HP LaserJet on Floor 3 to workstation"],
            ["Outlook calendar not syncing — meetings missing since 9 AM"],
            ["Request new ergonomic chair via Service Portal"],
        ]
        try:
            with open(dest, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            messagebox.showinfo("Template Saved", f"Tickets template saved to:\n{dest}")
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))

    def _download_agents_template(self) -> None:
        dest = filedialog.asksaveasfilename(
            title="Save Agents Template",
            initialfile="agents_template.csv",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not dest:
            return
        rows = [
            ["name", "email", "specializations", "work_start", "work_end", "tz", "max_load"],
            ["Alice Johnson", "alice.johnson@cotiviti.com", "Network;Infrastructure;VPN", 8, 17, "ET", 5],
            ["Bob Smith", "bob.smith@cotiviti.com", "Auth/Identity;Okta;Active Directory", 9, 18, "ET", 5],
            ["Carol Martinez", "carol.martinez@cotiviti.com", "Hardware;Laptop;Peripherals", 7, 16, "ET", 5],
            ["David Patel", "david.patel@cotiviti.com", "Software;Database;Applications", 10, 19, "ET", 5],
            ["Emma Wilson", "emma.wilson@cotiviti.com", "Email/Calendar;Outlook;Exchange", 8, 17, "ET", 5],
        ]
        try:
            with open(dest, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            messagebox.showinfo("Template Saved", f"Agents template saved to:\n{dest}")
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))

    def _import_tickets_dashboard(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Tickets",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8") as f:
                lines = [row[0].strip() for row in csv.reader(f) if row and row[0].strip()]
            if not lines:
                messagebox.showwarning("Empty File", "No ticket descriptions found.")
                return
            if not self._client:
                self._prompt_api_key()
                return
            for row in self._bulk_tree.get_children():
                self._bulk_tree.delete(row)
            self._bulk_input.delete("1.0", "end")
            self._bulk_input.insert("1.0", "\n".join(lines))
            threading.Thread(target=self._bulk_thread, args=(lines,), daemon=True).start()
            messagebox.showinfo(
                "Import Started",
                f"Analyzing {len(lines)} ticket(s).\nSee Bulk Upload tab for live progress.",
            )
        except Exception as exc:
            messagebox.showerror("Import Error", str(exc))

    def _import_agents_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Agent Roster",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            agents: list[dict] = []
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    name = row.get("name", "").strip()
                    if not name:
                        continue
                    specs_raw = row.get("specializations", "").strip()
                    specs = [s.strip() for s in specs_raw.replace("|", ";").split(";") if s.strip()]
                    email = row.get("email", "").strip() or f"{name.lower().replace(' ', '.')}@cotiviti.com"
                    agents.append({
                        "id":             f"A{i:02d}",
                        "name":           name,
                        "email":          email,
                        "specializations": specs or ["Other"],
                        "work_start":     int(row.get("work_start", 8)),
                        "work_end":       int(row.get("work_end", 17)),
                        "tz":             row.get("tz", "ET").strip() or "ET",
                        "load":           0,
                        "max_load":       int(row.get("max_load", 5)),
                    })
            if not agents:
                messagebox.showwarning(
                    "No Agents Found",
                    "No valid rows found.\nMake sure the CSV has a 'name' header column.",
                )
                return
            self.agents = agents
            self._refresh_agents_tab()
            self._refresh_dashboard()
            messagebox.showinfo("Agents Imported", f"{len(agents)} agent(s) loaded successfully.")
        except Exception as exc:
            messagebox.showerror("Import Error", str(exc))


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    root = tk.Tk()
    ITTicketAssistant(root)
    root.mainloop()


if __name__ == "__main__":
    main()
