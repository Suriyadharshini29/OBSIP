import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime

from bmi_logic import calculate_bmi, classify_bmi, validate_inputs
from database import init_db, save_record, get_records, get_all_users, delete_user_records

# ── Colour palette ──────────────────────────────────────────────────────────
BG        = "#1E1E2E"
PANEL     = "#2A2A3E"
ACCENT    = "#7C3AED"
ACCENT_LT = "#9D5CF6"
FG        = "#E2E8F0"
FG_DIM    = "#94A3B8"
ENTRY_BG  = "#313147"
BTN_FG    = "#FFFFFF"
DANGER    = "#E74C3C"

FONT_H1   = ("Segoe UI", 20, "bold")
FONT_H2   = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SML  = ("Segoe UI", 9)


class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.geometry("900x680")
        self.minsize(800, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        init_db()
        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=ACCENT, height=56)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚖  BMI Calculator", font=FONT_H1,
                 bg=ACCENT, fg=BTN_FG, pady=10).pack(side="left", padx=20)

        # Main two-column layout
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=16)

        left  = tk.Frame(body, bg=BG, width=300)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self._build_input_panel(left)
        self._build_result_panel(right)

    def _build_input_panel(self, parent):
        card = tk.Frame(parent, bg=PANEL, bd=0)
        card.pack(fill="x", pady=(0, 12))

        tk.Label(card, text="Calculate BMI", font=FONT_H2,
                 bg=PANEL, fg=FG).grid(row=0, column=0, columnspan=2,
                                       sticky="w", padx=16, pady=(14, 6))

        # Username
        tk.Label(card, text="Username", font=FONT_BODY,
                 bg=PANEL, fg=FG_DIM).grid(row=1, column=0, sticky="w", padx=16, pady=4)
        self.username_var = tk.StringVar()
        tk.Entry(card, textvariable=self.username_var, font=FONT_BODY,
                 bg=ENTRY_BG, fg=FG, insertbackground=FG, relief="flat",
                 width=22).grid(row=1, column=1, padx=(0, 16), pady=4, sticky="ew")

        # Weight
        tk.Label(card, text="Weight (kg)", font=FONT_BODY,
                 bg=PANEL, fg=FG_DIM).grid(row=2, column=0, sticky="w", padx=16, pady=4)
        self.weight_var = tk.StringVar()
        tk.Entry(card, textvariable=self.weight_var, font=FONT_BODY,
                 bg=ENTRY_BG, fg=FG, insertbackground=FG, relief="flat",
                 width=22).grid(row=2, column=1, padx=(0, 16), pady=4, sticky="ew")

        # Height
        tk.Label(card, text="Height (m)", font=FONT_BODY,
                 bg=PANEL, fg=FG_DIM).grid(row=3, column=0, sticky="w", padx=16, pady=4)
        self.height_var = tk.StringVar()
        tk.Entry(card, textvariable=self.height_var, font=FONT_BODY,
                 bg=ENTRY_BG, fg=FG, insertbackground=FG, relief="flat",
                 width=22).grid(row=3, column=1, padx=(0, 16), pady=4, sticky="ew")

        card.columnconfigure(1, weight=1)

        # Buttons
        btn_row = tk.Frame(card, bg=PANEL)
        btn_row.grid(row=4, column=0, columnspan=2, pady=(8, 14), padx=16, sticky="ew")

        tk.Button(btn_row, text="Calculate & Save", font=FONT_BODY,
                  bg=ACCENT, fg=BTN_FG, activebackground=ACCENT_LT,
                  relief="flat", cursor="hand2", padx=12, pady=6,
                  command=self._on_calculate).pack(side="left", padx=(0, 8))

        tk.Button(btn_row, text="Clear", font=FONT_BODY,
                  bg=ENTRY_BG, fg=FG, relief="flat", cursor="hand2",
                  padx=12, pady=6, command=self._clear_inputs).pack(side="left")

        # ── User history section ─────────────────────────────────────────────
        hist_card = tk.Frame(parent, bg=PANEL)
        hist_card.pack(fill="both", expand=True)

        tk.Label(hist_card, text="History", font=FONT_H2,
                 bg=PANEL, fg=FG).pack(anchor="w", padx=16, pady=(14, 6))

        user_row = tk.Frame(hist_card, bg=PANEL)
        user_row.pack(fill="x", padx=16, pady=(0, 6))

        tk.Label(user_row, text="User:", font=FONT_BODY,
                 bg=PANEL, fg=FG_DIM).pack(side="left")

        self.hist_user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(user_row, textvariable=self.hist_user_var,
                                       font=FONT_BODY, width=14, state="readonly")
        self.user_combo.pack(side="left", padx=6)

        tk.Button(user_row, text="↻", font=FONT_BODY, bg=PANEL, fg=FG,
                  relief="flat", cursor="hand2",
                  command=self._refresh_users).pack(side="left")

        btn_row2 = tk.Frame(hist_card, bg=PANEL)
        btn_row2.pack(fill="x", padx=16, pady=(0, 8))

        tk.Button(btn_row2, text="Show Chart", font=FONT_BODY,
                  bg=ACCENT, fg=BTN_FG, relief="flat", cursor="hand2",
                  padx=10, pady=4, command=self._show_chart).pack(side="left", padx=(0, 8))

        tk.Button(btn_row2, text="Delete User", font=FONT_SML,
                  bg=DANGER, fg=BTN_FG, relief="flat", cursor="hand2",
                  padx=8, pady=4, command=self._delete_user).pack(side="left")

        # Records listbox
        list_frame = tk.Frame(hist_card, bg=PANEL)
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        scrollbar = tk.Scrollbar(list_frame, bg=PANEL)
        scrollbar.pack(side="right", fill="y")

        self.records_lb = tk.Listbox(list_frame, font=FONT_SML,
                                     bg=ENTRY_BG, fg=FG, selectbackground=ACCENT,
                                     relief="flat", yscrollcommand=scrollbar.set,
                                     activestyle="none")
        self.records_lb.pack(fill="both", expand=True)
        scrollbar.config(command=self.records_lb.yview)

        self.hist_user_var.trace_add("write", lambda *_: self._load_history())
        self._refresh_users()

    def _build_result_panel(self, parent):
        # Result display card
        self.result_card = tk.Frame(parent, bg=PANEL)
        self.result_card.pack(fill="x", pady=(0, 12))

        tk.Label(self.result_card, text="Your Result", font=FONT_H2,
                 bg=PANEL, fg=FG).pack(anchor="w", padx=16, pady=(14, 4))

        self.bmi_label = tk.Label(self.result_card, text="—", font=("Segoe UI", 42, "bold"),
                                  bg=PANEL, fg=FG_DIM)
        self.bmi_label.pack(pady=(4, 0))

        self.category_label = tk.Label(self.result_card, text="Enter your data and click Calculate",
                                       font=FONT_H2, bg=PANEL, fg=FG_DIM)
        self.category_label.pack(pady=(0, 6))

        # BMI scale bar
        self._build_scale_bar()

        # Chart area
        self.chart_frame = tk.Frame(parent, bg=PANEL)
        self.chart_frame.pack(fill="both", expand=True)

        tk.Label(self.chart_frame, text="BMI Trend Chart",
                 font=FONT_H2, bg=PANEL, fg=FG).pack(anchor="w", padx=16, pady=(14, 0))

        self.chart_placeholder = tk.Label(
            self.chart_frame,
            text="Select a user and click 'Show Chart' to view BMI trend",
            font=FONT_BODY, bg=PANEL, fg=FG_DIM
        )
        self.chart_placeholder.pack(pady=40)

        self.canvas_widget = None  # holds embedded matplotlib canvas

    def _build_scale_bar(self):
        scale_frame = tk.Frame(self.result_card, bg=PANEL)
        scale_frame.pack(fill="x", padx=16, pady=(4, 14))

        categories = [
            ("Underweight\n< 18.5", "#3498DB"),
            ("Normal\n18.5–24.9", "#27AE60"),
            ("Overweight\n25–29.9", "#E67E22"),
            ("Obese\n≥ 30", "#E74C3C"),
        ]
        for label, color in categories:
            seg = tk.Frame(scale_frame, bg=color, height=10)
            seg.pack(side="left", fill="x", expand=True)
            tk.Label(scale_frame, text=label, font=("Segoe UI", 8),
                     bg=PANEL, fg=color).pack(side="left", expand=True)

    # ── Actions ──────────────────────────────────────────────────────────────

    def _on_calculate(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning("Missing Username", "Please enter a username.")
            return

        try:
            weight, height = validate_inputs(self.weight_var.get(), self.height_var.get())
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        bmi = calculate_bmi(weight, height)
        category, color = classify_bmi(bmi)

        # Update result display
        self.bmi_label.config(text=f"{bmi:.2f}", fg=color)
        self.category_label.config(text=category, fg=color)

        # Save to DB
        try:
            save_record(username, weight, height, bmi, category)
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return

        self._refresh_users()
        # Auto-select this user in history and load their records
        self.hist_user_var.set(username)
        self._load_history()

    def _clear_inputs(self):
        self.weight_var.set("")
        self.height_var.set("")
        self.username_var.set("")
        self.bmi_label.config(text="—", fg=FG_DIM)
        self.category_label.config(text="Enter your data and click Calculate", fg=FG_DIM)

    def _refresh_users(self):
        try:
            users = get_all_users()
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return
        self.user_combo["values"] = users
        if users and not self.hist_user_var.get():
            self.hist_user_var.set(users[0])

    def _load_history(self):
        self.records_lb.delete(0, tk.END)
        username = self.hist_user_var.get().strip()
        if not username:
            return
        try:
            records = get_records(username)
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return

        for rec in reversed(records):
            date, bmi, cat, w, h = rec
            self.records_lb.insert(tk.END, f"  {date[:10]}  BMI {bmi:.2f}  {cat}  ({w}kg / {h}m)")

    def _show_chart(self):
        username = self.hist_user_var.get().strip()
        if not username:
            messagebox.showwarning("No User", "Please select a user first.")
            return

        try:
            records = get_records(username)
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return

        if len(records) < 1:
            messagebox.showinfo("No Data", f"No records found for '{username}'.")
            return

        dates = [datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S") for r in records]
        bmis  = [r[1] for r in records]
        cats  = [r[2] for r in records]

        # Remove old chart
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None
        if self.chart_placeholder.winfo_exists():
            self.chart_placeholder.pack_forget()

        # Build figure
        fig, ax = plt.subplots(figsize=(6, 3.2))
        fig.patch.set_facecolor("#2A2A3E")
        ax.set_facecolor("#1E1E2E")

        # Shade BMI zones
        ax.axhspan(0,    18.5, color="#3498DB", alpha=0.08)
        ax.axhspan(18.5, 25,   color="#27AE60", alpha=0.08)
        ax.axhspan(25,   30,   color="#E67E22", alpha=0.08)
        ax.axhspan(30,   60,   color="#E74C3C", alpha=0.08)

        # Zone reference lines
        for y, lbl, col in [(18.5, "18.5", "#3498DB"), (25, "25", "#E67E22"), (30, "30", "#E74C3C")]:
            ax.axhline(y, color=col, linewidth=0.8, linestyle="--", alpha=0.6)
            ax.text(dates[0], y + 0.3, lbl, color=col, fontsize=7, alpha=0.8)

        # Colour each segment by category
        color_map = {"Underweight": "#3498DB", "Normal": "#27AE60",
                     "Overweight": "#E67E22", "Obese": "#E74C3C"}
        for i in range(len(dates) - 1):
            ax.plot(dates[i:i+2], bmis[i:i+2], color=color_map.get(cats[i], "#9D5CF6"),
                    linewidth=2.5)

        # Scatter points
        point_colors = [color_map.get(c, "#9D5CF6") for c in cats]
        ax.scatter(dates, bmis, c=point_colors, zorder=5, s=55, edgecolors="#1E1E2E", linewidths=0.8)

        # Annotate last point
        ax.annotate(f"{bmis[-1]:.2f}", xy=(dates[-1], bmis[-1]),
                    xytext=(6, 6), textcoords="offset points",
                    color=FG, fontsize=8)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=30)

        ax.set_title(f"BMI Trend — {username}", color=FG, fontsize=11, pad=8)
        ax.set_ylabel("BMI", color=FG_DIM, fontsize=9)
        ax.tick_params(colors=FG_DIM, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#313147")
        ax.yaxis.label.set_color(FG_DIM)

        bmi_vals = bmis[:]
        margin = 2
        ax.set_ylim(max(0, min(bmi_vals) - margin), max(bmi_vals) + margin)

        fig.tight_layout()

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def _delete_user(self):
        username = self.hist_user_var.get().strip()
        if not username:
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete all records for '{username}'? This cannot be undone."):
            return
        try:
            delete_user_records(username)
        except RuntimeError as e:
            messagebox.showerror("Database Error", str(e))
            return

        self.records_lb.delete(0, tk.END)
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None
            self.chart_placeholder.pack(pady=40)

        self._refresh_users()
        messagebox.showinfo("Deleted", f"All records for '{username}' have been removed.")


def main():
    app = BMIApp()
    app.mainloop()


if __name__ == "__main__":
    main()
