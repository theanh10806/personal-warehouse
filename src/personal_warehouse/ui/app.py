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
from personal_warehouse.ui.theme import C, current_theme, fnt, pick_font, set_theme
from personal_warehouse.ui.widgets import Pages, lbl


class WarehouseApp(DashboardPage, InventoryPage, ItemFormPage, MovementsPage, LocationsPage, ScanPage,
                   SettingsPage, LabelsFeature, UpdatesFeature, DataToolsFeature, tk.Tk):
    def __init__(self):
        super().__init__()
        pick_font()
        self.geometry("1400x860")
        self.minsize(1150, 720)
        self._status_job = self._search_job = self._scan_job = None
        self._bt = self._upd = None
        self.rtl = False
        self._setup()
        self.after(3000, self._auto_update_check)       # once per start, not on every UI rebuild

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
        self.option_add("*TCombobox*Listbox.background", C["input"])
        self.option_add("*TCombobox*Listbox.foreground", C["ink"])
        self.option_add("*TCombobox*Listbox.selectBackground", C["accent"])
        self.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
        self.option_add("*TCombobox*Listbox.font", fnt(10))

    def _build(self):
        self.pages = Pages(self._nav_highlight)
        self.nb = self.pages                                  # compatibility name
        side = tk.Frame(self, bg=C["side"], width=236)
        side.pack(side=self.s1, fill="y")
        side.pack_propagate(False)
        main = tk.Frame(self, bg=C["bg"])
        main.pack(side=self.s1, fill="both", expand=True)

        self.status_var = tk.StringVar()
        tk.Label(main, textvariable=self.status_var, anchor=self.a1, bg=C["head"], fg=C["title"],
                 font=fnt(10), padx=16, pady=6).pack(side="bottom", fill="x")
        self.content = tk.Frame(main, bg=C["bg"])
        self.content.pack(fill="both", expand=True)

        names = ["dashboard", "inventory", "item", "movement", "scan", "locations", "settings"]
        for n in names:
            setattr(self, f"{n}_tab", tk.Frame(self.content, bg=C["bg"], padx=26, pady=18))
        self._build_sidebar(side)
        self._build_dashboard()
        self._build_inventory()
        self._build_item_form()
        self._build_movements()
        self._build_scan()
        self._build_locations()
        self._build_settings()
        self.pages.select(self.dashboard_tab)

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

    def _goto(self, frame):
        self.pages.select(frame)

    def _nav_highlight(self, frame):
        for fr, b in self.nav_btns.items():
            on = fr is frame
            b.configure(bg=C["side_act"] if on else C["side"], fg="#FFFFFF" if on else C["side_ink"],
                        font=fnt(11, on))

    def _bind_keys(self):
        self.bind("<Control-n>", lambda e: self.new_item())
        self.bind("<Control-k>", lambda e: (self.pages.select(self.scan_tab), self.scan_entry.focus_set()))
        self.bind("<Control-f>", lambda e: (self.pages.select(self.inventory_tab), self.search_entry.focus_set()))
        self.bind("<Control-s>", lambda e: self.save_item() if self.pages.select() == str(self.item_tab) else None)

    def status(self, msg, ms=7000):
        self.status_var.set(msg)
        if self._status_job:
            self.after_cancel(self._status_job)
        self._status_job = self.after(ms, lambda: self.status_var.set(""))

    def _page_head(self, parent, title, sub=""):
        box = tk.Frame(parent, bg=C["bg"])
        box.pack(fill="x", pady=(0, 14))
        lbl(box, title, 22, True, C["title"], anchor=self.a1, justify=self.just).pack(fill="x")
        if sub:
            lbl(box, sub, 10, False, C["muted"], anchor=self.a1, justify=self.just, wraplength=1000).pack(fill="x", pady=(2, 0))
        return box

    def _field_label(self, parent, text, bg=None):
        return lbl(parent, text, 10, False, C["muted"], bg or C["bg"], anchor=self.a1, justify=self.just)

    def refresh_all(self):
        self.refresh_movement_choices()
        self.refresh_inventory()
        self.refresh_dashboard()
        self.refresh_movements()
        self.refresh_locations()

    def on_close(self):
        auto_backup(overwrite=True)
        self.destroy()
