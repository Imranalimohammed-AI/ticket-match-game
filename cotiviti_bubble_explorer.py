"""
Cotiviti — Service Portal Bubble Explorer
Click bubbles to discover: Service Catalog item, Incident, or Generic Service Request?
"""
import math
import random
import tkinter as tk
from tkinter import ttk

# ── Brand palette (identical to cotiviti_ticket_match.py) ─────────────────────
C_BG       = "#F5F3FF"
C_PANEL    = "#31006F"
C_SHADOW   = "#1A0040"
C_PURPLE   = "#31006F"
C_PINK     = "#EC008C"
C_TEAL     = "#00AEFF"
C_P_BRIGHT = "#9579D3"
C_K_BRIGHT = "#F49AC1"
C_T_BRIGHT = "#13D0CA"
C_INC_SURF = "#EDE9FF"
C_GSR_SURF = "#FFE8F5"
C_CAT_SURF = "#E5F5FF"
C_GOLD     = "#F98E2B"
C_WHITE    = "#FFFFFF"
C_TEXT     = "#31006F"
C_MUTED    = "#7C77AD"
C_SUCCESS  = "#13D0CA"
C_DANGER   = "#CC0055"
C_SEL      = "#9579D3"
C_SUBHDR   = "#7C77AD"
FONT       = "Segoe UI"

BUBBLE_R = 62   # bubble radius in pixels

# ── Per-type visual metadata ───────────────────────────────────────────────────
TYPE_META: dict[str, dict] = {
    "incident": {
        "fill":       C_INC_SURF,
        "ring":       C_PURPLE,
        "ring_hvr":   C_P_BRIGHT,
        "text_fg":    C_PURPLE,
        "disc_ring":  C_DANGER,
        "stamp_txt":  "✗  Not a Catalog",
        "stamp_fg":   C_DANGER,
        "panel_bg":   "#240052",
        "panel_fg":   "#C9AAFF",
        "type_lbl":   "🚨  INCIDENT  —  NOT a Service Catalog item",
        "verdict":    "✗  This is NOT a Service Catalog item.",
        "verdict_fg": C_DANGER,
    },
    "gsr": {
        "fill":       C_GSR_SURF,
        "ring":       C_PINK,
        "ring_hvr":   C_K_BRIGHT,
        "text_fg":    "#A0004F",
        "disc_ring":  C_PINK,
        "stamp_txt":  "✗  Not a Catalog",
        "stamp_fg":   C_PINK,
        "panel_bg":   "#450020",
        "panel_fg":   C_K_BRIGHT,
        "type_lbl":   "📋  GENERIC SERVICE REQUEST  —  NOT a Service Catalog item",
        "verdict":    "✗  This is NOT a Service Catalog item.",
        "verdict_fg": C_PINK,
    },
    "catalog": {
        "fill":       C_CAT_SURF,
        "ring":       C_TEAL,
        "ring_hvr":   C_T_BRIGHT,
        "text_fg":    C_TEXT,
        "disc_ring":  C_SUCCESS,
        "stamp_txt":  "✓  Catalog",
        "stamp_fg":   C_SUCCESS,
        "panel_bg":   "#003040",
        "panel_fg":   C_T_BRIGHT,
        "type_lbl":   "📦  SERVICE CATALOG (Fulfillment Task)  —  Submit via the Service Portal",
        "verdict":    "✓  This IS a Service Catalog item.",
        "verdict_fg": C_SUCCESS,
    },
}

# ── All 15 portal items from the screenshot ────────────────────────────────────
BUBBLE_DEFS: list[dict] = [
    {
        "name":   "Report An\nIncident\nOr Outage",
        "type":   "incident",
        "emoji":  "🚨",
        "detail": (
            "An INCIDENT is any unplanned event that interrupts or degrades an IT service.\n"
            "Log it immediately — no pre-approval required. The Break-Fix workflow triggers\n"
            "automatically to restore normal service as swiftly as possible."
        ),
    },
    {
        "name":   "Generic\nService\nRequest",
        "type":   "gsr",
        "emoji":  "📋",
        "detail": (
            "A GENERIC SERVICE REQUEST is raised when your need cannot be fulfilled by a\n"
            "standard Service Catalog item. IT will assess, scope, and route it appropriately.\n"
            "Use this only when your item is NOT already listed in the Service Portal."
        ),
    },
    {
        "name":   "Report\nSecurity/\nPrivacy Event",
        "type":   "catalog",
        "emoji":  "🔒",
        "detail": (
            "Report potential security or privacy events via the Service Portal.\n"
            "Pre-approved catalog form with automated routing to the security team\n"
            "for assessment and response."
        ),
    },
    {
        "name":   "Application &\nAccount\nServices",
        "type":   "catalog",
        "emoji":  "⚙️",
        "detail": (
            "Pre-approved requests for application access and account services.\n"
            "Submit via the Service Portal — the automated workflow handles\n"
            "provisioning and approval routing."
        ),
    },
    {
        "name":   "Infrastructure\nServices",
        "type":   "catalog",
        "emoji":  "☁️",
        "detail": (
            "Standard infrastructure support and management service requests.\n"
            "Pre-approved catalog item — select it in the Service Portal\n"
            "and the workflow takes care of the rest."
        ),
    },
    {
        "name":   "Security\nServices",
        "type":   "catalog",
        "emoji":  "🛡️",
        "detail": (
            "Various security catalog items including consultation and advisory services.\n"
            "Pre-approved and available in the Service Portal —\n"
            "submit your request for automated routing."
        ),
    },
    {
        "name":   "Software\nServices",
        "type":   "catalog",
        "emoji":  "💿",
        "detail": (
            "Order standard software for business use via the Service Portal.\n"
            "Pre-approved catalog item with automated provisioning —\n"
            "no manual IT intervention required."
        ),
    },
    {
        "name":   "Facilities",
        "type":   "catalog",
        "emoji":  "🏢",
        "detail": (
            "Facilities management service requests via the Service Portal.\n"
            "Pre-approved catalog item — submit your request and the\n"
            "workflow routes it to the Facilities team automatically."
        ),
    },
    {
        "name":   "Project\nIngestion",
        "type":   "catalog",
        "emoji":  "📥",
        "detail": (
            "Infrastructure Project Request Form for new project intake.\n"
            "Pre-approved catalog item — submit via the Service Portal\n"
            "for review and ingestion into the project pipeline."
        ),
    },
    {
        "name":   "JiraET\nAccess",
        "type":   "catalog",
        "emoji":  "🗃️",
        "detail": (
            "Request licenses for enhanced user roles and access in JiraET and Confluence.\n"
            "Pre-approved catalog item — select the access level you need\n"
            "and submit via the Service Portal."
        ),
    },
    {
        "name":   "JiraET\nAssignment\nGroup Request",
        "type":   "catalog",
        "emoji":  "👥",
        "detail": (
            "Create, modify, or retire JiraET User Access Groups.\n"
            "Pre-approved catalog form — submit via the Service Portal\n"
            "for automated processing."
        ),
    },
    {
        "name":   "JiraET\nEnhancement",
        "type":   "catalog",
        "emoji":  "💡",
        "detail": (
            "Add new or update current workflows and processes in JiraET.\n"
            "Submit an enhancement request via the Service Portal for the\n"
            "JiraET team to assess and implement."
        ),
    },
    {
        "name":   "Contact the\nJiraET Team",
        "type":   "catalog",
        "emoji":  "💬",
        "detail": (
            "Get in touch directly with the JiraET support team.\n"
            "Available as a catalog item in the Service Portal —\n"
            "submit your enquiry for a response."
        ),
    },
    {
        "name":   "Production\nOperations",
        "type":   "catalog",
        "emoji":  "🔑",
        "detail": (
            "Centralised service request management for Production Operations.\n"
            "Pre-approved catalog item — submit via the Service Portal\n"
            "for handling by the Production Ops team."
        ),
    },
    {
        "name":   "Hardware\nServices",
        "type":   "catalog",
        "emoji":  "🖥️",
        "detail": (
            "Request hardware for business use via the Service Portal.\n"
            "Pre-approved catalog item — select the hardware you need,\n"
            "submit, and track delivery through the portal."
        ),
    },
]

TOTAL_BUBBLES = len(BUBBLE_DEFS)


# ── Bubble ─────────────────────────────────────────────────────────────────────

class Bubble:
    """One floating bubble drawn on a Canvas."""

    def __init__(self, canvas: tk.Canvas, defn: dict, cx: float, cy: float) -> None:
        self.canvas     = canvas
        self.defn       = defn
        self.x          = cx
        self.y          = cy
        speed           = random.uniform(0.55, 1.3)
        angle           = random.uniform(0, 2 * math.pi)
        self.dx         = speed * math.cos(angle)
        self.dy         = speed * math.sin(angle)
        self.discovered = False
        self.meta       = TYPE_META[defn["type"]]
        self._create_items()

    def _create_items(self) -> None:
        m = self.meta
        x, y, r = self.x, self.y, BUBBLE_R

        # Hover glow ring (larger, lighter ring behind main oval)
        self._glow = self.canvas.create_oval(
            x-r-6, y-r-6, x+r+6, y+r+6,
            fill="", outline=m["ring_hvr"], width=2, state="hidden",
        )
        # Main bubble oval
        self._oval = self.canvas.create_oval(
            x-r, y-r, x+r, y+r,
            fill=m["fill"], outline=m["ring"], width=4,
        )
        # Emoji (top area of bubble)
        self._emoji = self.canvas.create_text(
            x, y - 20,
            text=self.defn["emoji"],
            font=(FONT, 16),
            anchor="center",
        )
        # Name text (lower area, hidden after discovery)
        self._name = self.canvas.create_text(
            x, y + 13,
            text=self.defn["name"],
            font=(FONT, 7, "bold"),
            fill=m["text_fg"],
            justify="center",
            anchor="center",
        )
        # Stamp text (shown after discovery, hidden initially)
        self._stamp = self.canvas.create_text(
            x, y + 13,
            text=m["stamp_txt"],
            font=(FONT, 8, "bold"),
            fill=m["stamp_fg"],
            justify="center",
            anchor="center",
            state="hidden",
        )
        self._clickable = [self._oval, self._emoji, self._name]

    def bind(self, on_click) -> None:
        for iid in self._clickable:
            self.canvas.tag_bind(iid, "<Button-1>", lambda _e: on_click(self))
            self.canvas.tag_bind(iid, "<Enter>",    lambda _e: self._hover(True))
            self.canvas.tag_bind(iid, "<Leave>",    lambda _e: self._hover(False))

    def _hover(self, on: bool) -> None:
        if self.discovered:
            return
        m = self.meta
        if on:
            self.canvas.itemconfig(self._oval, outline=m["ring_hvr"], width=5)
            self.canvas.itemconfig(self._glow, state="normal")
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.itemconfig(self._oval, outline=m["ring"], width=4)
            self.canvas.itemconfig(self._glow, state="hidden")
            self.canvas.config(cursor="")

    def discover(self) -> None:
        self.discovered = True
        m = self.meta
        self.canvas.itemconfig(self._oval,  outline=m["disc_ring"], width=5)
        self.canvas.itemconfig(self._name,  state="hidden")
        self.canvas.itemconfig(self._stamp, state="normal")
        self.canvas.itemconfig(self._glow,  state="hidden")
        # Slow bubble to gentle drift after discovery
        self.dx *= 0.3
        self.dy *= 0.3

    def move(self, w: int, h: int) -> None:
        pad = BUBBLE_R + 8
        self.x += self.dx
        self.y += self.dy

        if self.x < pad:
            self.x = pad;         self.dx =  abs(self.dx)
        elif self.x > w - pad:
            self.x = w - pad;     self.dx = -abs(self.dx)
        if self.y < pad:
            self.y = pad;         self.dy =  abs(self.dy)
        elif self.y > h - pad:
            self.y = h - pad;     self.dy = -abs(self.dy)

        x, y, r = self.x, self.y, BUBBLE_R
        self.canvas.coords(self._glow,  x-r-6, y-r-6, x+r+6, y+r+6)
        self.canvas.coords(self._oval,  x-r,   y-r,   x+r,   y+r)
        self.canvas.coords(self._emoji, x,     y-20)
        self.canvas.coords(self._name,  x,     y+13)
        self.canvas.coords(self._stamp, x,     y+13)


# ── Game ───────────────────────────────────────────────────────────────────────

class BubbleGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root      = root
        self.root.title("🫧  Cotiviti — Service Portal Bubble Explorer")
        self.root.geometry("1180x820")
        self.root.configure(bg=C_BG)
        self.root.minsize(980, 700)

        self.bubbles:    list[Bubble] = []
        self.discovered: int          = 0
        self._anim_id:   str | None   = None
        self._placed:    bool         = False

        self._build_ui()
        self._canvas.bind("<Configure>", self._on_canvas_ready)

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Header (same 3-D slab style as cotiviti_ticket_match)
        hdr_shd = tk.Frame(self.root, bg=C_SHADOW, height=84)
        hdr_shd.pack(fill="x")
        hdr_shd.pack_propagate(False)
        hdr = tk.Frame(hdr_shd, bg=C_PANEL)
        hdr.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 4))

        tk.Frame(hdr, bg=C_PINK, width=7).pack(side="left", fill="y")
        logo_f = tk.Frame(hdr, bg=C_PANEL)
        logo_f.pack(side="left", padx=(12, 0))
        _lf = (FONT, 15, "bold")
        _lkw = dict(bg=C_PANEL, padx=0, pady=0)   # zero padding so letters sit flush
        tk.Label(logo_f, text="C",    font=_lf,               fg=C_WHITE,    **_lkw).pack(side="left")
        tk.Label(logo_f, text="O",    font=_lf,               fg=C_P_BRIGHT, **_lkw).pack(side="left")
        tk.Label(logo_f, text="T",    font=_lf,               fg=C_WHITE,    **_lkw).pack(side="left")
        tk.Label(logo_f, text="I",    font=(FONT, 15, "bold"), fg=C_PINK,     **_lkw).pack(side="left")
        tk.Label(logo_f, text="VITI", font=_lf,               fg=C_WHITE,    **_lkw).pack(side="left")
        tk.Frame(hdr, bg=C_TEAL, width=3).pack(side="left", fill="y", padx=(10, 10))
        tk.Label(hdr, text="🫧  Service Portal Bubble Explorer",
                 font=(FONT, 18, "bold"), bg=C_PANEL, fg=C_WHITE).pack(side="left")

        self._disc_lbl = tk.Label(
            hdr, text=f"0 / {TOTAL_BUBBLES} discovered",
            font=(FONT, 12, "bold"), bg=C_PANEL, fg=C_GOLD, padx=16,
        )
        self._disc_lbl.pack(side="right")

        # Tri-colour accent stripe
        stripe = tk.Frame(self.root, height=4)
        stripe.pack(fill="x")
        for clr in [C_PINK, C_PURPLE, C_TEAL]:
            tk.Frame(stripe, bg=clr, height=4).pack(side="left", fill="y", expand=True)

        # Sub-header with colour legend
        sub = tk.Frame(self.root, bg=C_SUBHDR, height=28)
        sub.pack(fill="x")
        sub.pack_propagate(False)
        tk.Label(
            sub,
            text=(
                "Click the bubbles to discover their type!      "
                "🟣 Incident   🩷 Generic Service Request   🔵 Service Catalog"
            ),
            font=(FONT, 9, "bold"), bg=C_SUBHDR, fg=C_WHITE,
        ).pack(side="left", padx=16, pady=4)

        # Feedback panel (bottom, fixed 120 px)
        fb_shd = tk.Frame(self.root, bg=C_SHADOW, height=120)
        fb_shd.pack(fill="x", side="bottom")
        fb_shd.pack_propagate(False)
        self._fb_inner = tk.Frame(fb_shd, bg=C_PANEL)
        self._fb_inner.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 3))

        self._fb_type = tk.Label(
            self._fb_inner,
            text="👆  Click any bubble to learn whether it is a Service Catalog item!",
            font=(FONT, 11, "bold"), bg=C_PANEL, fg=C_GOLD,
            anchor="w", padx=16, pady=6,
        )
        self._fb_type.pack(fill="x")
        self._fb_verdict = tk.Label(
            self._fb_inner, text="",
            font=(FONT, 10, "bold"), bg=C_PANEL, fg=C_MUTED,
            anchor="w", padx=20,
        )
        self._fb_verdict.pack(fill="x")
        self._fb_detail = tk.Label(
            self._fb_inner, text="",
            font=(FONT, 9), bg=C_PANEL, fg="#9090C8",
            anchor="w", padx=20, pady=2, justify="left",
        )
        self._fb_detail.pack(fill="x")

        # Canvas (play area — takes remaining space)
        self._canvas = tk.Canvas(self.root, bg=C_BG, highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

    # ── Initial placement (deferred until canvas has real dimensions) ──────────

    def _on_canvas_ready(self, _event=None) -> None:
        if not self._placed:
            self._placed = True
            self._place_bubbles()
            self._animate()

    def _draw_bg_dots(self) -> None:
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        cols = ["#D8D4F0", "#C8D8F0", "#D0E8D8", "#F0D0E8", "#E8E4FF"]
        for _ in range(50):
            x = random.randint(0, w)
            y = random.randint(0, h)
            r = random.choice([2, 3, 4])
            self._canvas.create_oval(x-r, y-r, x+r, y+r, fill=random.choice(cols), outline="")

    def _place_bubbles(self) -> None:
        self._canvas.delete("all")
        self.bubbles.clear()

        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()

        self._draw_bg_dots()

        defs = list(BUBBLE_DEFS)
        random.shuffle(defs)

        cols, rows = 5, 3
        cell_w = w / cols
        cell_h = h / rows
        pad    = BUBBLE_R + 10

        for idx, defn in enumerate(defs):
            col = idx % cols
            row = idx // cols
            cx  = cell_w * (col + 0.5) + random.uniform(-12, 12)
            cy  = cell_h * (row + 0.5) + random.uniform(-12, 12)
            cx  = max(pad, min(w - pad, cx))
            cy  = max(pad, min(h - pad, cy))
            b   = Bubble(self._canvas, defn, cx, cy)
            b.bind(self._on_bubble_click)
            self.bubbles.append(b)

    # ── Animation ──────────────────────────────────────────────────────────────

    def _animate(self) -> None:
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w > 1 and h > 1:
            for b in self.bubbles:
                b.move(w, h)
        self._anim_id = self.root.after(33, self._animate)   # ~30 fps

    # ── Click ──────────────────────────────────────────────────────────────────

    def _on_bubble_click(self, bubble: Bubble) -> None:
        if not bubble.discovered:
            bubble.discover()
            self.discovered += 1
            self._disc_lbl.config(text=f"{self.discovered} / {TOTAL_BUBBLES} discovered")

        m    = bubble.meta
        defn = bubble.defn
        self._fb_inner.config(  bg=m["panel_bg"])
        self._fb_type.config(   text=m["type_lbl"],  bg=m["panel_bg"], fg=m["panel_fg"])
        self._fb_verdict.config(text=m["verdict"],   bg=m["panel_bg"], fg=m["verdict_fg"])
        self._fb_detail.config( text=defn["detail"], bg=m["panel_bg"], fg="#A0A8CC")

        if self.discovered == TOTAL_BUBBLES:
            self.root.after(700, self._all_done)

    # ── All discovered overlay ─────────────────────────────────────────────────

    def _all_done(self) -> None:
        if self._anim_id:
            self.root.after_cancel(self._anim_id)
            self._anim_id = None

        ov = tk.Toplevel(self.root)
        ov.title("All Discovered!")
        ov.configure(bg=C_BG)
        ov.resizable(False, False)
        ov.transient(self.root)
        ov.grab_set()
        self.root.update_idletasks()
        rx = self.root.winfo_x() + (self.root.winfo_width()  - 600) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - 520) // 2
        ov.geometry(f"600x520+{rx}+{ry}")

        # Banner
        ban_shd = tk.Frame(ov, bg=C_SHADOW)
        ban_shd.pack(fill="x")
        ban = tk.Frame(ban_shd, bg=C_PANEL)
        ban.pack(fill="x", padx=(0, 3), pady=(0, 4))
        stp = tk.Frame(ban, height=5)
        stp.pack(fill="x")
        for clr in [C_PINK, C_PURPLE, C_TEAL]:
            tk.Frame(stp, bg=clr, height=5).pack(side="left", fill="y", expand=True)
        tk.Label(ban, text="🎉  All 15 Items Discovered!",
                 font=(FONT, 20, "bold"), bg=C_PANEL, fg=C_GOLD).pack(pady=(14, 4))
        tk.Label(ban, text="You've explored the full Cotiviti Service Portal.",
                 font=(FONT, 11), bg=C_PANEL, fg=C_WHITE).pack(pady=(0, 10))

        # Three summary cards
        sf = tk.Frame(ov, bg=C_BG)
        sf.pack(pady=14, padx=16, fill="x")
        cards = [
            ("incident", "🚨  INCIDENT",           "NOT a catalog item\nReport immediately — no portal form"),
            ("gsr",      "📋  GENERIC SERVICE REQ", "NOT a catalog item\nFor needs not listed in the portal"),
            ("catalog",  "📦  SERVICE CATALOG",     "13 pre-approved portal items\nSubmit via the Service Portal"),
        ]
        for t, lbl, body in cards:
            m     = TYPE_META[t]
            s_shd = tk.Frame(sf, bg=C_SHADOW)
            s_shd.pack(side="left", fill="x", expand=True, padx=5)
            card  = tk.Frame(s_shd, bg=m["fill"])
            card.pack(fill="x", padx=(0, 4), pady=(0, 4))
            tk.Frame(card, bg=m["ring"], height=4).pack(fill="x")
            tk.Label(card, text=lbl,  font=(FONT, 9, "bold"),
                     bg=m["fill"], fg=m["ring"]).pack(pady=(10, 2))
            tk.Label(card, text=body, font=(FONT, 8),
                     bg=m["fill"], fg=C_MUTED, justify="center").pack(pady=(0, 12))

        # Key rule
        rule_shd = tk.Frame(ov, bg=C_SHADOW)
        rule_shd.pack(fill="x", padx=16, pady=(4, 0))
        rule = tk.Frame(rule_shd, bg=C_SUBHDR)
        rule.pack(fill="x", padx=(0, 3), pady=(0, 3))
        tk.Label(
            rule,
            text=(
                "💡  Key Rule:  An INCIDENT or GENERIC SERVICE REQUEST is NOT a catalog item.\n"
                "The Service Catalog contains pre-approved items with automated workflows in the portal."
            ),
            font=(FONT, 9), bg=C_SUBHDR, fg=C_WHITE,
            justify="left", padx=12, pady=8,
        ).pack(fill="x")

        # Explore Again button
        btn_shd = tk.Frame(ov, bg=C_SHADOW)
        btn_shd.pack(pady=14)
        tk.Button(
            btn_shd, text="  Explore Again  ", font=(FONT, 13, "bold"),
            bg=C_PINK, fg=C_WHITE, padx=20, pady=10,
            cursor="hand2", relief="flat", activebackground=C_K_BRIGHT,
            command=lambda: [ov.destroy(), self._restart()],
        ).pack(padx=(0, 4), pady=(0, 4))

    # ── Restart ────────────────────────────────────────────────────────────────

    def _restart(self) -> None:
        if self._anim_id:
            self.root.after_cancel(self._anim_id)
            self._anim_id = None

        self.discovered = 0
        self._disc_lbl.config(text=f"0 / {TOTAL_BUBBLES} discovered")
        self._fb_inner.config(  bg=C_PANEL)
        self._fb_type.config(   text="👆  Click any bubble to learn whether it is a Service Catalog item!",
                                bg=C_PANEL, fg=C_GOLD)
        self._fb_verdict.config(text="", bg=C_PANEL, fg=C_MUTED)
        self._fb_detail.config( text="", bg=C_PANEL, fg="#9090C8")

        self._place_bubbles()
        self._animate()


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    root = tk.Tk()
    BubbleGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
