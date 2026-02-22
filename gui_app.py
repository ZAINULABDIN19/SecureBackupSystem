import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

# ---------------- THEME ----------------

BG_COLOR = "#0f172a"
BTN_COLOR = "#2563eb"
BTN_HOVER = "#1d4ed8"
TEXT_COLOR = "#f1f5f9"
ACCENT = "#22d3ee"
FOOTER_COLOR = "#94a3b8"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 11, "bold")
FONT_FOOTER = ("Segoe UI", 9)


# ---------------- GUI ----------------

class SecureBackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Backup System")
        self.root.geometry("450x450")
        self.root.configure(bg=BG_COLOR)
        self.current_user = None
        self.show_main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def styled_button(self, parent, text, command):
        return tk.Button(parent,
                         text=text,
                         bg=BTN_COLOR,
                         fg="white",
                         activebackground=BTN_HOVER,
                         font=FONT_BUTTON,
                         width=25,
                         height=1,
                         bd=0,
                         cursor="hand2",
                         command=command)

    def add_footer(self):
        footer = tk.Label(self.root,
                          text="Created by Zain ul Abdin  |  Secure Backup System v1.0",
                          font=FONT_FOOTER,
                          fg=FOOTER_COLOR,
                          bg=BG_COLOR)
        footer.pack(side="bottom", pady=10)

    # -------- MAIN MENU --------

    def show_main_menu(self):
        self.clear_window()

        tk.Label(self.root,
                 text="🔐 Secure Backup System",
                 font=FONT_TITLE,
                 fg=ACCENT,
                 bg=BG_COLOR).pack(pady=40)

        self.styled_button(self.root, "Register", self.show_register).pack(pady=10)
        self.styled_button(self.root, "Login", self.show_login).pack(pady=10)
        self.styled_button(self.root, "Exit", self.root.quit).pack(pady=10)

        self.add_footer()

    # -------- REGISTER --------

    def show_register(self):
        self.clear_window()

        tk.Label(self.root,
                 text="Create Account",
                 font=FONT_TITLE,
                 fg=TEXT_COLOR,
                 bg=BG_COLOR).pack(pady=25)

        username = tk.Entry(self.root, font=FONT_LABEL, width=30)
        username.pack(pady=8)
        username.insert(0, "Username")

        password = tk.Entry(self.root, show="*", font=FONT_LABEL, width=30)
        password.pack(pady=8)
        password.insert(0, "Password")

        role = tk.StringVar(value="user")
        tk.OptionMenu(self.root, role, "admin", "user").pack(pady=8)

        def register_action():
            register_user(username.get(), password.get(), role.get())
            messagebox.showinfo("Success", "Registered Successfully")

        self.styled_button(self.root, "Register", register_action).pack(pady=15)
        self.styled_button(self.root, "Back", self.show_main_menu).pack()

        self.add_footer()

    # -------- LOGIN --------

    def show_login(self):
        self.clear_window()

        tk.Label(self.root,
                 text="Login",
                 font=FONT_TITLE,
                 fg=TEXT_COLOR,
                 bg=BG_COLOR).pack(pady=25)

        username = tk.Entry(self.root, font=FONT_LABEL, width=30)
        username.pack(pady=8)
        username.insert(0, "Username")

        password = tk.Entry(self.root, show="*", font=FONT_LABEL, width=30)
        password.pack(pady=8)
        password.insert(0, "Password")

        def login_action():
            if authenticate(username.get(), password.get()):
                self.current_user = username.get()
                global current_user
                current_user = self.current_user
                messagebox.showinfo("Success", "Login Successful")
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Login Failed")

        self.styled_button(self.root, "Login", login_action).pack(pady=15)
        self.styled_button(self.root, "Back", self.show_main_menu).pack()

        self.add_footer()

    # -------- DASHBOARD --------

    def show_dashboard(self):
        self.clear_window()

        role = get_role(self.current_user)

        tk.Label(self.root,
                 text=f"Dashboard ({role.upper()})",
                 font=FONT_TITLE,
                 fg=ACCENT,
                 bg=BG_COLOR).pack(pady=25)

        if role == "admin":
            self.styled_button(
                self.root,
                "Generate RSA Keys",
                lambda: [generate_rsa_keys(),
                         messagebox.showinfo("Done", "RSA Keys Generated")]
            ).pack(pady=8)

        self.styled_button(self.root, "Create Backup",
                           self.create_backup_gui).pack(pady=8)

        self.styled_button(self.root, "List Backups",
                           self.list_backups_gui).pack(pady=8)

        if role == "admin":
            self.styled_button(self.root, "Restore Backup",
                               self.restore_backup_gui).pack(pady=8)

        self.styled_button(self.root, "Logout",
                           self.show_main_menu).pack(pady=15)

        self.add_footer()

    # -------- BACKUP ACTIONS --------

    def create_backup_gui(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            create_backup(file_path)
            messagebox.showinfo("Success", "Backup Created Successfully")

    def list_backups_gui(self):
        backups = list_backups()
        if backups:
            messagebox.showinfo("Available Backups", "\n".join(backups))
        else:
            messagebox.showinfo("Backups", "No backups found")

    def restore_backup_gui(self):
        backups = list_backups()
        if not backups:
            messagebox.showerror("Error", "No backups available")
            return

        backup_name = simpledialog.askstring("Restore", "Enter backup name:")
        if backup_name:
            output_file = filedialog.asksaveasfilename()
            if output_file:
                restore_backup(backup_name, output_file)
                messagebox.showinfo("Success", "Backup Restored Successfully")


# -------- START GUI --------

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureBackupGUI(root)
    root.mainloop()