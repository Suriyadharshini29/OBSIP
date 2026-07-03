import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

# Character sets
UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = string.punctuation
AMBIGUOUS = set("0Ol1I")

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator")
        self.root.resizable(False, False)
        self.history = []
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        # --- Length ---
        lf_len = ttk.LabelFrame(self.root, text="Password Length")
        lf_len.grid(row=0, column=0, columnspan=2, sticky="ew", **pad)

        self.length_var = tk.IntVar(value=16)
        ttk.Label(lf_len, text="Length:").grid(row=0, column=0, padx=6)
        self.length_spin = ttk.Spinbox(lf_len, from_=8, to=128, textvariable=self.length_var, width=5)
        self.length_spin.grid(row=0, column=1, padx=6)
        self.length_slider = ttk.Scale(lf_len, from_=8, to=128, variable=self.length_var, orient="horizontal", length=220)
        self.length_slider.grid(row=0, column=2, padx=6, pady=4)

        # --- Character Types ---
        lf_chars = ttk.LabelFrame(self.root, text="Character Types")
        lf_chars.grid(row=1, column=0, columnspan=2, sticky="ew", **pad)

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        self.exclude_ambiguous = tk.BooleanVar(value=False)

        ttk.Checkbutton(lf_chars, text="Uppercase (A-Z)", variable=self.use_upper).grid(row=0, column=0, sticky="w", padx=8)
        ttk.Checkbutton(lf_chars, text="Lowercase (a-z)", variable=self.use_lower).grid(row=0, column=1, sticky="w", padx=8)
        ttk.Checkbutton(lf_chars, text="Numbers (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w", padx=8)
        ttk.Checkbutton(lf_chars, text="Symbols (!@#...)", variable=self.use_symbols).grid(row=1, column=1, sticky="w", padx=8)
        ttk.Checkbutton(lf_chars, text="Exclude ambiguous chars (0, O, l, 1, I)", variable=self.exclude_ambiguous).grid(
            row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 4))

        # --- Generate Button ---
        ttk.Button(self.root, text="Generate Password", command=self.generate).grid(
            row=2, column=0, columnspan=2, pady=8)

        # --- Password Output ---
        lf_out = ttk.LabelFrame(self.root, text="Generated Password")
        lf_out.grid(row=3, column=0, columnspan=2, sticky="ew", **pad)

        self.password_var = tk.StringVar()
        pw_entry = ttk.Entry(lf_out, textvariable=self.password_var, font=("Courier", 13), width=36, state="readonly")
        pw_entry.grid(row=0, column=0, padx=8, pady=6)

        copy_state = "normal" if CLIPBOARD_AVAILABLE else "disabled"
        self.copy_btn = ttk.Button(lf_out, text="Copy", command=self.copy_to_clipboard, state=copy_state)
        self.copy_btn.grid(row=0, column=1, padx=4)

        # --- Strength Indicator ---
        lf_str = ttk.LabelFrame(self.root, text="Password Strength")
        lf_str.grid(row=4, column=0, columnspan=2, sticky="ew", **pad)

        self.strength_label = ttk.Label(lf_str, text="—", font=("Helvetica", 11, "bold"), width=10)
        self.strength_label.grid(row=0, column=0, padx=8)
        self.strength_bar = ttk.Progressbar(lf_str, length=200, maximum=100)
        self.strength_bar.grid(row=0, column=1, padx=8, pady=6)

        # --- History ---
        lf_hist = ttk.LabelFrame(self.root, text="Last 5 Passwords (session only)")
        lf_hist.grid(row=5, column=0, columnspan=2, sticky="ew", **pad)

        self.history_list = tk.Listbox(lf_hist, font=("Courier", 10), height=5, width=48, selectmode="single")
        self.history_list.grid(row=0, column=0, padx=8, pady=6)

    def _get_charset(self):
        charset = ""
        required = []
        exclude = AMBIGUOUS if self.exclude_ambiguous.get() else set()

        def filtered(chars):
            return "".join(c for c in chars if c not in exclude)

        if self.use_upper.get():
            fc = filtered(UPPERCASE)
            charset += fc
            required.append(fc)
        if self.use_lower.get():
            fc = filtered(LOWERCASE)
            charset += fc
            required.append(fc)
        if self.use_digits.get():
            fc = filtered(DIGITS)
            charset += fc
            required.append(fc)
        if self.use_symbols.get():
            fc = filtered(SYMBOLS)
            charset += fc
            required.append(fc)

        return charset, required

    def _calc_strength(self, password, num_types):
        length = len(password)
        score = 0
        if length >= 8:  score += 20
        if length >= 12: score += 20
        if length >= 16: score += 20
        if length >= 20: score += 10
        score += num_types * 10  # up to 40 for 4 types
        score = min(score, 100)

        if score < 40:
            return "Weak", score, "red"
        elif score < 70:
            return "Medium", score, "orange"
        else:
            return "Strong", score, "green"

    def generate(self):
        length = self.length_var.get()
        if length < 8:
            messagebox.showerror("Invalid Length", "Password length must be at least 8.")
            return

        charset, required = self._get_charset()
        if len(required) < 2:
            messagebox.showerror("Too Few Types", "Please select at least 2 character types.")
            return
        if not charset:
            messagebox.showerror("Empty Charset", "No characters available after filtering.")
            return

        # Guarantee at least one char from each selected type
        password_chars = [secrets.choice(pool) for pool in required]
        remaining = length - len(password_chars)
        password_chars += [secrets.choice(charset) for _ in range(remaining)]

        # Shuffle securely
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        password = "".join(password_chars)
        self.password_var.set(password)

        # Strength
        label, score, color = self._calc_strength(password, len(required))
        self.strength_label.config(text=label, foreground=color)
        self.strength_bar["value"] = score

        # History (last 5, no persistence)
        self.history.insert(0, password)
        self.history = self.history[:5]
        self.history_list.delete(0, tk.END)
        for pw in self.history:
            self.history_list.insert(tk.END, pw)

        # Auto-copy if available
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(password)

    def copy_to_clipboard(self):
        pw = self.password_var.get()
        if not pw:
            return
        pyperclip.copy(pw)
        messagebox.showinfo("Copied", "Password copied to clipboard.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
