"""Reusable Tk widgets / factories (card, label, button, tree), the responsive helpers
(ScrollFrame, Flow) and the page switcher."""

import tkinter as tk
from tkinter import ttk

from personal_warehouse.core.barcode import code128_bars
from personal_warehouse.i18n import tr
from personal_warehouse.ui.theme import C, bw, fnt, mix, px


def card(parent, **kw):
    """Paper-coloured content surface with the theme's soft 1.5 px outline."""
    kw.setdefault("bd", 0)
    return tk.Frame(parent, bg=C["card"], highlightbackground=C["line"], highlightthickness=bw(), **kw)


def lbl(parent, text="", size=10, bold=False, fg=None, bg=None, **kw):
    return tk.Label(parent, text=text, font=fnt(size, bold), fg=fg or C["ink"], bg=bg or C["bg"], **kw)


def btn(parent, text, cmd, kind="soft", min_hit=44, **kw):
    """Consistent, high-contrast button with a comfortable hit target and clear interaction states.

    ``min_hit`` is the minimum height in pixels; the default of 44 matches the common
    touch-target guideline so even the secondary "soft" actions stay easy to press.
    Compact toolbar controls can pass ``min_hit=36`` without squeezing their layout."""
    pal = {
        "primary": (C.get("accent_fill", C["accent"]), "#FFFFFF", C.get("accent_hover", C["accent_d"])),
        "success": (C.get("ok_fill", C["ok"]), "#FFFFFF", C.get("ok_hover", C["ok_d"])),
        "danger": (C.get("danger_fill", C["danger"]), "#FFFFFF", C.get("danger_hover", C["danger_d"])),
        "soft": (C["card"], C["ink"], C["soft_h"]),
        "ghost": (C["card"], C["accent"], C["soft_h"]),
    }
    bg, fg, hov = pal[kind]
    pressed = C.get("accent_d", hov) if kind == "primary" else hov
    opts = dict(padx=px(14), pady=px(14), cursor="hand2", font=fnt(10, True),
                highlightthickness=bw(), highlightbackground=C["line"],
                highlightcolor=C["accent"], takefocus=True)
    if kind in ("primary", "success", "danger"):
        opts["highlightbackground"] = bg                 # filled buttons: the outline melts into the fill
    opts.update(kw)
    # Enforce the hit target: a 10pt glyph plus the focus ring is about px(13) tall at
    # 96 dpi, so pad the vertical space until the whole button reaches min_hit pixels.
    fill = px(min_hit) - px(13)
    opts["padx"] = max(px(12), int(opts.get("padx", px(14))))
    opts["pady"] = max(px(12), (fill // 2) if fill > 0 else px(12), int(opts.get("pady", px(14))))
    # Single-glyph buttons ("⋯", "☾", "✕" ...) need an explicit width or the target shrinks.
    if len(text) <= 2 and "width" not in opts:
        opts["width"] = max(2, int(px(min_hit) // px(13)))
    b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, activebackground=hov,
                  activeforeground=fg, disabledforeground=C["muted"], relief="flat", bd=0, **opts)

    def restore(_event=None):
        if str(b["state"]) != "disabled":
            b.configure(bg=hov if b._is_hovered else bg)

    b._is_hovered = False
    b.bind("<Enter>", lambda e: (setattr(b, "_is_hovered", True),
                                  b.configure(bg=hov) if str(b["state"]) != "disabled" else None))
    b.bind("<Leave>", lambda e: (setattr(b, "_is_hovered", False), restore()))
    b.bind("<ButtonPress-1>", lambda e: b.configure(bg=pressed) if str(b["state"]) != "disabled" else None)
    b.bind("<ButtonRelease-1>", restore)
    b.bind("<FocusIn>", lambda e: b.configure(highlightthickness=bw() + 1))
    b.bind("<FocusOut>", lambda e: b.configure(highlightthickness=bw()))
    if kind in ("soft", "ghost"):                            # hover: the outline turns yellow like the mock-up
        b.bind("<Enter>", lambda e: b.configure(highlightbackground=C["yellow"]), add="+")
        b.bind("<Leave>", lambda e: b.configure(highlightbackground=C["line"]), add="+")
    return b


def pulse(widget, color, to=None, steps=12, frame_ms=16):
    """Flash a text widget's colour from ``color`` back to ``to`` (theme title by default).

    A small acknowledgement that a value / state just updated (KPI cards, status line)."""
    try:
        target = to or C["title"]
        widget.configure(fg=color)
        i = 0

        def tick():
            nonlocal i
            i += 1
            eased = 1 - (1 - i / steps) ** 2
            if str(widget.winfo_exists()) == "1":
                widget.configure(fg=mix(color, target, eased) if i < steps else target)
                if i < steps:
                    widget.after(frame_ms, tick)
        widget.after(frame_ms, tick)
    except (tk.TclError, AttributeError):
        pass


def nchip(parent, glyph, active=False, size=38, font_size=14):
    """Neutral icon tile: a rounded-ish square in the theme's head/active surfaces holding a glyph.

    The sidebar navigation uses these instead of bare Unicode labels, so every nav icon shares
    one style (tile size, glyph weight) - the "consistent icon set" from the design rules."""
    tint = C["side_tile_act"] if active else C["side_tile"]
    color = "#FFFFFF" if active else C["side_ink"]
    box = tk.Frame(parent, bg=tint, width=px(size), height=px(size), bd=0, highlightthickness=0)
    box.pack_propagate(False)
    tk.Label(box, text=glyph, bg=tint, fg=color, font=fnt(font_size, active)).pack(expand=True)
    return box


def chip(parent, glyph, tint, color, size=34, font_size=14, outline=None):
    """Round-ish icon tile used in KPI cards and insight rows (a coloured glyph on a soft tint).
    ``outline`` draws the thin ink stroke the insight rows use."""
    box = tk.Frame(parent, bg=tint, width=px(size), height=px(size), bd=0,
                   highlightthickness=1 if outline else 0, highlightbackground=outline or tint)
    box.pack_propagate(False)
    tk.Label(box, text=glyph, bg=tint, fg=color, font=fnt(font_size, True)).pack(expand=True)
    return box


def badge(parent, text, tint, color, bg=None):
    """Pill with a coloured outline (the mock-up's .chip)."""
    return tk.Label(parent, text=text, bg=tint, fg=color, font=fnt(8, True), padx=8, pady=3, bd=0,
                    highlightthickness=1, highlightbackground=color)


def cols_for_width(breakpoints, width):
    """breakpoints = [(min_width, columns), ...] (any order). Returns the columns for ``width``."""
    for min_w, cols in sorted(breakpoints, reverse=True):
        if width >= min_w:
            return cols
    return 1


class Flow:
    """A responsive grid. Children are laid out row by row in N columns; N depends on the width the
    container really has (e.g. 4 KPI cards -> 2 -> 1). In RTL the columns are mirrored, so the first
    child is always at the *start* side."""

    def __init__(self, parent, rtl, breakpoints, weights=None, gap=6, bg=None):
        self.frame = tk.Frame(parent, bg=bg or C["bg"])
        self.rtl, self.bp, self.weights, self.gap = rtl, list(breakpoints), weights, gap
        self.items = []
        self.cols = None
        self._used_cols = 0
        self._used_rows = 0
        self.frame.bind("<Configure>", self._on_resize, add="+")

    def add(self, widget):
        self.items.append(widget)
        self.cols = None                                  # force a re-layout on the next resize
        return widget

    def _on_resize(self, event=None):
        width = self.frame.winfo_width()
        if not isinstance(width, (int, float)) or width <= 1:
            return
        self.layout(cols_for_width(self.bp, width))

    def layout(self, cols):
        cols = max(1, min(cols, len(self.items) or 1))
        if cols == self.cols:
            return
        self.cols = cols
        for c in range(max(self._used_cols, cols)):
            self.frame.columnconfigure(c, weight=0, uniform="", minsize=0)
        for r in range(max(self._used_rows, 1)):
            self.frame.rowconfigure(r, weight=0)
        for i, w in enumerate(self.items):
            r, c = divmod(i, cols)
            span = 1
            if cols > 1 and c == 0 and i == len(self.items) - 1:
                span = cols                               # a lone last item takes the whole row
            elif self.rtl:
                c = cols - 1 - c
            w.grid(row=r, column=c, columnspan=span, sticky="nsew", padx=self.gap // 2 + 1,
                   pady=self.gap // 2 + 1)
        wts = self.weights if self.weights and len(self.weights) == cols else (1,) * cols
        for i in range(cols):
            c = cols - 1 - i if self.rtl else i
            self.frame.columnconfigure(c, weight=wts[i], uniform="flow", minsize=px(120))
        self._used_cols = cols
        self._used_rows = (len(self.items) + cols - 1) // cols


def make_tree(parent, cols, heads, widths, anchors=None, rtl=False, **kw):
    """A Treeview whose columns keep their proportions when the window grows or shrinks.
    Initial column requests are small so a table never forces its parent to be wider than the window;
    a horizontal scrollbar only appears when even the minimum widths do not fit."""
    wrap = tk.Frame(parent, bg=C["card"], highlightbackground=C["line"], highlightthickness=bw(), bd=0)
    tree = ttk.Treeview(wrap, columns=cols, show="headings", **kw)
    sb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=sb.set, xscrollcommand=hsb.set)
    flip = {"w": "e", "e": "w"}
    minw = {c: max(48, int(widths[c] * 0.55)) for c in cols}
    for c in cols:
        tree.heading(c, text=heads[c])
        a = (anchors or {}).get(c, "center")
        tree.column(c, width=minw[c], minwidth=minw[c], anchor=flip.get(a, a) if rtl else a, stretch=False)
    if rtl:
        tree.configure(displaycolumns=list(reversed(cols)))
    # grid (not pack): with pack the expanding tree swallows the space the scrollbars need
    wrap.rowconfigure(0, weight=1)
    wrap.columnconfigure(1 if rtl else 0, weight=1)
    tree.grid(row=0, column=1 if rtl else 0, sticky="nsew")
    sb.grid(row=0, column=0 if rtl else 1, sticky="ns")
    state = {"hsb": False}

    def fit(event=None):
        avail = tree.winfo_width()
        if not isinstance(avail, (int, float)) or avail <= 1:
            return
        total, floor = sum(widths[c] for c in cols), sum(minw[c] for c in cols)
        scale = max(avail / total, 0) if total else 1
        for c in cols:
            w = int(widths[c] * scale) if avail >= floor else minw[c]
            tree.column(c, width=max(minw[c], w))
        need = avail < floor
        if need != state["hsb"]:
            state["hsb"] = need
            if need:
                hsb.grid(row=1, column=1 if rtl else 0, sticky="ew")
            else:
                hsb.grid_remove()
    tree.bind("<Configure>", fit, add="+")
    tree.tag_configure("odd", background=C["stripe"])
    tree.tag_configure("low", background=C["low"], foreground=C["ink"])
    tree.tag_configure("out", background=C["out"], foreground=C["ink"])
    tree.tag_configure("gone", foreground=C["gone"])
    return wrap, tree


def draw_barcode(canvas, text, width=250, height=74):
    canvas.delete("all")
    if not text:
        canvas.create_text(width // 2, height // 2, text=tr("bc_none"), fill="#64748B", font=fnt(9))
        return
    bars, total = code128_bars(text)
    quiet = 10
    scale = max(1, width // (total + 2 * quiet))
    x0 = (width - scale * (total + 2 * quiet)) // 2 + quiet * scale
    for x, w in bars:
        canvas.create_rectangle(x0 + x * scale, 4, x0 + (x + w) * scale, height - 20, fill="black", outline="")
    canvas.create_text(width // 2, height - 9, text=text, fill="black", font=("Courier New", 10, "bold"))


ANIMATE_PAGES = False        # the slide/fade on every page switch forces a re-layout per frame: off = snappy


def debounce(widget, fn, ms=40):
    """Return a callback that runs ``fn`` once, ``ms`` after the last call (collapses <Configure> bursts)."""
    job = {"id": None}

    def run():
        job["id"] = None
        try:
            fn()
        except tk.TclError:
            pass

    def call(event=None):
        if job["id"]:
            widget.after_cancel(job["id"])
        job["id"] = widget.after(ms, run)
    return call


_SCROLLERS = []


def clear_scrollers():
    """Called when the window is rebuilt (language / theme change): the old pages are destroyed."""
    del _SCROLLERS[:]


class ScrollFrame:
    """A page container that scrolls vertically (mouse wheel + scrollbar) when the window is too small and
    that stretches its content to the full viewport when there is room.  Put widgets in ``.body``.
    The scrollbar sits on the start side of the window in RTL."""

    def __init__(self, parent, rtl=False, min_width=520, pad=(22, 18)):
        self.rtl, self.min_width = rtl, px(min_width)
        self.outer = tk.Frame(parent, bg=C["bg"])
        self.canvas = tk.Canvas(self.outer, bg=C["bg"], highlightthickness=0, bd=0, yscrollincrement=px(20))
        self.vsb = ttk.Scrollbar(self.outer, orient="vertical", command=self.canvas.yview)
        self.hsb = ttk.Scrollbar(self.outer, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self._yset, xscrollcommand=self.hsb.set)
        self.body = tk.Frame(self.canvas, bg=C["bg"], padx=px(pad[0]), pady=px(pad[1]))
        self._win = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.outer.rowconfigure(0, weight=1)
        self.outer.columnconfigure(1 if rtl else 0, weight=1)
        self.canvas.grid(row=0, column=1 if rtl else 0, sticky="nsew")
        self._vsb_on = self._hsb_on = False
        self._last = None
        self._rh = 0
        self.canvas.bind("<Configure>", self.refit, add="+")
        self.body.bind("<Configure>", self.refit, add="+")
        _SCROLLERS.append(self)
        self.outer.after(600, self._poll)

    def _yset(self, lo, hi):
        self.vsb.set(lo, hi)
        need = float(lo) > 0.0 or float(hi) < 1.0
        if need != self._vsb_on:
            self._vsb_on = need
            if need:
                self.vsb.grid(row=0, column=0 if self.rtl else 1, sticky="ns")
            else:
                self.vsb.grid_remove()

    def refit(self, event=None):
        try:
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            rw, rh = self.body.winfo_reqwidth(), self.body.winfo_reqheight()
        except tk.TclError:
            return
        if not all(isinstance(v, (int, float)) for v in (cw, ch, rw, rh)) or cw <= 1:
            return
        w, h = max(cw, self.min_width), max(ch, rh)
        key = (w, h, cw, ch)
        if key == self._last:
            return
        self._last = key
        self._rh = rh
        self.canvas.itemconfigure(self._win, width=w, height=h)
        self.canvas.configure(scrollregion=(0, 0, w, h))
        need_h = cw < self.min_width
        if need_h != self._hsb_on:
            self._hsb_on = need_h
            if need_h:
                self.hsb.grid(row=1, column=1 if self.rtl else 0, sticky="ew")
            else:
                self.hsb.grid_remove()
                self.canvas.xview_moveto(0)

    def _poll(self):
        """Content can grow without the window changing size (tables filling up, panels re-flowing)."""
        try:
            if not self.outer.winfo_exists():
                return
            if self.body.winfo_reqheight() != self._rh and self.outer.winfo_ismapped():
                self._last = None
                self.refit()
            self.outer.after(600, self._poll)
        except tk.TclError:
            pass

    def animate_in(self, duration=190):
        """Reveal a freshly shown page: a short upward slide plus a gentle background fade
        so a page switch reads as a transition instead of a hard cut."""
        try:
            if getattr(self, "_anim_job", None):
                self.outer.after_cancel(self._anim_job)
            start_bg = mix(C["bg"], C["head"], 0.6)
            off = px(10)
            self._last = None
            self.refit()
            self.canvas.configure(bg=start_bg)
            self.canvas.coords(self._win, 0, off)
            steps = max(6, duration // 16)
            i = 0

            def tick():
                nonlocal i
                i += 1
                eased = 1 - (1 - i / steps) ** 3          # ease-out: fast start, soft landing
                self.canvas.coords(self._win, 0, round(off * (1 - eased)))
                self.canvas.configure(bg=mix(start_bg, C["bg"], eased))
                if i < steps:
                    self._anim_job = self.outer.after(16, tick)
                else:
                    self._anim_job = None
                    self._last = None
                    self.refit()
            self._anim_job = self.outer.after(16, tick)
        except (tk.TclError, AttributeError):
            pass

    def scroll(self, units):
        lo, hi = self.canvas.yview()
        if lo <= 0.0 and hi >= 1.0:
            return False
        self.canvas.yview_scroll(units, "units")
        return True


def install_wheel(root):
    """One global mouse-wheel handler: scrolls the visible ScrollFrame under the pointer, but leaves
    tables, lists and drop-downs to scroll themselves."""
    own = ("Treeview", "Listbox", "Text", "TCombobox", "TSpinbox")

    def target(widget):
        path = str(widget)
        for sf in _SCROLLERS:
            try:
                if sf.outer.winfo_exists() and sf.outer.winfo_ismapped() and path.startswith(str(sf.outer)):
                    return sf
            except tk.TclError:
                continue
        return None

    def on_wheel(event):
        try:
            if event.widget.winfo_class() in own:
                return
        except (tk.TclError, KeyError, AttributeError):
            return
        sf = target(event.widget)
        if not sf:
            return
        if getattr(event, "num", None) == 4:
            step = -3
        elif getattr(event, "num", None) == 5:
            step = 3
        else:
            d = event.delta or 0
            step = -int(d / 120) * 3 if abs(d) >= 120 else (-3 if d > 0 else 3 if d < 0 else 0)
        if step and sf.scroll(step):
            return "break"

    root.bind_all("<MouseWheel>", on_wheel, add="+")
    root.bind_all("<Button-4>", on_wheel, add="+")
    root.bind_all("<Button-5>", on_wheel, add="+")


class Pages:
    """Tiny page switcher (sidebar navigation instead of notebook tabs).  A page is identified by its inner
    frame; if it was registered together with a ScrollFrame, the scroll container is what gets shown."""

    def __init__(self, on_select=None):
        self.current = None
        self.on_select = on_select
        self._outer = {}
        self._scroll = {}

    def register(self, inner, scroll):
        self._outer[inner] = scroll.outer
        self._scroll[inner] = scroll

    def _shown(self, frame):
        return self._outer.get(frame, frame)

    def select(self, frame=None):
        if frame is None:
            return str(self.current) if self.current else ""
        if self.current is frame:
            return None
        if self.current is not None:
            self._shown(self.current).pack_forget()
        self._shown(frame).pack(fill="both", expand=True)
        self.current = frame
        sf = self._scroll.get(frame)
        if sf:
            sf._last = None
            sf.canvas.yview_moveto(0)
            sf.outer.after(30, sf.refit)
            if ANIMATE_PAGES:
                sf.animate_in()
        if self.on_select:
            self.on_select(frame)
        return None
