"""
Cotiviti — IT Ticket Triage Challenge
Match the Following: Incident · Generic Service Request · Service Catalog (Fulfillment Task)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import random

# ── Official Cotiviti Brand Palette ───────────────────────────────────────────
C_BG       = "#F5F3FF"   # Very light lavender background
C_PANEL    = "#31006F"   # Deep Purple — headers & overlays
C_CARD     = "#FFFFFF"   # Snow White — card faces
C_CARD_HVR = "#EDE9FF"   # Light Violet hover
C_SHADOW   = "#1A0040"   # Deep shadow
C_EDGE_LT  = "#C2BFE0"   # Light Violet — 3-D highlight edge

# Cotiviti primary type colours
C_PURPLE   = "#31006F"   # Deep Purple   → Incident
C_PINK     = "#EC008C"   # Lively Pink   → Generic Service Request
C_TEAL     = "#00AEFF"   # Sky Blue      → Service Catalog

# Secondary / highlight per type
C_P_BRIGHT = "#9579D3"   # Soothing Violet
C_K_BRIGHT = "#F49AC1"   # Light Pink
C_T_BRIGHT = "#13D0CA"   # Sea Green

# Light tinted surfaces per type
C_INC_SURF = "#EDE9FF"   # Light Purple surface
C_GSR_SURF = "#FFE8F5"   # Light Pink surface
C_CAT_SURF = "#E5F5FF"   # Light Blue surface

C_GOLD     = "#F98E2B"   # Orangesicle
C_WHITE    = "#FFFFFF"   # Snow White
C_TEXT     = "#31006F"   # Body text (Deep Purple on light bg)
C_MUTED    = "#7C77AD"   # Light Purple muted
C_SUCCESS  = "#13D0CA"   # Sea Green
C_DANGER   = "#CC0055"   # Dark Magenta
C_SEL      = "#9579D3"   # Soothing Violet — selected state
C_SUBHDR   = "#7C77AD"   # Light Purple sub-header
FONT       = "Segoe UI"
BTN_H      = 88   # fixed scenario card height px

# ── Ticket type definitions ────────────────────────────────────────────────────
TYPES: dict[str, dict] = {
    "Incident": {
        "emoji":   "🚨",
        "border":  C_PURPLE,
        "bright":  C_P_BRIGHT,
        "light":   C_INC_SURF,
        "desc":    "Unplanned disruption or service failure\nrequiring immediate emergency response",
        "kb_ref":  "KB-INC-001",
        "kb_body": (
            "An Incident is any unplanned event that interrupts or degrades an IT service. "
            "Log it immediately — no pre-approval required. The Break-Fix workflow triggers "
            "automatically to restore normal service as swiftly as operationally feasible.\n\n"
            "Key question: Was this working before and suddenly stopped?"
        ),
    },
    "Generic Service Request": {
        "emoji":   "📋",
        "border":  C_PINK,
        "bright":  C_PINK,       # Lively Pink — better contrast on light surface
        "light":   C_GSR_SURF,
        "desc":    "Request for info, advice, or items\nnot found in the Service Catalog",
        "kb_ref":  "KB-GSR-002",
        "kb_body": (
            "A Generic Service Request is raised when your need cannot be fulfilled by a standard "
            "Service Catalog item. IT will assess, scope, and route it appropriately.\n\n"
            "Key question: Is this a new need not listed in the Service Portal?"
        ),
    },
    "Service Catalog (Fulfillment Task)": {
        "emoji":   "📦",
        "border":  C_TEAL,
        "bright":  C_T_BRIGHT,
        "light":   C_CAT_SURF,
        "desc":    "Pre-approved standard items with automated\nworkflows — submitted via the Service Portal",
        "kb_ref":  "KB-CAT-003",
        "kb_body": (
            "Service Catalog items are standardised, pre-approved requests fulfilled via automated "
            "workflows in the Cotiviti Service Portal. Select, submit, and the system handles the rest.\n\n"
            "Key question: Is this item available and listed in the Service Portal?"
        ),
    },
}

PER_TYPE = 2
TOTAL    = PER_TYPE * len(TYPES)

CORRECT_QUIPS: list[str] = [
    "🎓  Textbook! HR has been notified — favourably, of course.",
    "⚡  Correct! The IT gods have updated your permanent record.",
    "🏆  Spot-on! Your ITIL certificate is practically printing itself.",
    "💡  Precisely! The Service Desk is slow-clapping in your honour.",
    "🌟  Outstanding! Your manager has been cc'd on this triumph.",
    "🎯  Bullseye! The Change Advisory Board is genuinely moved.",
    "🧠  Stellar recall! The CMDB has been ceremonially updated.",
    "🥂  Magnificent! Your ITSM prowess has been formally documented.",
    "✨  Exceptional! The on-call engineer weeps tears of pure joy.",
    "🎪  Superb! Even the SLA timer paused briefly to applaud.",
    "🚀  Correct! Proceed directly to the Service Desk hall of fame.",
    "📜  Well played! This classification will be studied for generations.",
]

WRONG_TIPS: list[str] = [
    "❌  Respectfully, no. Even the office printer is disappointed.",
    "🤔  A brief KB consultation is warranted, esteemed colleague.",
    "📋  Incident? GSR? Catalog? This is not a lucky dip, you know.",
    "💡  Incidents break things. GSRs request things. Catalog = portal.",
    "🧩  The Help Desk would like a word after class. No rush.",
    "😬  That was bold. Confidently wrong is still wrong, colleague.",
    "📎  The ITIL framework is watching. It is deeply unimpressed.",
    "🗃️  Your ticket would have been auto-rejected. Consider the KB.",
    "🤦  The on-call engineer received a sympathy notification.",
    "🚨  Incorrect classification. Dignity levels: slightly reduced.",
    "📉  The Change Board briefly lowered their expectations.",
    "😅  Fascinating choice. Incorrect, but truly fascinating.",
]

# ── Scenario bank ──────────────────────────────────────────────────────────────
ALL_SCENARIOS: list[dict] = [
    # Incidents
    {"s": "🖥️  My laptop won't power on at all",
     "t": "Incident",
     "kb": "Complete hardware failure causing total service loss — classic Break-Fix Incident."},
    {"s": "🌐  GlobalProtect VPN shows 'Gateway not responding'",
     "t": "Incident",
     "kb": "Unplanned network connectivity failure blocking remote access — Incident, not a request."},
    {"s": "📧  Outlook keeps crashing immediately on launch",
     "t": "Incident",
     "kb": "Unexpected application crash disrupting email — Incident. It was working fine yesterday."},
    {"s": "📧  All Outlook emails stuck in Outbox — cannot send or receive",
     "t": "Incident",
     "kb": "Mail flow disruption = unplanned service degradation = Incident."},
    {"s": "🔑  Okta MFA not working — locked out of all SSO applications",
     "t": "Incident",
     "kb": "Authentication system failure locking users out of all apps — critical Incident."},
    {"s": "🔌  Shared network drive disappeared suddenly for the whole team",
     "t": "Incident",
     "kb": "Sudden shared-storage loss affecting multiple users = Incident."},
    {"s": "💥  Database errors are blocking all staff transactions",
     "t": "Incident",
     "kb": "System-wide transaction failure impacting operations — major Incident."},
    {"s": "🌐  GlobalProtect VPN disconnects every few minutes",
     "t": "Incident",
     "kb": "Intermittent VPN drops degrade service quality — still an Incident."},
    {"s": "📧  Outlook calendar not syncing — meetings missing since yesterday",
     "t": "Incident",
     "kb": "Calendar sync failure = unplanned degradation = Incident. Someone's stand-up is in peril."},
    {"s": "📡  Internet completely down across Building B",
     "t": "Incident",
     "kb": "Site-wide internet outage = major Incident. Emergency escalation — immediately."},
    {"s": "🖥️  Unable to Launch Citrix Desktop",
     "t": "Incident",
     "kb": "Citrix session failure preventing virtual desktop access = Incident."},
    {"s": "🔓  Unable to login to my machine",
     "t": "Incident",
     "kb": "Workstation authentication failure = unplanned service disruption = Incident."},
    {"s": "📊  COB Tracker issues",
     "t": "Incident",
     "kb": "Business-critical tracker not functioning = Incident. Month-end close is in jeopardy."},
    {"s": "❌  Unable to access Decipher inside Citrix",
     "t": "Incident",
     "kb": "Application inaccessible within virtual desktop = unplanned disruption = Incident."},
    # Generic Service Requests
    {"s": "🗝️  Need access to an internal app NOT listed in the portal",
     "t": "Generic Service Request",
     "kb": "Non-catalogued access cannot be self-served — raise a GSR for IT to assess and provision."},
    {"s": "👥  Add a colleague to our existing AD security group",
     "t": "Generic Service Request",
     "kb": "AD group changes outside standard new-hire flows are not catalog items — GSR required."},
    {"s": "📂  Need Read only access for the SharePoint folder",
     "t": "Generic Service Request",
     "kb": "SharePoint folder access not listed in the portal requires IT assessment — raise a GSR for manual provisioning."},
    {"s": "🔑  Access to a shared mailbox — not in the Service Catalog",
     "t": "Generic Service Request",
     "kb": "If shared mailbox access isn't listed in the portal, raise a GSR for manual provisioning."},
    {"s": "🔍  Requesting access to WIZ scanner reports",
     "t": "Generic Service Request",
     "kb": "WIZ scanner report access is not a standard catalog item — raise a GSR for IT to assess and provision."},
    {"s": "💾  Request to increase Hard Disk space in Citrix",
     "t": "Generic Service Request",
     "kb": "Citrix storage changes require manual IT infrastructure assessment — raise a GSR."},
    # Service Catalog
    {"s": "💿  Request Adobe Acrobat Pro via the Service Desk Portal",
     "t": "Service Catalog (Fulfillment Task)",
     "kb": "Standard licensed software with automated install workflow in the portal = Catalog item."},
    {"s": "📦  Add a second monitor — available in the hardware catalog",
     "t": "Service Catalog (Fulfillment Task)",
     "kb": "Pre-approved hardware in the catalog — click, submit, collect."},
    {"s": "🔐  Request Audit Access for a compliance review (via portal)",
     "t": "Service Catalog (Fulfillment Task)",
     "kb": "Pre-approved audit access packages in the portal = Service Catalog Fulfillment Task."},
    {"s": "📧  Request for External Distribution list (via porta)",
     "t": "Service Catalog (Fulfillment Task)",
     "kb": "Distribution list creation is a standard pre-approved catalog item via the Service Portal."},
    {"s": "👤  Request Existing Role Based Access for New Hire (via porta)",
     "t": "Service Catalog (Fulfillment Task)",
     "kb": "Role-based access packages for new hires are pre-approved catalog items in the portal."},
]


def _show_kb_article(type_label: str) -> None:
    meta = TYPES[type_label]
    messagebox.showinfo(
        f"{meta['kb_ref']}  —  {type_label}",
        f"{meta['emoji']}  {type_label}\n\n{meta['kb_body']}\n\nReference: {meta['kb_ref']}",
    )


# ── Game ───────────────────────────────────────────────────────────────────────

class TicketMatchGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🎮 Cotiviti — IT Ticket Triage Challenge!")
        self.root.geometry("1080x760")
        self.root.configure(bg=C_BG)
        self.root.minsize(920, 640)

        self.score         = 0
        self.streak        = 0
        self.total_correct = 0
        self.total_wrong   = 0

        self.scenarios:     list[dict]      = []
        self.selected_left: int | None      = None
        self.left_matched:  set[int]        = set()
        self.left_buttons:  list[tk.Button] = []
        self.btn_outer:     list[tk.Frame]  = []   # outermost shadow/glow frame
        self.bucket_counts: dict[str, int]  = {t: 0 for t in TYPES}
        self.used_by_type:  dict[str, list] = {t: [] for t in TYPES}
        self.bucket_refs:   dict[str, dict] = {}

        self._draw_bg_stars()
        self._configure_styles()
        self._build_layout()
        self.show_welcome()

    # ── Starfield background ────────────────────────────────────────────────────

    def _draw_bg_stars(self) -> None:
        canvas = tk.Canvas(self.root, bg=C_BG, highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        star_cols = ["#2D2A6A", "#1E1B4B", "#3D3875", "#252060",
                     "#3A1A5A", "#0C2848", "#1D1550", "#1A1040"]
        for _ in range(70):
            x = random.randint(0, 1080)
            y = random.randint(0, 760)
            r = random.choice([1, 1, 1, 2, 2])
            canvas.create_oval(x, y, x + r * 2, y + r * 2,
                               fill=random.choice(star_cols), outline="")
        self.root.tk.call("lower", canvas._w)   # lower canvas below all packed widgets

    # ── Styles ─────────────────────────────────────────────────────────────────

    def _configure_styles(self) -> None:
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Coti.Horizontal.TProgressbar",
                    background=C_PINK, troughcolor=C_PANEL,
                    borderwidth=0, thickness=16)
        s.configure("Dark.Vertical.TScrollbar",
                    background=C_CARD, troughcolor=C_PANEL,
                    arrowcolor=C_WHITE, borderwidth=0)
        s.map("Dark.Vertical.TScrollbar",
              background=[("active", C_CARD_HVR)])

    # ── 3-D card helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _raise_card(parent: tk.Frame, bg: str,
                    shadow: str = C_SHADOW, highlight: str = C_EDGE_LT,
                    **pack_kw) -> tuple[tk.Frame, tk.Frame]:
        """Variable-height 3-D raised card (shadow right+bottom, highlight left+top)."""
        shd = tk.Frame(parent, bg=shadow)
        shd.pack(**pack_kw)
        hi = tk.Frame(shd, bg=highlight)
        hi.pack(fill="x", padx=(0, 4), pady=(0, 4))
        card = tk.Frame(hi, bg=bg)
        card.pack(fill="x", padx=(3, 0), pady=(3, 0))
        return shd, card

    @staticmethod
    def _raise_card_fill(parent: tk.Frame, bg: str,
                         shadow: str = C_SHADOW, highlight: str = C_EDGE_LT,
                         **pack_kw) -> tuple[tk.Frame, tk.Frame]:
        """Fill-both 3-D raised card (for fixed-size containers)."""
        shd = tk.Frame(parent, bg=shadow)
        shd.pack(**pack_kw)
        hi = tk.Frame(shd, bg=highlight)
        hi.pack(fill="both", expand=True, padx=(0, 4), pady=(0, 4))
        card = tk.Frame(hi, bg=bg)
        card.pack(fill="both", expand=True, padx=(3, 0), pady=(3, 0))
        return shd, card

    # ── Layout ─────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        # ── Header (3-D raised slab) ──
        hdr_shadow = tk.Frame(self.root, bg=C_SHADOW, height=82)
        hdr_shadow.pack(fill="x")
        hdr_shadow.pack_propagate(False)
        hdr = tk.Frame(hdr_shadow, bg=C_PANEL)
        hdr.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

        # Pink left accent bar
        tk.Frame(hdr, bg=C_PINK, width=7).pack(side="left", fill="y")
        # Cotiviti brand logo — multi-colour letter treatment
        logo_frame = tk.Frame(hdr, bg=C_PANEL)
        logo_frame.pack(side="left", padx=(12, 0))
        _lf = (FONT, 14, "bold")
        tk.Label(logo_frame, text="C",     font=_lf, bg=C_PANEL, fg="#FFFFFF").pack(side="left")
        tk.Label(logo_frame, text="O",     font=_lf, bg=C_PANEL, fg="#9579D3").pack(side="left")
        tk.Label(logo_frame, text="T",     font=_lf, bg=C_PANEL, fg="#FFFFFF").pack(side="left")
        tk.Label(logo_frame, text="I",     font=(FONT, 16, "bold"), bg=C_PANEL, fg="#EC008C").pack(side="left")
        tk.Label(logo_frame, text="VITI",  font=_lf, bg=C_PANEL, fg="#FFFFFF").pack(side="left")
        tk.Frame(hdr, bg=C_TEAL, width=3).pack(side="left", fill="y", padx=(10, 10))
        tk.Label(hdr, text="🎮  IT Ticket Triage Challenge",
                 font=(FONT, 18, "bold"), bg=C_PANEL, fg=C_WHITE).pack(side="left")

        # Score / streak — right side
        self.streak_lbl = tk.Label(hdr, text="", font=(FONT, 12, "bold"),
                                   bg=C_PANEL, fg=C_GOLD)
        self.streak_lbl.pack(side="right", padx=12)
        score_pill = tk.Frame(hdr, bg=C_SEL, padx=2, pady=2)
        score_pill.pack(side="right", padx=8)
        self.score_lbl = tk.Label(score_pill, text="⭐  0 / 100",
                                  font=(FONT, 13, "bold"),
                                  bg=C_SEL, fg=C_GOLD, padx=10, pady=4)
        self.score_lbl.pack()

        # ── Tri-colour accent stripe ──
        stripe = tk.Frame(self.root, height=4, bg=C_BG)
        stripe.pack(fill="x")
        for clr in [C_PINK, C_PURPLE, C_TEAL]:
            tk.Frame(stripe, bg=clr, height=4).pack(side="left", fill="y",
                                                    expand=True, ipadx=0)

        # ── Sub-header ──
        sub = tk.Frame(self.root, bg=C_SUBHDR, height=28)
        sub.pack(fill="x")
        sub.pack_propagate(False)
        tk.Label(sub, text="One Round  ·  6 Tickets  ·  Max 100 pts",
                 font=(FONT, 10, "bold"), bg=C_SUBHDR, fg=C_WHITE).pack(side="left",
                                                                         padx=16, pady=4)
        tk.Label(sub, text="Sort each scenario into the correct ticket type",
                 font=(FONT, 9), bg=C_SUBHDR, fg="#8B9BB4").pack(side="right", padx=16)

        # ── Column header labels ──
        col_hdr = tk.Frame(self.root, bg=C_BG)
        col_hdr.pack(fill="x", padx=16, pady=(10, 4))

        lhdr = tk.Frame(col_hdr, bg=C_PANEL)
        lhdr.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Frame(lhdr, bg=C_PINK, width=4).pack(side="left", fill="y")
        tk.Label(lhdr, text="📋  SCENARIOS", font=(FONT, 10, "bold"),
                 bg=C_PANEL, fg=C_WHITE, padx=10, pady=8, anchor="w").pack(
                     side="left", fill="x", expand=True)

        rhdr = tk.Frame(col_hdr, bg=C_PANEL)
        rhdr.pack(side="right", fill="x", expand=True)
        tk.Frame(rhdr, bg=C_TEAL, width=4).pack(side="left", fill="y")
        tk.Label(rhdr, text="🎫  TICKET TYPES", font=(FONT, 10, "bold"),
                 bg=C_PANEL, fg=C_WHITE, padx=10, pady=8, anchor="w").pack(
                     side="left", fill="x", expand=True)

        # ── Two-column body ──
        cols = tk.Frame(self.root, bg=C_BG)
        cols.pack(fill="both", expand=True, padx=16)

        self.left_col = tk.Frame(cols, bg=C_BG)
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_col = tk.Frame(cols, bg=C_BG)
        right_col.pack(side="right", fill="both", expand=True)
        self._build_buckets(right_col)

        # ── Feedback label ──
        self.feedback_lbl = tk.Label(
            self.root,
            text="👆  Click a scenario on the left, then click the matching ticket type!",
            font=(FONT, 11), bg=C_BG, fg=C_MUTED,
        )
        self.feedback_lbl.pack(pady=5)

        # ── Progress bar ──
        prg_row = tk.Frame(self.root, bg=C_BG)
        prg_row.pack(fill="x", padx=16, pady=(2, 8))
        tk.Label(prg_row, text="Progress:", font=(FONT, 9),
                 bg=C_BG, fg=C_MUTED).pack(side="left")
        self.prg_var = tk.DoubleVar(value=0)
        ttk.Progressbar(prg_row, variable=self.prg_var, maximum=TOTAL,
                        length=360, style="Coti.Horizontal.TProgressbar").pack(
                            side="left", padx=8)
        self.prg_lbl = tk.Label(prg_row, text=f"0 / {TOTAL}",
                                font=(FONT, 9), bg=C_BG, fg=C_MUTED)
        self.prg_lbl.pack(side="left")

    def _build_buckets(self, parent: tk.Frame) -> None:
        for label, meta in TYPES.items():
            # ── 3-D card: shadow → type-coloured border → content ──
            shadow = tk.Frame(parent, bg=C_SHADOW)
            shadow.pack(fill="x", pady=(0, 10))

            border = tk.Frame(shadow, bg=meta["border"])
            border.pack(fill="x", padx=(0, 5), pady=(0, 5))

            # Brighter highlight strip (left+top edge of inner card)
            hi = tk.Frame(border, bg=meta["bright"])
            hi.pack(fill="x", padx=(4, 0), pady=(4, 0))

            inner = tk.Frame(hi, bg=meta["light"])
            inner.pack(fill="x", padx=(1, 0), pady=(1, 0))

            # Content
            title_row = tk.Frame(inner, bg=meta["light"])
            title_row.pack(fill="x", padx=12, pady=(10, 3))

            title_lbl = tk.Label(title_row, text=f"{meta['emoji']}  {label}",
                                 font=(FONT, 11, "bold"),
                                 bg=meta["light"], fg=meta["bright"], anchor="w")
            title_lbl.pack(side="left", fill="x", expand=True)

            dots_lbl = tk.Label(title_row, text=" ".join(["○"] * PER_TYPE),
                                font=(FONT, 13), bg=meta["light"], fg=C_MUTED)
            dots_lbl.pack(side="right", padx=4)

            desc_lbl = tk.Label(inner, text=meta["desc"],
                                font=(FONT, 9), bg=meta["light"], fg=C_MUTED,
                                justify="left", anchor="w")
            desc_lbl.pack(fill="x", padx=12, pady=(0, 5))

            ref_lbl = tk.Label(inner, text=f"📎  {meta['kb_ref']}",
                               font=(FONT, 8, "bold"), bg=meta["light"],
                               fg=meta["bright"], cursor="hand2")
            ref_lbl.pack(anchor="w", padx=12, pady=(0, 9))
            ref_lbl.bind("<Button-1>", lambda _e, lb=label: _show_kb_article(lb))

            for w in (shadow, border, hi, inner, title_row, title_lbl, dots_lbl, desc_lbl):
                w.bind("<Button-1>", lambda _e, lb=label: self.click_bucket(lb))

            self.bucket_refs[label] = {
                "shadow":   shadow,
                "border":   border,
                "inner":    inner,
                "dots_lbl": dots_lbl,
                "meta":     meta,
            }

    # ── Welcome screen ─────────────────────────────────────────────────────────

    def show_welcome(self) -> None:
        ov = self._overlay(680, 580, C_BG)
        ov.title("Welcome!")

        # Banner
        banner_shd = tk.Frame(ov, bg=C_SHADOW)
        banner_shd.pack(fill="x")
        banner = tk.Frame(banner_shd, bg=C_PANEL)
        banner.pack(fill="x", padx=(0, 3), pady=(0, 4))
        # tri-colour stripe
        stp = tk.Frame(banner, height=5, bg=C_PANEL)
        stp.pack(fill="x")
        for clr in [C_PINK, C_PURPLE, C_TEAL]:
            tk.Frame(stp, bg=clr, height=5).pack(side="left", fill="y", expand=True)
        tk.Label(banner, text="🎮  IT Ticket Triage Challenge!",
                 font=(FONT, 21, "bold"), bg=C_PANEL, fg=C_GOLD).pack(pady=(14, 4))
        tk.Label(banner, text="Sort all 6 scenarios correctly — earn up to 100 pts!",
                 font=(FONT, 11), bg=C_PANEL, fg=C_WHITE).pack(pady=(0, 12))

        # Three square 3-D type cards
        CARD_SZ = 185
        cards_row = tk.Frame(ov, bg=C_BG)
        cards_row.pack(pady=14)
        for label, meta in TYPES.items():
            # shadow → bright highlight → dark surface
            s_frame = tk.Frame(cards_row, bg=C_SHADOW,
                               width=CARD_SZ + 6, height=CARD_SZ + 6)
            s_frame.pack(side="left", padx=8)
            s_frame.pack_propagate(False)
            hi_frame = tk.Frame(s_frame, bg=meta["bright"])
            hi_frame.pack(fill="both", expand=True, padx=(0, 5), pady=(0, 5))
            card = tk.Frame(hi_frame, bg=meta["light"])
            card.pack(fill="both", expand=True, padx=(4, 0), pady=(4, 0))

            tk.Label(card, text=meta["emoji"], font=(FONT, 30),
                     bg=meta["light"]).pack(pady=(18, 4))
            tk.Label(card, text=label, font=(FONT, 9, "bold"),
                     bg=meta["light"], fg=meta["bright"],
                     wraplength=160, justify="center").pack(pady=(0, 4))
            tk.Label(card, text=meta["desc"],
                     font=(FONT, 8), bg=meta["light"], fg=C_MUTED,
                     wraplength=160, justify="center").pack()
            lnk = tk.Label(card, text=f"📎  {meta['kb_ref']}",
                           font=(FONT, 8, "bold", "underline"),
                           bg=meta["light"], fg=meta["bright"], cursor="hand2")
            lnk.pack(pady=(8, 12))
            lnk.bind("<Button-1>", lambda _e, lb=label: _show_kb_article(lb))

        # Score bar
        sbar_shd = tk.Frame(ov, bg=C_SHADOW)
        sbar_shd.pack(fill="x", padx=16)
        sbar = tk.Frame(sbar_shd, bg=C_SUBHDR)
        sbar.pack(fill="x", padx=(0, 3), pady=(0, 3))
        tk.Label(sbar, text="⭐ 10 pts / match   🔥 +2 pts per streak   🌟 +10 Flawless bonus",
                 font=(FONT, 10, "bold"), bg=C_SUBHDR, fg=C_GOLD, pady=8).pack()

        btn_shd = tk.Frame(ov, bg=C_SHADOW)
        btn_shd.pack(pady=14)
        tk.Button(btn_shd, text="  Let's Play! →  ", font=(FONT, 13, "bold"),
                  bg=C_PINK, fg=C_WHITE, padx=20, pady=10,
                  cursor="hand2", relief="flat", activebackground=C_K_BRIGHT,
                  command=lambda: [ov.destroy(), self.start_round()]).pack(
                      padx=(0, 4), pady=(0, 4))

    # ── Round lifecycle ────────────────────────────────────────────────────────

    def start_round(self) -> None:
        for w in self.left_col.winfo_children():
            w.destroy()
        self.selected_left = None
        self.left_matched.clear()
        self.left_buttons.clear()
        self.btn_outer.clear()
        self.bucket_counts = {t: 0 for t in TYPES}

        for refs in self.bucket_refs.values():
            meta = refs["meta"]
            refs["shadow"].config(bg=C_SHADOW)
            refs["border"].config(bg=meta["border"])
            refs["inner"].config(bg=meta["light"])
            refs["dots_lbl"].config(text=" ".join(["○"] * PER_TYPE),
                                    fg=C_MUTED, font=(FONT, 13))

        self.scenarios = []
        for type_label in TYPES:
            pool = [i for i, sc in enumerate(ALL_SCENARIOS)
                    if sc["t"] == type_label and i not in self.used_by_type[type_label]]
            if len(pool) < PER_TYPE:
                self.used_by_type[type_label].clear()
                pool = [i for i, sc in enumerate(ALL_SCENARIOS) if sc["t"] == type_label]
            chosen = random.sample(pool, PER_TYPE)
            self.used_by_type[type_label].extend(chosen)
            self.scenarios.extend([ALL_SCENARIOS[i] for i in chosen])

        random.shuffle(self.scenarios)

        for i, sc in enumerate(self.scenarios):
            # ── 3-D scenario card: shadow → highlight → face ──
            outer = tk.Frame(self.left_col, bg=C_SHADOW, height=BTN_H + 7)
            outer.pack(fill="x", pady=3)
            outer.pack_propagate(False)

            hi = tk.Frame(outer, bg=C_EDGE_LT)
            hi.pack(fill="both", expand=True, padx=(0, 5), pady=(0, 5))

            face = tk.Frame(hi, bg=C_CARD)
            face.pack(fill="both", expand=True, padx=(3, 0), pady=(3, 0))

            # Thin left accent strip
            accent = tk.Frame(face, bg=C_EDGE_LT, width=4)
            accent.pack(side="left", fill="y")

            btn = tk.Button(
                face, text=sc["s"],
                font=(FONT, 11), bg=C_CARD, fg=C_TEXT,
                activebackground=C_SEL, activeforeground=C_WHITE,
                relief="flat", bd=0, cursor="hand2",
                wraplength=420, justify="left", anchor="w",
                padx=10, pady=6,
                command=lambda idx=i: self.click_left(idx),
            )
            btn.pack(side="left", fill="both", expand=True)
            btn.bind("<Enter>",
                     lambda _, b=btn, o=outer:
                     (b.config(bg=C_CARD_HVR), o.config(bg=C_EDGE_LT))
                     if b.cget("bg") == C_CARD else None)
            btn.bind("<Leave>",
                     lambda _, b=btn, o=outer:
                     (b.config(bg=C_CARD), o.config(bg=C_SHADOW))
                     if b.cget("bg") == C_CARD_HVR else None)

            self.left_buttons.append(btn)
            self.btn_outer.append(outer)

        self.prg_var.set(0)
        self.prg_lbl.config(text=f"0 / {TOTAL}")
        self.feedback_lbl.config(
            text="👆  Click a scenario on the left, then click the matching ticket type!",
            fg=C_MUTED,
        )

    # ── Click: scenario ────────────────────────────────────────────────────────

    def click_left(self, idx: int) -> None:
        if idx in self.left_matched:
            return
        if self.selected_left == idx:
            self.left_buttons[idx].config(bg=C_CARD, fg=C_TEXT)
            self.btn_outer[idx].config(bg=C_SHADOW)
            self.selected_left = None
            self.feedback_lbl.config(
                text="👆  Click a scenario, then click the matching ticket type!",
                fg=C_MUTED,
            )
            return
        if self.selected_left is not None:
            self.left_buttons[self.selected_left].config(bg=C_CARD, fg=C_TEXT)
            self.btn_outer[self.selected_left].config(bg=C_SHADOW)
        self.selected_left = idx
        self.left_buttons[idx].config(bg=C_SEL, fg=C_WHITE)
        self.btn_outer[idx].config(bg=C_PINK)       # hot-pink glow halo
        self.feedback_lbl.config(
            text="✅  Now click the matching ticket type on the right →",
            fg=C_WHITE,
        )

    # ── Click: bucket ──────────────────────────────────────────────────────────

    def click_bucket(self, bucket_label: str) -> None:
        if self.bucket_counts.get(bucket_label, 0) >= PER_TYPE:
            return
        if self.selected_left is None:
            self.feedback_lbl.config(text="⚠️  First click a scenario on the left!", fg=C_DANGER)
            return
        if self.scenarios[self.selected_left]["t"] == bucket_label:
            self._on_correct(self.selected_left, bucket_label)
        else:
            self._on_wrong(self.selected_left, bucket_label)

    # ── Correct ────────────────────────────────────────────────────────────────

    def _on_correct(self, l_idx: int, bucket_label: str) -> None:
        bonus           = self.streak * 2
        pts             = 10 + bonus
        self.score      = min(self.score + pts, 100)
        self.streak    += 1
        self.total_correct += 1
        self.left_matched.add(l_idx)
        self.bucket_counts[bucket_label] += 1
        self.selected_left = None

        meta = TYPES[bucket_label]
        # Card glows with the matched type's vivid colour
        self.btn_outer[l_idx].config(bg=meta["border"])
        lb = self.left_buttons[l_idx]
        lb.config(bg=meta["light"], fg=meta["bright"],
                  relief="flat", state="disabled",
                  text=f"✓  {lb.cget('text')}")

        count = self.bucket_counts[bucket_label]
        refs  = self.bucket_refs[bucket_label]
        if count >= PER_TYPE:
            refs["shadow"].config(bg=C_SUCCESS)
            refs["border"].config(bg=C_SUCCESS)
            refs["inner"].config(bg="#063D2A")
            refs["dots_lbl"].config(text="✅  All matched!", fg=C_SUCCESS,
                                    font=(FONT, 10, "bold"))
        else:
            refs["dots_lbl"].config(
                text=" ".join(["●"] * count + ["○"] * (PER_TYPE - count)))

        streak_tag = ""
        if self.streak == 2:
            streak_tag = "  🔥 2x Streak — bonus points issued with great enthusiasm!"
        elif self.streak == 3:
            streak_tag = "  ⚡ 3x Streak — the Change Board is genuinely applauding!"
        elif self.streak >= 4:
            streak_tag = "  💥 Unstoppable Streak — legend status duly noted!"

        self.streak_lbl.config(text=f"🔥 ×{self.streak}" if self.streak > 1 else "")
        self.score_lbl.config(text=f"⭐  {self.score} / 100")
        self.feedback_lbl.config(
            text=f"{random.choice(CORRECT_QUIPS)}  +{pts} pts{streak_tag}",
            fg=C_SUCCESS,
        )

        done = len(self.left_matched)
        self.prg_var.set(done)
        self.prg_lbl.config(text=f"{done} / {TOTAL}")

        if done == TOTAL:
            self.root.after(900, self._round_done)

    # ── Wrong ──────────────────────────────────────────────────────────────────

    def _on_wrong(self, l_idx: int, bucket_label: str) -> None:
        self.streak = 0
        self.total_wrong += 1
        self.streak_lbl.config(text="")

        lb   = self.left_buttons[l_idx]
        refs = self.bucket_refs[bucket_label]

        self.btn_outer[l_idx].config(bg=C_DANGER)
        lb.config(bg=C_DANGER, fg=C_WHITE)
        refs["shadow"].config(bg=C_DANGER)
        self.feedback_lbl.config(text=random.choice(WRONG_TIPS), fg=C_DANGER)

        def _reset() -> None:
            lb.config(bg=C_SEL, fg=C_WHITE)
            self.btn_outer[l_idx].config(bg=C_PINK)
            refs["shadow"].config(bg=C_SHADOW)

        self.root.after(800, _reset)

    # ── Round done ─────────────────────────────────────────────────────────────

    def _round_done(self) -> None:
        is_perfect = self.total_wrong == 0
        if is_perfect:
            self.score = min(self.score + 10, 100)

        ov = self._overlay(780, 720, C_BG)
        ov.title("Challenge Complete!")

        # ── Score banner ──
        ban_shd = tk.Frame(ov, bg=C_SHADOW)
        ban_shd.pack(fill="x")
        ban = tk.Frame(ban_shd, bg=C_PANEL)
        ban.pack(fill="x", padx=(0, 3), pady=(0, 4))
        stp = tk.Frame(ban, height=5, bg=C_PANEL)
        stp.pack(fill="x")
        for clr in [C_PINK, C_PURPLE, C_TEAL]:
            tk.Frame(stp, bg=clr, height=5).pack(side="left", fill="y", expand=True)
        tk.Label(ban, text="🏆  Challenge Complete!",
                 font=(FONT, 22, "bold"), bg=C_PANEL, fg=C_GOLD).pack(pady=(14, 4))

        # Score pill
        pill_shd = tk.Frame(ban, bg=C_SHADOW)
        pill_shd.pack(pady=2)
        pill = tk.Frame(pill_shd, bg=C_SEL)
        pill.pack(padx=(0, 4), pady=(0, 4))
        tk.Label(pill, text=f"⭐  {self.score} / 100 pts",
                 font=(FONT, 18, "bold"), bg=C_SEL, fg=C_GOLD,
                 padx=20, pady=6).pack()

        if self.score == 100:
            grade, grade_fg = "🌟 PERFECT SCORE — Legendary Ticket Maestro status achieved!", C_TEAL
        elif self.score >= 80:
            grade, grade_fg = "🥇 Excellent — Top Tier ITSM talent confirmed!", C_P_BRIGHT
        elif self.score >= 60:
            grade, grade_fg = "🥈 Good effort — the KB Review below awaits your attention.", C_GOLD
        else:
            grade, grade_fg = "🥉 Keep practising — the printer forgives you. Probably.", C_K_BRIGHT

        tk.Label(ban, text=grade, font=(FONT, 11, "bold"),
                 bg=C_PANEL, fg=grade_fg).pack(pady=(6, 4))
        notice_text = ("🌟 FLAWLESS — Zero mistakes! +10 Flawless Bonus awarded!"
                       if is_perfect else f"Wrong attempts: {self.total_wrong}")
        tk.Label(ban, text=notice_text, font=(FONT, 10),
                 bg=C_PANEL, fg=C_SUCCESS if is_perfect else C_DANGER).pack(pady=(0, 10))

        # ── KB section header ──
        tk.Label(ov, text="📚  KNOWLEDGE BASE REVIEW",
                 font=(FONT, 12, "bold"), bg=C_SUBHDR, fg=C_WHITE,
                 anchor="w", padx=16, pady=6).pack(fill="x")

        # ── Three 3-D KB cards (natural height — no clipping) ──
        KB_SZ_W = 218
        type_row = tk.Frame(ov, bg=C_BG)
        type_row.pack(pady=8)
        for label, meta in TYPES.items():
            s_f = tk.Frame(type_row, bg=C_SHADOW, width=KB_SZ_W + 5)
            s_f.pack(side="left", padx=5)
            hi_f = tk.Frame(s_f, bg=meta["bright"])
            hi_f.pack(fill="x", padx=(0, 4), pady=(0, 4))
            c_f = tk.Frame(hi_f, bg=meta["light"])
            c_f.pack(fill="x", padx=(3, 0), pady=(3, 0))
            # Coloured header strip
            h_row = tk.Frame(c_f, bg=meta["border"])
            h_row.pack(fill="x")
            tk.Label(h_row, text=f"{meta['emoji']}  {meta['kb_ref']}",
                     font=(FONT, 10, "bold"), bg=meta["border"], fg=C_WHITE,
                     padx=8, pady=5).pack(side="left")
            # Body text — readable size, high-contrast colour
            tk.Label(c_f, text=meta["kb_body"],
                     font=(FONT, 9), bg=meta["light"], fg="#E2E8F0",
                     wraplength=196, justify="left").pack(anchor="w", padx=8, pady=(6, 2))
            # Clickable link
            lnk = tk.Label(c_f, text="📖  View KB Article",
                           font=(FONT, 9, "bold", "underline"),
                           bg=meta["light"], fg=meta["bright"], cursor="hand2")
            lnk.pack(anchor="w", padx=8, pady=(2, 8))
            lnk.bind("<Button-1>", lambda _e, lb=label: _show_kb_article(lb))

        # ── Scrollable scenario review ──
        tk.Label(ov, text="Scenario-by-Scenario Review",
                 font=(FONT, 10, "bold"), bg=C_BG, fg=C_WHITE,
                 anchor="w", padx=16).pack(fill="x", pady=(4, 2))

        f_outer = tk.Frame(ov, bg=C_BG)
        f_outer.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        canvas    = tk.Canvas(f_outer, bg=C_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(f_outer, orient="vertical", command=canvas.yview,
                                  style="Dark.Vertical.TScrollbar")
        i_frame   = tk.Frame(canvas, bg=C_BG)

        i_frame.bind("<Configure>",
                     lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=i_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        for sc in self.scenarios:
            meta = TYPES[sc["t"]]
            # 3-D scenario row in review
            row_shd = tk.Frame(i_frame, bg=meta["border"])
            row_shd.pack(fill="x", pady=2, padx=2)
            row = tk.Frame(row_shd, bg=meta["light"])
            row.pack(fill="x", padx=(4, 0), pady=(0, 0))
            tk.Label(row, text=f"{meta['emoji']}  {sc['s'].strip()}",
                     font=(FONT, 9, "bold"),
                     bg=meta["light"], fg=meta["bright"],
                     anchor="w", wraplength=700).pack(fill="x", padx=10, pady=(4, 0))
            tk.Label(row, text=f"   → {sc['t']}  |  💡 {sc['kb']}",
                     font=(FONT, 9), bg=meta["light"], fg="#CBD5E1",
                     anchor="w", wraplength=700, justify="left").pack(
                         fill="x", padx=10, pady=(1, 6))

        # ── KB Quick-ref pills ──
        pills_shd = tk.Frame(ov, bg=C_SHADOW)
        pills_shd.pack(fill="x", pady=(4, 0))
        pills = tk.Frame(pills_shd, bg=C_PANEL)
        pills.pack(fill="x", padx=(0, 3), pady=(0, 3))
        tk.Label(pills, text="📎  Quick KB References:",
                 font=(FONT, 9, "bold"), bg=C_PANEL, fg=C_WHITE).pack(
                     side="left", padx=12, pady=7)
        for label, meta in TYPES.items():
            p_shd = tk.Frame(pills, bg=C_SHADOW)
            p_shd.pack(side="left", padx=4, pady=5)
            pill_btn = tk.Label(p_shd,
                                text=f"  {meta['emoji']} {meta['kb_ref']}  ",
                                font=(FONT, 9, "bold"),
                                bg=meta["border"], fg=C_WHITE,
                                cursor="hand2", padx=6, pady=4)
            pill_btn.pack(padx=(0, 3), pady=(0, 3))
            pill_btn.bind("<Button-1>", lambda _e, lb=label: _show_kb_article(lb))

        # ── Play Again ──
        btn_shd = tk.Frame(ov, bg=C_SHADOW)
        btn_shd.pack(pady=8)
        tk.Button(btn_shd, text="  Play Again  ", font=(FONT, 13, "bold"),
                  bg=C_PINK, fg=C_WHITE, padx=20, pady=10,
                  cursor="hand2", relief="flat", activebackground=C_K_BRIGHT,
                  command=lambda: [ov.destroy(), self._restart()]).pack(
                      padx=(0, 4), pady=(0, 4))

    # ── Restart ────────────────────────────────────────────────────────────────

    def _restart(self) -> None:
        self.score         = 0
        self.streak        = 0
        self.total_correct = 0
        self.total_wrong   = 0
        for t in self.used_by_type:
            self.used_by_type[t].clear()
        self.score_lbl.config(text="⭐  0 / 100")
        self.streak_lbl.config(text="")
        self.start_round()

    def _overlay(self, w: int, h: int, bg: str = C_BG) -> tk.Toplevel:
        ov = tk.Toplevel(self.root)
        ov.configure(bg=bg)
        ov.resizable(False, False)
        ov.transient(self.root)
        ov.grab_set()
        self.root.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - w) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        ov.geometry(f"{w}x{h}+{rx}+{ry}")
        return ov


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    root = tk.Tk()
    TicketMatchGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
