"""The main window: a thin shell that wires the pages and features together.

Each page / feature lives in its own module under ui/pages and ui/features as a mixin class holding
that part's `_build_*`, `refresh_*` and action methods. They all share this window (`self`).
"""
import tkinter as tk
from tkinter import ttk

from personal_warehouse.core.database import auto_backup
from personal_warehouse.i18n import LANGS, current_lang, tr
from personal_warehouse.i18n import set_language as set_ui_language
from personal_warehouse.settings import save_settings
from personal_warehouse.ui.features.data_tools import DataToolsFeature
from personal_warehouse.ui.features.labels import LabelsFeature
from personal_warehouse.ui.features.updates import UpdatesFeature
from personal_warehouse.ui.pages.dashboard import DashboardPage
from personal_warehouse.ui.pages.inventory import InventoryPage
from personal_warehouse.ui.pages.item_form import ItemFormPage
from personal_warehouse.ui.pages.locations import LocationsPage
from personal_warehouse.ui.pages.movements import MovementsPage
from personal_warehouse.ui.pages.scan import ScanPage
from personal_warehouse.ui.pages.settings import SettingsPage
<<<<<<< HEAD
from personal_warehouse.ui.theme import C, TS, bw, current_theme, fnt, mix, pick_font, px, set_scale, set_theme
from personal_warehouse.ui.widgets import (Pages, ScrollFrame, btn, clear_scrollers, install_wheel, lbl, nchip, pulse)
=======
from personal_warehouse.ui.theme import C, current_theme, fnt, pick_font, set_theme
from personal_warehouse.ui.widgets import Pages, lbl
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb


class WarehouseApp(DashboardPage, InventoryPage, ItemFormPage, MovementsPage, LocationsPage, ScanPage,
                   SettingsPage, LabelsFeature, UpdatesFeature, DataToolsFeature, tk.Tk):
    def __init__(self):
        super().__init__()
        pick_font()
<<<<<<< HEAD
        set_scale(self.winfo_fpixels("1i") / 96.0)
        self._fit_window()
        self.minsize(px(720), px(500))
        self._status_job = self._search_job = self._scan_job = self._resize_job = None
        self._bt = self._upd = None
        self.rtl = False
        self._compact = None
        self._compact_manual = None               # None = follow the window width, True/False = user's choice
        install_wheel(self)
        self.bind("<Configure>", self._on_window_configure, add="+")
        self._setup()
        self.after(3000, self._auto_update_check)       # once per start, not on every UI rebuild

    def _fit_window(self):
        """Open at a comfortable size that always fits the screen (laptops, scaled displays), centred."""
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(px(1360), sw - px(60)), min(px(840), sh - px(110))
        self.geometry(f"{w}x{h}+{max((sw - w) // 2, 0)}+{max((sh - h) // 2 - px(20), 0)}")

=======
        self.geometry("1400x860")
        self.minsize(1150, 720)
        self._status_job = self._search_job = self._scan_job = None
        self._bt = self._upd = None
        self.rtl = False
        self._setup()
        self.after(3000, self._auto_update_check)       # once per start, not on every UI rebuild

>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
    def set_language(self, code):
        if code in LANGS and code != current_lang():
            set_ui_language(code)
            save_settings(lang=code)
            self.after(30, self.rebuild)

    def change_theme(self, name):
        if name != current_theme():
            set_theme(name)
            save_settings(theme=name)
            self.after(30, self.rebuild)

    def _setup(self):
        self.rtl = current_lang() == "ar"
        self.s1, self.s2 = ("right", "left") if self.rtl else ("left", "right")   # start / end side
        self.a1 = "e" if self.rtl else "w"                                         # start anchor
        self.just = "right" if self.rtl else "left"
        self.title(tr("app_name"))
        self.configure(bg=C["bg"])
        self.selected_id = None
        self.photo_new = self.photo_current = None
        self.photo_remove = False
        self._photo_img = None
        self.sort_col, self.sort_desc = "location", False
        self.item_choice_map, self._all_labels = {}, []
        self.scan_item_id = None
        self._scan_img = None
        self._sect_data = {}
        self._style()
        self._build()
        self._bind_keys()
        self.refresh_all()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def rebuild(self):
<<<<<<< HEAD
        clear_scrollers()
=======
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        for w in self.winfo_children():
            w.destroy()
        self._setup()

    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure(".", background=C["bg"], foreground=C["ink"], font=fnt(10))
        s.configure("TFrame", background=C["bg"])
        s.configure("TLabel", background=C["bg"], foreground=C["ink"], font=fnt(10))
        field = dict(fieldbackground=C["input"], foreground=C["ink"], bordercolor=C["line"],
                     lightcolor=C["line"], darkcolor=C["line"], insertcolor=C["ink"])
<<<<<<< HEAD
        s.configure("TEntry", padding=(10, 9), **field)
        s.map("TEntry", bordercolor=[("focus", C["accent"])], lightcolor=[("focus", C["accent"])],
              darkcolor=[("focus", C["accent"])], fieldbackground=[("disabled", C["head"])],
              foreground=[("disabled", C["muted"])])
        s.configure("TCombobox", padding=(9, 8), background=C["head"], arrowcolor=C["muted"], **field)
        s.map("TCombobox", fieldbackground=[("readonly", C["input"])], foreground=[("readonly", C["ink"])],
              selectbackground=[("readonly", C["input"])], selectforeground=[("readonly", C["ink"])],
              bordercolor=[("focus", C["accent"])])
        s.configure("TSpinbox", padding=(9, 8), arrowcolor=C["muted"], background=C["head"], **field)
        s.configure("TCheckbutton", background=C["bg"], foreground=C["ink"], font=fnt(10))
        s.map("TCheckbutton", background=[("active", C["bg"])], foreground=[("active", C["ink"])])
        s.configure("Treeview", rowheight=px(40), font=fnt(10), background=C["card"], fieldbackground=C["card"],
                    foreground=C["ink"], borderwidth=0)
        s.map("Treeview", background=[("selected", C["sel"])], foreground=[("selected", C["title"])])
        s.configure("Treeview.Heading", font=fnt(9, True), background=C["head"], foreground=C["muted"],
                    relief="flat", padding=(12, 10))
        s.map("Treeview.Heading", background=[("active", C["soft_h"])])
        for orient in ("Vertical", "Horizontal"):
            s.configure(f"{orient}.TScrollbar", background=C["soft_h"], troughcolor=C["bg"], bordercolor=C["bg"],
                        lightcolor=C["soft_h"], darkcolor=C["soft_h"], arrowcolor=C["muted"], relief="flat",
                        arrowsize=px(14))
            s.map(f"{orient}.TScrollbar", background=[("active", C["accent"])])
=======
        s.configure("TEntry", padding=7, **field)
        s.map("TEntry", bordercolor=[("focus", C["accent"])], lightcolor=[("focus", C["accent"])],
              darkcolor=[("focus", C["accent"])], fieldbackground=[("disabled", C["head"])],
              foreground=[("disabled", C["muted"])])
        s.configure("TCombobox", padding=6, background=C["head"], arrowcolor=C["muted"], **field)
        s.map("TCombobox", fieldbackground=[("readonly", C["input"])], foreground=[("readonly", C["ink"])],
              selectbackground=[("readonly", C["input"])], selectforeground=[("readonly", C["ink"])],
              bordercolor=[("focus", C["accent"])])
        s.configure("TSpinbox", padding=6, arrowcolor=C["muted"], background=C["head"], **field)
        s.configure("TCheckbutton", background=C["bg"], foreground=C["ink"], font=fnt(10))
        s.map("TCheckbutton", background=[("active", C["bg"])], foreground=[("active", C["ink"])])
        s.configure("Treeview", rowheight=32, font=fnt(10), background=C["card"], fieldbackground=C["card"],
                    foreground=C["ink"], borderwidth=0)
        s.map("Treeview", background=[("selected", C["sel"])], foreground=[("selected", C["ink"])])
        s.configure("Treeview.Heading", font=fnt(10, True), background=C["head"], foreground=C["title"],
                    relief="flat", padding=(8, 8))
        s.map("Treeview.Heading", background=[("active", C["soft_h"])])
        s.configure("Vertical.TScrollbar", background=C["head"], troughcolor=C["bg"], bordercolor=C["bg"],
                    arrowcolor=C["muted"], relief="flat")
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        self.option_add("*TCombobox*Listbox.background", C["input"])
        self.option_add("*TCombobox*Listbox.foreground", C["ink"])
        self.option_add("*TCombobox*Listbox.selectBackground", C["accent"])
        self.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
        self.option_add("*TCombobox*Listbox.font", fnt(10))

<<<<<<< HEAD
    # ------------------------------------------------------------------ layout shell
    def pad(self, start, end):
        """(start, end) spacing as the (left, right) tuple Tk wants: mirrored in RTL."""
        return (end, start) if self.rtl else (start, end)

    def _build(self):
        self.pages = Pages(self._nav_highlight)
        self.nb = self.pages                                  # compatibility name
        self._compact = None
        self.side = tk.Frame(self, bg=C["side"], width=px(244), highlightbackground=C["line"], highlightthickness=1)
        self.side.pack(side=self.s1, fill="y")
        self.side.pack_propagate(False)
=======
    def _build(self):
        self.pages = Pages(self._nav_highlight)
        self.nb = self.pages                                  # compatibility name
        side = tk.Frame(self, bg=C["side"], width=236)
        side.pack(side=self.s1, fill="y")
        side.pack_propagate(False)
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        main = tk.Frame(self, bg=C["bg"])
        main.pack(side=self.s1, fill="both", expand=True)

        self.status_var = tk.StringVar()
<<<<<<< HEAD
        tk.Frame(main, bg=C["line"], height=1).pack(side="bottom", fill="x")
        self._status_lbl = tk.Label(main, textvariable=self.status_var, anchor=self.a1, bg=C["bg"], fg=C["muted"],
                                    font=fnt(9), padx=px(20), pady=px(6))
        self._status_lbl.pack(side="bottom", fill="x")
        self._build_topbar(main)
=======
        tk.Label(main, textvariable=self.status_var, anchor=self.a1, bg=C["head"], fg=C["title"],
                 font=fnt(10), padx=16, pady=6).pack(side="bottom", fill="x")
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        self.content = tk.Frame(main, bg=C["bg"])
        self.content.pack(fill="both", expand=True)

        names = ["dashboard", "inventory", "item", "movement", "scan", "locations", "settings"]
        for n in names:
<<<<<<< HEAD
            sf = ScrollFrame(self.content, rtl=self.rtl, min_width=560)
            setattr(self, f"{n}_tab", sf.body)                # pages build into the scrollable body
            self.pages.register(sf.body, sf)
        self._build_sidebar(self.side)
=======
            setattr(self, f"{n}_tab", tk.Frame(self.content, bg=C["bg"], padx=26, pady=18))
        self._build_sidebar(side)
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        self._build_dashboard()
        self._build_inventory()
        self._build_item_form()
        self._build_movements()
        self._build_scan()
        self._build_locations()
        self._build_settings()
        self.pages.select(self.dashboard_tab)
<<<<<<< HEAD
        self.after(60, self._apply_responsive)

    def _hover(self, w, base, hov):
        """Give a flat top-bar control a hover state so it feels live, not just press-reactive."""
        w.bind("<Enter>", lambda _e: w.configure(bg=hov) if str(w["state"]) != "disabled" else None)
        w.bind("<Leave>", lambda _e: w.configure(bg=base))
        return w

    def _build_topbar(self, parent):
        bar = tk.Frame(parent, bg=C["top"])
        bar.pack(fill="x")
        tk.Frame(parent, bg=C["line"], height=1).pack(fill="x")
        inner = tk.Frame(bar, bg=C["top"], padx=px(18), pady=px(11))
        inner.pack(fill="x")
        # end side first, so a narrow window squeezes the search box and never these controls
        self.top_add = btn(inner, tr("btn_add_item"), self.new_item, "primary", padx=12, pady=6)
        self.top_add.pack(side=self.s2, padx=self.pad(8, 0))
        self._theme_btn = tk.Button(inner, text="☾" if current_theme() == "light" else "☀", relief="flat", bd=0,
                                    cursor="hand2", padx=12, pady=8, bg=C["head"], fg=C["ink"],
                                    highlightthickness=bw(), highlightbackground=C["line"],
                                    activebackground=C.get("accent_fill", C["accent"]),
                                    activeforeground="#FFFFFF", font=fnt(11, True),
                                    command=lambda: self.change_theme("dark" if current_theme() == "light" else "light"))
        self._hover(self._theme_btn, C["head"], C["soft_h"]).pack(side=self.s2, padx=self.pad(8, 0))
        seg = tk.Frame(inner, bg=C["head"], highlightthickness=bw(), highlightbackground=C["line"], padx=2, pady=2)
        seg.pack(side=self.s2, padx=self.pad(8, 0))
        for code, text in (("vi", "VI"), ("en", "EN"), ("ar", "ع")):
            on = code == current_lang()
            base = C["card"] if on else C["head"]
            b = tk.Button(seg, text=text, relief="flat", bd=0, cursor="hand2", padx=10, pady=6,
                          bg=base, fg=C["title"] if on else C["muted"],
                          activebackground=C["yellow"], activeforeground=C["ink"], font=fnt(9, True),
                          command=lambda c=code: self.set_language(c))
            self._hover(b, base, C["card"] if on else C["soft_h"]).pack(side=self.s1, padx=1)
        self._menu_btn = tk.Button(inner, text="☰", relief="flat", bd=0, cursor="hand2", padx=12, pady=8, bg=C["head"],
                                   fg=C["ink"], activebackground=C["yellow"], activeforeground=C["title"],
                                   highlightthickness=bw(), highlightbackground=C["line"],
                                   font=fnt(13), command=self._toggle_sidebar)
        self._hover(self._menu_btn, C["head"], C["soft_h"]).pack(side=self.s1, padx=self.pad(0, 8))
        holder = tk.Frame(inner, bg=C["top"])
        holder.pack(side=self.s1, fill="x", expand=True)
        self._search_box = tk.Frame(holder, bg=C["input"], highlightbackground=C["line"], highlightcolor=C["accent"],
                                    highlightthickness=bw(), height=px(46))
        self._search_box.pack(side=self.s1)
        self._search_box.pack_propagate(False)
        tk.Label(self._search_box, text="⌕", bg=C["input"], fg=C["muted"], font=fnt(12)).pack(
            side=self.s1, padx=self.pad(10, 4))
        self.top_search = tk.Entry(self._search_box, relief="flat", bd=0, bg=C["input"], fg=C["ink"],
                                   insertbackground=C["ink"], font=fnt(10), justify=self.just)
        self.top_search.pack(side=self.s1, fill="both", expand=True, padx=self.pad(0, 8))
        self._search_hint = tr("top_search")
        self._search_placeholder(True)
        self.top_search.bind("<FocusIn>", self._search_focus_in)
        self.top_search.bind("<FocusOut>", self._search_focus_out)
        self.top_search.bind("<Return>", self._global_search)
        holder.bind("<Configure>", lambda e: self._size_search(holder), add="+")

    def _size_search(self, holder):
        w = holder.winfo_width()
        if isinstance(w, (int, float)) and w > 1:
            self._search_box.configure(width=max(px(120), min(w - px(4), px(460))))

    def _search_placeholder(self, show):
        e = self.top_search
        if show and not e.get():
            e.insert(0, self._search_hint)
            e.configure(fg=C["muted"])
            self._search_is_hint = True
        elif not show and getattr(self, "_search_is_hint", False):
            e.delete(0, "end")
            e.configure(fg=C["ink"])
            self._search_is_hint = False

    def _search_focus_in(self, event=None):
        self._search_placeholder(False)
        self._search_box.configure(highlightbackground=C["accent"], highlightcolor=C["accent"])

    def _search_focus_out(self, event=None):
        self._search_placeholder(True)
        self._search_box.configure(highlightbackground=C["line"], highlightcolor=C["accent"])

    def _focus_global_search(self):
        self.top_search.focus_set()
        self._search_placeholder(False)
        self.top_search.selection_range(0, "end")
        return "break"

    def _global_search(self, event=None):
        text = "" if getattr(self, "_search_is_hint", False) else self.top_search.get().strip()
        self.search_var.set(text)
        self.loc_filter.set(tr("all_locations"))
        self.cond_filter.set(tr("all_conditions"))
        self.low_only.set(False)
        self.pages.select(self.inventory_tab)
        self.refresh_inventory()

    def _build_sidebar(self, side):
        self._brand_texts, self._side_footers = [], []
        head = tk.Frame(side, bg=C["side"], padx=px(10), pady=px(16))
        head.pack(fill="x")
        brand = tk.Frame(head, bg=C["side_logo"], padx=px(10), pady=px(10))      # the mock-up's "logo card"
        brand.pack(fill="x")
        self._brand_logo = tk.Label(brand, text="▦", bg=C["yellow"], fg=C["ink_line"], font=fnt(15, True),
                                    width=2, padx=3, pady=3, highlightthickness=bw(),
                                    highlightbackground=C["ink_line"])
        self._brand_logo.pack(side=self.s1, padx=self.pad(0, 9))
        box = tk.Frame(brand, bg=C["side_logo"])
        box.pack(side=self.s1, fill="x", expand=True)
        tk.Label(box, text=tr("app_name"), bg=C["side_logo"], fg=C["title"] if current_theme() == "dark" else C["ink"],
                 font=fnt(11, True), anchor=self.a1, justify=self.just, wraplength=px(130)).pack(fill="x")
        tk.Label(box, text=tr("brand_sub"), bg=C["side_logo"], fg=C["muted"], font=fnt(8), anchor=self.a1,
                 justify=self.just, wraplength=px(130)).pack(fill="x")
        self._brand_texts.append(box)
        self._brand_box_opts = dict(side=self.s1, fill="x", expand=True)
        self.nav_btns = {}
        nav = [("dashboard", "▦", "nav_dashboard"), ("inventory", "▤", "nav_inventory"),
               ("item", "＋", "nav_item"), ("movement", "⇄", "nav_move"), ("scan", "⌕", "nav_scan"),
               ("locations", "▣", "nav_map"), ("settings", "⚙", "nav_settings")]
        for key, icon, label in nav:
            self._nav_item(side, icon, tr(label), getattr(self, f"{key}_tab"))
        foot = tk.Frame(side, bg=C["side"], padx=px(10), pady=px(12))
        foot.pack(side="bottom", fill="x")
        hint = tk.Frame(foot, bg=C["side_hov"], padx=px(12), pady=px(10))
        hint.pack(fill="x")
        tk.Label(hint, text=tr("nav_hint"), bg=C["side_hov"], fg=C["side_ink"], font=fnt(8),
                 wraplength=px(180), justify=self.just, anchor=self.a1).pack(fill="x")
        self._side_footers.append(foot)

    def _nav_item(self, side, icon, text, frame):
        row = tk.Frame(side, bg=C["side"], cursor="hand2")
        row.pack(fill="x", padx=px(10), pady=px(3))
        bar = tk.Frame(row, bg=C["side"], width=4)
        bar.pack(side=self.s1, fill="y")
        ic = nchip(row, icon, active=False)
        ic.pack(side=self.s1, padx=self.pad(8, 4), pady=px(4))
        tx = tk.Label(row, text=text, bg=C["side"], fg=C["side_ink"], font=fnt(TS["body"]), anchor=self.a1,
                      justify=self.just, wraplength=px(150), cursor="hand2")
        tx.pack(side=self.s1, fill="x", expand=True)
        parts = (row, ic, tx)
        row.configure(takefocus=True)
        for w in parts:
            w.bind("<Button-1>", lambda e, fr=frame: self._goto(fr))
            w.bind("<Return>", lambda e, fr=frame: self._goto(fr))
            w.bind("<space>", lambda e, fr=frame: self._goto(fr))
            w.bind("<Enter>", lambda e, p=parts, f=frame: self._nav_paint(p, C["side_hov"], f, hover=True))
            w.bind("<Leave>", lambda e, p=parts, f=frame: self._nav_paint(p, C["side"], f, hover=True, hovering=False))
        self.nav_btns[frame] = dict(row=row, bar=bar, tile=ic, tx=tx)

    def _nav_paint(self, parts, color, frame, hover=False, hovering=True):
        """Hover feedback for an idle nav row (the active row keeps its red state)."""
        if hover and self.pages.current is frame:
            return
        row, tile, tx = parts
        row.configure(bg=color)
        tx.configure(bg=color, fg="#FFFFFF" if hovering else C["side_ink"])
        self._tile_paint(tile, False, hover=hovering)

    def _toggle_sidebar(self):
        self._compact_manual = not bool(self._compact)
        self._set_compact(self._compact_manual)

    def _set_compact(self, flag):
        flag = bool(flag)
        if flag == self._compact:
            return
        self._compact = flag
        self.side.configure(width=px(68 if flag else 244))
        for box in self._brand_texts:
            box.pack_forget() if flag else box.pack(**self._brand_box_opts)
        for foot in self._side_footers:
            foot.pack_forget() if flag else foot.pack(side="bottom", fill="x")
        for parts in self.nav_btns.values():
            if flag:
                parts["tx"].pack_forget()
                parts["tile"].pack_configure(expand=True, padx=0)
            else:
                parts["tile"].pack_configure(expand=False, padx=self.pad(8, 4))
                parts["tx"].pack(side=self.s1, fill="x", expand=True)

    def _on_window_configure(self, event):
        if event.widget is not self:
            return
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(90, self._apply_responsive)

    def _apply_responsive(self):
        self._resize_job = None
        w = self.winfo_width()
        if not isinstance(w, (int, float)) or w <= 1:
            return
        if not hasattr(self, "side"):
            return
        self._set_compact(self._compact_manual if self._compact_manual is not None else w < px(1040))
        self.top_add.configure(text=tr("btn_add_item") if w >= px(900) else "＋")
=======

    def _build_sidebar(self, side):
        head = tk.Frame(side, bg=C["side"], padx=20, pady=22)
        head.pack(fill="x")
        tk.Label(head, text="▣  WAREHOUSE", bg=C["side"], fg="#FFFFFF", font=fnt(16, True),
                 anchor=self.a1).pack(fill="x")
        tk.Label(head, text=tr("brand_sub"), bg=C["side"], fg=C["side_ink"], font=fnt(9),
                 anchor=self.a1).pack(fill="x", pady=(3, 0))
        self.nav_btns = {}
        nav = [("dashboard", "▦", "nav_dashboard"), ("inventory", "☰", "nav_inventory"),
               ("item", "✎", "nav_item"), ("movement", "⇄", "nav_move"), ("scan", "⌖", "nav_scan"),
               ("locations", "◫", "nav_map"), ("settings", "⚙", "nav_settings")]
        for key, icon, label in nav:
            frame = getattr(self, f"{key}_tab")
            b = tk.Button(side, text=f"  {icon}   {tr(label)}", anchor=self.a1, relief="flat", bd=0,
                          bg=C["side"], fg=C["side_ink"], activebackground=C["side_hov"],
                          activeforeground="#FFFFFF", font=fnt(11), padx=18, pady=11, cursor="hand2",
                          command=lambda fr=frame: self._goto(fr))
            b.pack(fill="x", padx=10, pady=2)
            b.bind("<Enter>", lambda e, b=b, f=frame: b.configure(bg=C["side_hov"]) if self.pages.current is not f else None)
            b.bind("<Leave>", lambda e, b=b, f=frame: b.configure(bg=C["side"]) if self.pages.current is not f else None)
            self.nav_btns[frame] = b
        # language + theme switch at the bottom
        foot = tk.Frame(side, bg=C["side"], padx=14, pady=14)
        foot.pack(side="bottom", fill="x")
        tk.Label(foot, text=tr("nav_hint"), bg=C["side"], fg=C["side_ink"], font=fnt(8), wraplength=200,
                 justify=self.just, anchor=self.a1).pack(fill="x", pady=(0, 10))
        row = tk.Frame(foot, bg=C["side"])
        row.pack(fill="x")
        for code, text in (("vi", "VI"), ("en", "EN"), ("ar", "ع")):
            on = code == current_lang()
            tk.Button(row, text=text, relief="flat", bd=0, cursor="hand2", padx=10, pady=5,
                      bg=C["side_act"] if on else C["side_hov"], fg="#FFFFFF" if on else C["side_ink"],
                      activebackground=C["accent_d"], activeforeground="#FFFFFF", font=fnt(10, True),
                      command=lambda c=code: self.set_language(c)).pack(side=self.s1, padx=(0, 6))
        tk.Button(row, text="☾" if current_theme() == "light" else "☀", relief="flat", bd=0, cursor="hand2", padx=10, pady=5,
                  bg=C["side_hov"], fg="#FFFFFF", activebackground=C["accent_d"], activeforeground="#FFFFFF",
                  font=fnt(11, True),
                  command=lambda: self.change_theme("dark" if current_theme() == "light" else "light")).pack(side=self.s2)
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb

    def _goto(self, frame):
        self.pages.select(frame)

<<<<<<< HEAD
    @staticmethod
    def _tile_paint(tile, active, hover=False):
        """Repaint a nav icon tile: idle = dark chip, hover = red chip, active = translucent-white chip."""
        label = tile.winfo_children()[0]
        tint = C["side_tile_act"] if active else C["side_act"] if hover else C["side_tile"]
        if active:
            tint = mix(C["side_act"], "#FFFFFF", 0.22)
        label.configure(bg=tint, fg="#FFFFFF" if (active or hover) else C["side_ink"], font=fnt(14, active))
        tile.configure(bg=tint)

    def _nav_highlight(self, frame):
        for fr, parts in self.nav_btns.items():
            on = fr is frame
            row_bg = C["side_act"] if on else C["side"]
            for key in ("row", "tx"):
                parts[key].configure(bg=row_bg)
            parts["bar"].configure(bg=C["yellow"] if on else C["side"])
            self._tile_paint(parts["tile"], on)
            parts["tx"].configure(fg="#FFFFFF" if on else C["side_ink"], font=fnt(TS["body"], on))

    def _bind_keys(self):
        self.bind("<Control-n>", lambda e: (self.new_item(), "break")[1])
        self.bind("<Control-k>", lambda e: self._focus_global_search())
        self.bind("<Control-f>", lambda e: (self.pages.select(self.inventory_tab), self.search_entry.focus_set(), "break")[2])
=======
    def _nav_highlight(self, frame):
        for fr, b in self.nav_btns.items():
            on = fr is frame
            b.configure(bg=C["side_act"] if on else C["side"], fg="#FFFFFF" if on else C["side_ink"],
                        font=fnt(11, on))

    def _bind_keys(self):
        self.bind("<Control-n>", lambda e: self.new_item())
        self.bind("<Control-k>", lambda e: (self.pages.select(self.scan_tab), self.scan_entry.focus_set()))
        self.bind("<Control-f>", lambda e: (self.pages.select(self.inventory_tab), self.search_entry.focus_set()))
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        self.bind("<Control-s>", lambda e: self.save_item() if self.pages.select() == str(self.item_tab) else None)

    def status(self, msg, ms=7000):
        self.status_var.set(msg)
<<<<<<< HEAD
        if msg:
            pulse(self._status_lbl, C["accent"], to=C["muted"], steps=8)      # settle back to the quiet muted tone
=======
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        if self._status_job:
            self.after_cancel(self._status_job)
        self._status_job = self.after(ms, lambda: self.status_var.set(""))

    def _page_head(self, parent, title, sub=""):
<<<<<<< HEAD
        """Title block on the start side, ``box.actions`` frame on the end side. When the page is too narrow
        the actions drop below the title instead of being cut off."""
        box = tk.Frame(parent, bg=C["bg"])
        box.pack(fill="x", pady=(0, px(12)))
        text = tk.Frame(box, bg=C["bg"])
        actions = tk.Frame(box, bg=C["bg"])
        t = lbl(text, title, TS["page"], True, C["title"], anchor=self.a1, justify=self.just)
        t.pack(fill="x")
        s = None
        if sub:
            s = lbl(text, sub, TS["body"], False, C["muted"], anchor=self.a1, justify=self.just)
            s.pack(fill="x", pady=(2, 0))
        box.actions = actions
        state = {"narrow": None}

        def place(event=None):
            w = box.winfo_width()
            if not isinstance(w, (int, float)) or w <= 1:
                return
            if s is not None:
                s.configure(wraplength=max(px(200), w - px(8)))
            narrow = w < px(760)
            if narrow == state["narrow"]:
                return
            state["narrow"] = narrow
            for g in (text, actions):
                g.grid_forget()
            box.columnconfigure(0, weight=1)
            box.columnconfigure(1, weight=0)
            if narrow:
                text.grid(row=0, column=0, columnspan=2, sticky="ew")
                actions.grid(row=1, column=0, columnspan=2, sticky=self.a1, pady=(px(8), 0))
            else:
                tc, ac = (1, 0) if self.rtl else (0, 1)
                box.columnconfigure(tc, weight=1)
                box.columnconfigure(ac, weight=0)
                text.grid(row=0, column=tc, sticky="ew")
                actions.grid(row=0, column=ac, sticky="ne")
        box.bind("<Configure>", place, add="+")
        place()
        return box

    def _field_label(self, parent, text, bg=None):
        return lbl(parent, text, TS["label"], False, C["muted"], bg or C["bg"], anchor=self.a1, justify=self.just)
=======
        box = tk.Frame(parent, bg=C["bg"])
        box.pack(fill="x", pady=(0, 14))
        lbl(box, title, 22, True, C["title"], anchor=self.a1, justify=self.just).pack(fill="x")
        if sub:
            lbl(box, sub, 10, False, C["muted"], anchor=self.a1, justify=self.just, wraplength=1000).pack(fill="x", pady=(2, 0))
        return box

    def _field_label(self, parent, text, bg=None):
        return lbl(parent, text, 10, False, C["muted"], bg or C["bg"], anchor=self.a1, justify=self.just)
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb

    def refresh_all(self):
        self.refresh_movement_choices()
        self.refresh_inventory()
        self.refresh_dashboard()
        self.refresh_movements()
        self.refresh_locations()

    def on_close(self):
        auto_backup(overwrite=True)
        self.destroy()
