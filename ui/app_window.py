import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import datetime
from core.speedtest_runner import run_full_test
from core.history import HistoryManager
from utils.fileio import save_history_to_csv


class SpeedTestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Internet Speed Test")
        self.geometry("480x350")
        self.resizable(False, False)

        self.history = HistoryManager(limit=50)
        self._init_ui()

        self.test_thread = None
        self.stop_flag = threading.Event()

    def _init_ui(self):
        pad = 8

        main = ttk.Frame(self, padding=pad)
        main.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main, textvariable=self.status_var).pack(anchor="w")

        self.download_var = tk.StringVar(value="Download: - Mbps")
        self.upload_var = tk.StringVar(value="Upload: - Mbps")
        self.ping_var = tk.StringVar(value="Ping: - ms")
        self.server_var = tk.StringVar(value="Server: Auto")

        ttk.Label(main, textvariable=self.download_var, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(main, textvariable=self.upload_var, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(main, textvariable=self.ping_var).pack(anchor="w", pady=(6,0))
        ttk.Label(main, textvariable=self.server_var, font=("Segoe UI", 8, "italic")).pack(anchor="w")

        self.progress = ttk.Progressbar(main, mode="indeterminate")
        self.progress.pack(fill="x", pady=10)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x")

        self.start_btn = ttk.Button(btn_frame, text="Start Test", command=self.start_test)
        self.start_btn.pack(side="left", padx=(0,6))

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_test, state="disabled")
        self.stop_btn.pack(side="left")

        ttk.Button(btn_frame, text="Save CSV", command=self.save_csv).pack(side="right")
        ttk.Button(btn_frame, text="Clear", command=self.clear_results).pack(side="right", padx=(6,0))

        ttk.Label(main, text="History:").pack(anchor="w", pady=(12,0))
        self.history_box = tk.Listbox(main, height=5)
        self.history_box.pack(fill="both", expand=True)

    def start_test(self):
        if self.test_thread and self.test_thread.is_alive():
            messagebox.showinfo("Running", "Speed test already running.")
            return

        self.stop_flag.clear()
        self.progress.start(10)
        self.status_var.set("Starting test...")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.test_thread = threading.Thread(target=self._run_thread, daemon=True)
        self.test_thread.start()

    def stop_test(self):
        self.stop_flag.set()
        self.status_var.set("Stopping...")

    def _run_thread(self):
        try:
            result = run_full_test(self.stop_flag, lambda s: self.status_var.set(s))
            if result is None:
                self.after(0, lambda: self._finish("Stopped"))
                return

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.add({
                "timestamp": timestamp,
                **result
            })

            self.after(0, lambda: self._display_result(result, timestamp))

        except Exception as e:
            self.after(0, lambda: self._finish(f"Error: {e}"))

    def _display_result(self, data, timestamp):
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        self.download_var.set(f"Download: {data['download']:.2f} Mbps")
        self.upload_var.set(f"Upload: {data['upload']:.2f} Mbps")
        self.ping_var.set(f"Ping: {data['ping']:.0f} ms")
        self.server_var.set(f"Server: {data['server']}")

        self.status_var.set(f"Completed: {timestamp}")

        self.refresh_history()

    def _finish(self, msg):
        self.progress.stop()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set(msg)

    def clear_results(self):
        self.download_var.set("Download: - Mbps")
        self.upload_var.set("Upload: - Mbps")
        self.ping_var.set("Ping: - ms")
        self.server_var.set("Server: Auto")
        self.status_var.set("Ready")

    def refresh_history(self):
        self.history_box.delete(0, tk.END)
        for h in self.history.get_all():
            line = f"{h['timestamp']} | {h['download']:.2f}/{h['upload']:.2f} Mbps | {h['ping']:.0f} ms"
            self.history_box.insert(0, line)

    def save_csv(self):
        if not self.history.get_all():
            messagebox.showinfo("No Data", "No history to save.")
            return

        fname = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
        if not fname:
            return

        save_history_to_csv(fname, self.history.get_all())
        messagebox.showinfo("Saved", f"Saved to {fname}")
