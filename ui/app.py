import tkinter as tk
from tkinter import ttk, messagebox

from db import setup_database
from ui.dashboard_view import DashboardView
from ui.cars_view import CarsView
from ui.customers_view import CustomersView
from ui.rentals_view import RentalsView


class CarRentalApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FASTAUTO - Location de Voiture")
        self.root.geometry("1100x650")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#111827")

        self.logo_image = None

        setup_database()
        self._configure_style()
        self._build_layout()

    def _configure_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        dark_bg = "#111827"
        sidebar_bg = "#020617"
        card_bg = "#1f2937"
        text_primary = "#f9fafb"
        text_muted = "#9ca3af"
        accent = "#facc15"
        accent_hover = "#eab308"

        style.configure("TFrame", background=dark_bg)
        style.configure("Sidebar.TFrame", background=sidebar_bg)
        style.configure(
            "Sidebar.TButton",
            background=sidebar_bg,
            foreground=text_muted,
            padding=10,
            anchor="w",
        )
        style.map(
            "Sidebar.TButton",
            background=[("active", dark_bg)],
            foreground=[("active", text_primary)],
        )
        style.configure("Content.TFrame", background=dark_bg)
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 18, "bold"),
            background=dark_bg,
            foreground=text_primary,
        )
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 11, "bold"),
            background=card_bg,
            foreground=text_muted,
        )
        style.configure(
            "TLabelframe",
            background=dark_bg,
            foreground=text_muted,
        )
        style.configure(
            "TLabelframe.Label",
            background=dark_bg,
            foreground=text_muted,
        )
        style.configure(
            "KPIValue.TLabel",
            font=("Segoe UI", 14, "bold"),
            background=card_bg,
            foreground=text_primary,
        )
        style.configure(
            "TButton",
            padding=6,
        )
        style.configure(
            "Accent.TButton",
            background=accent,
            foreground="#111827",
            padding=10,
        )
        style.map(
            "Accent.TButton",
            background=[("active", accent_hover)],
        )

        # Treeview styling
        style.configure(
            "Dark.Treeview",
            background=dark_bg,
            fieldbackground=dark_bg,
            foreground=text_primary,
            rowheight=24,
            bordercolor=card_bg,
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", "#1d4ed8")],
            foreground=[("selected", "#f9fafb")],
        )
        style.configure(
            "Dark.Treeview.Heading",
            background=card_bg,
            foreground=text_muted,
            font=("Segoe UI", 10, "bold"),
        )

    def _build_layout(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=220)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_propagate(False)

        # Logo / brand
        title_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        title_frame.pack(padx=16, pady=(16, 24), anchor="w", fill="x")
        try:
            # place your logo file as 'logo.png' in the project root
            self.logo_image = tk.PhotoImage(file="logo.png")
            logo_bg = tk.Frame(
                title_frame,
                bg="#facc15",
                bd=0,
                highlightthickness=0,
                padx=8,
                pady=4,
            )
            logo_bg.pack(anchor="w")
            logo_label = tk.Label(
                logo_bg,
                image=self.logo_image,
                bg="#facc15",
                borderwidth=0,
                highlightthickness=0,
            )
            logo_label.pack(anchor="w")
        except Exception:
            title = ttk.Label(
                title_frame,
                text="FASTAUTO",
                foreground="#facc15",
                background="#020617",
                justify="left",
                font=("Segoe UI", 18, "bold"),
            )
            title.pack(anchor="w")
            subtitle = ttk.Label(
                title_frame,
                text="Car Rental & Dépannage",
                foreground="#9ca3af",
                background="#020617",
                font=("Segoe UI", 9),
            )
            subtitle.pack(anchor="w", pady=(2, 0))

        self.content = ttk.Frame(self.root, style="Content.TFrame")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.views = {}
        self.current_view = None

        def add_nav_button(text, view_key, view_class):
            btn = ttk.Button(
                sidebar,
                text=text,
                style="Sidebar.TButton",
                command=lambda: self.show_view(view_key, view_class),
            )
            btn.pack(fill="x", padx=8, pady=2)

        add_nav_button("Dashboard", "dashboard", DashboardView)
        add_nav_button("Voitures", "cars", CarsView)
        add_nav_button("Clients", "customers", CustomersView)
        add_nav_button("Locations", "rentals", RentalsView)

        footer = ttk.Label(
            sidebar,
            text="v1.0 - Tkinter + SQLite",
            foreground="#6b7280",
            background="#020617",
            font=("Segoe UI", 8),
        )
        footer.pack(side="bottom", padx=10, pady=12, anchor="w")

        # default view
        self.show_view("dashboard", DashboardView)

    def show_view(self, key, view_class):
        if self.current_view is not None:
            self.current_view.pack_forget()
        if key not in self.views:
            frame = view_class(self.content)
            self.views[key] = frame
        self.current_view = self.views[key]
        self.current_view.pack(fill="both", expand=True)
        # some views might need refresh
        if hasattr(self.current_view, "refresh"):
            try:
                self.current_view.refresh()
            except Exception as exc:  # pragma: no cover - UI safe guard
                messagebox.showerror("Erreur", str(exc))

