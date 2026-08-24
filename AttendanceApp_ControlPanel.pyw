"""
AI Attendance System - Windows 11 Desktop Control Panel (XAMPP-Style)
--------------------------------------------------------------------
Author: AI Attendance Team
Platform: Windows 10 / Windows 11
"""

import os
import sys
import subprocess
import threading
import webbrowser
import time
import socket
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Application Configuration
APP_TITLE = "AI Attendance System - Control Panel"
APP_VERSION = "v2.0 (Windows 11 Edition)"
PORT = 8000
SERVER_URL = f"http://127.0.0.1:{PORT}/"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class AttendanceControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("780x560")
        self.root.minsize(680, 480)
        self.root.configure(bg="#0f172a")  # Dark slate theme

        self.server_process = None
        self.is_running = False

        # Set window icon if available
        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        self._build_ui()
        self._check_initial_server_status()

    def _build_ui(self):
        # 1. Header Frame
        header_frame = tk.Frame(self.root, bg="#1e293b", padx=20, pady=14, relief="flat")
        header_frame.pack(fill="x", side="top")

        title_label = tk.Label(
            header_frame,
            text="📸 AI Classroom Attendance System",
            font=("Segoe UI", 16, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        title_label.pack(side="left")

        version_label = tk.Label(
            header_frame,
            text=APP_VERSION,
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#334155",
            padx=8,
            pady=2
        )
        version_label.pack(side="right")

        # 2. Main Content Frame
        content_frame = tk.Frame(self.root, bg="#0f172a", padx=16, pady=12)
        content_frame.pack(fill="both", expand=True)

        # 2a. Status & Primary Actions Card
        status_card = tk.Frame(content_frame, bg="#1e293b", padx=16, pady=14, relief="ridge", bd=1)
        status_card.pack(fill="x", pady=(0, 10))

        # Status Line
        status_top_row = tk.Frame(status_card, bg="#1e293b")
        status_top_row.pack(fill="x", pady=(0, 10))

        tk.Label(
            status_top_row,
            text="Core Engine Status:",
            font=("Segoe UI", 11, "bold"),
            fg="#f8fafc",
            bg="#1e293b"
        ).pack(side="left")

        self.status_badge = tk.Label(
            status_top_row,
            text="🔴 OFFLINE",
            font=("Segoe UI", 10, "bold"),
            fg="#ef4444",
            bg="#334155",
            padx=10,
            pady=3
        )
        self.status_badge.pack(side="left", padx=10)

        self.port_label = tk.Label(
            status_top_row,
            text=f"Port: {PORT} (0.0.0.0)",
            font=("Consolas", 10),
            fg="#94a3b8",
            bg="#1e293b"
        )
        self.port_label.pack(side="right")

        # Main Server Buttons (Start, Stop, Open Browser)
        btn_row = tk.Frame(status_card, bg="#1e293b")
        btn_row.pack(fill="x", pady=4)

        self.start_btn = tk.Button(
            btn_row,
            text="▶  Start Server",
            font=("Segoe UI", 11, "bold"),
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.start_server
        )
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = tk.Button(
            btn_row,
            text="⏹  Stop Server",
            font=("Segoe UI", 11, "bold"),
            bg="#ef4444",
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            state="disabled",
            command=self.stop_server
        )
        self.stop_btn.pack(side="left", padx=8)

        self.open_browser_btn = tk.Button(
            btn_row,
            text="🌐  Open Web Portal",
            font=("Segoe UI", 11, "bold"),
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda: webbrowser.open(SERVER_URL)
        )
        self.open_browser_btn.pack(side="left", padx=8)

        self.restart_btn = tk.Button(
            btn_row,
            text="🔄  Restart",
            font=("Segoe UI", 10, "bold"),
            bg="#64748b",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.restart_server
        )
        self.restart_btn.pack(side="right")

        # 2b. Quick Links Navigation Grid (XAMPP-Style Modules)
        links_card = tk.Frame(content_frame, bg="#1e293b", padx=12, pady=10, relief="ridge", bd=1)
        links_card.pack(fill="x", pady=(0, 10))

        tk.Label(
            links_card,
            text="⚡ Quick Modules Navigation:",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#1e293b"
        ).pack(anchor="w", pady=(0, 6))

        grid_row = tk.Frame(links_card, bg="#1e293b")
        grid_row.pack(fill="x")

        quick_links = [
            ("📸 Mark Attendance", f"http://127.0.0.1:{PORT}/"),
            ("🎓 Student Registration", f"http://127.0.0.1:{PORT}/register/"),
            ("📋 Attendance Sheet", f"http://127.0.0.1:{PORT}/attendance-sheet/"),
            ("👥 Students List", f"http://127.0.0.1:{PORT}/students/"),
            ("📊 Dashboard", f"http://127.0.0.1:{PORT}/dashboard/"),
            ("⚙️ Admin Panel", f"http://127.0.0.1:{PORT}/admin/"),
        ]

        for text, url in quick_links:
            b = tk.Button(
                grid_row,
                text=text,
                font=("Segoe UI", 8, "bold"),
                bg="#334155",
                fg="#f1f5f9",
                activebackground="#475569",
                activeforeground="#ffffff",
                relief="flat",
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda u=url: webbrowser.open(u)
            )
            b.pack(side="left", padx=3, expand=True, fill="x")

        # 2c. Real-Time Console Logs Terminal
        log_card = tk.Frame(content_frame, bg="#1e293b", padx=12, pady=10, relief="ridge", bd=1)
        log_card.pack(fill="both", expand=True)

        log_header = tk.Frame(log_card, bg="#1e293b")
        log_header.pack(fill="x", pady=(0, 6))

        tk.Label(
            log_header,
            text="💻 Live Server Activity Console:",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        ).pack(side="left")

        clear_btn = tk.Button(
            log_header,
            text="Clear Console",
            font=("Segoe UI", 8),
            bg="#334155",
            fg="#cbd5e1",
            relief="flat",
            padx=6,
            pady=1,
            cursor="hand2",
            command=self._clear_logs
        )
        clear_btn.pack(side="right")

        self.log_area = scrolledtext.ScrolledText(
            log_card,
            bg="#020617",
            fg="#a7f3d0",
            insertbackground="white",
            font=("Consolas", 9),
            relief="flat",
            wrap="word",
            height=10
        )
        self.log_area.pack(fill="both", expand=True)

        # 3. Footer Bar
        footer = tk.Frame(self.root, bg="#0f172a", padx=16, pady=6)
        footer.pack(fill="x", side="bottom")

        tk.Label(
            footer,
            text="💡 Tip: Double-click START_ATTENDANCE_APP.bat on Desktop to launch instantly.",
            font=("Segoe UI", 8),
            fg="#64748b",
            bg="#0f172a"
        ).pack(side="left")

    def _log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)

    def _clear_logs(self):
        self.log_area.delete("1.0", tk.END)

    def _is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    def _check_initial_server_status(self):
        if self._is_port_in_use(PORT):
            self._set_running_state(True)
            self._log(f"Detected existing Django server already running on port {PORT}.")
        else:
            self._set_running_state(False)
            self._log("Control Panel initialized. Ready to start AI Attendance Engine.")

    def _set_running_state(self, running):
        self.is_running = running
        if running:
            self.status_badge.config(text="🟢 ONLINE (RUNNING)", fg="#10b981", bg="#064e3b")
            self.start_btn.config(state="disabled", bg="#64748b")
            self.stop_btn.config(state="normal", bg="#ef4444")
        else:
            self.status_badge.config(text="🔴 STOPPED (OFFLINE)", fg="#ef4444", bg="#450a0a")
            self.start_btn.config(state="normal", bg="#10b981")
            self.stop_btn.config(state="disabled", bg="#64748b")

    def start_server(self):
        if self.is_running:
            return

        self._log("Starting Django Server (python manage.py runserver 0.0.0.0:8000)...")
        
        def run_thread():
            try:
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                self.server_process = subprocess.Popen(
                    [sys.executable, "manage.py", "runserver", f"0.0.0.0:{PORT}"],
                    cwd=BASE_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=creationflags
                )

                self.root.after(0, lambda: self._set_running_state(True))
                self.root.after(0, lambda: self._log(f"Server started successfully at {SERVER_URL}"))

                # Stream stdout to console
                for line in iter(self.server_process.stdout.readline, ''):
                    if not line:
                        break
                    clean_line = line.strip()
                    if clean_line:
                        self.root.after(0, lambda l=clean_line: self._log(l))

                self.server_process.stdout.close()
                self.server_process.wait()
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Error starting server: {e}"))
            finally:
                self.root.after(0, lambda: self._set_running_state(False))

        threading.Thread(target=run_thread, daemon=True).start()

        # Check port after 1.5 seconds and open browser
        def open_browser_delayed():
            time.sleep(1.5)
            if self._is_port_in_use(PORT):
                webbrowser.open(SERVER_URL)

        threading.Thread(target=open_browser_delayed, daemon=True).start()

    def stop_server(self):
        self._log("Stopping server...")
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process = None
            except Exception as e:
                self._log(f"Error terminating process: {e}")

        # Kill any stray processes listening on port 8000 (Windows taskkill)
        if os.name == 'nt':
            try:
                subprocess.run(
                    f'for /f "tokens=5" %a in (\'netstat -aon ^| find ":{PORT}" ^| find "LISTENING"\') do taskkill /f /pid %a',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

        time.sleep(0.5)
        self._set_running_state(False)
        self._log("Server stopped successfully.")

    def restart_server(self):
        self.stop_server()
        time.sleep(1.0)
        self.start_server()


def main():
    root = tk.Tk()
    app = AttendanceControlPanel(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(app, root))
    root.mainloop()


def on_close(app, root):
    if app.is_running:
        if messagebox.askyesno("Exit Control Panel", "Django server is currently running.\nDo you want to stop the server and exit?"):
            app.stop_server()
            root.destroy()
    else:
        root.destroy()


if __name__ == "__main__":
    main()
