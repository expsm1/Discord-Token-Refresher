"""
Bot Token Refresher – Modern GUI (Resizable)
Regain control of your Discord bot if a third‑party service has taken over your token.

Requirements:
    pip install customtkinter
"""

import threading
import webbrowser
from typing import Optional

import customtkinter as ctk
import requests

# ---- Theme ----
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DISCORD_API_BASE = "https://discord.com/api/v9"
DEVELOPER_PORTAL_URL = "https://discord.com/developers/applications"

LOG_COLORS = {
    "white": "#DCE4EE",
    "red": "#F1554C",
    "green": "#4CAF7D",
    "blue": "#3B9EFF",
    "yellow": "#E5C07B",
}


def format_bot_tag(bot_info: dict) -> str:
    username = bot_info.get("username", "Unknown")
    discriminator = bot_info.get("discriminator")
    if discriminator and discriminator != "0":
        return f"{username}#{discriminator}"
    return username


class DiscordTokenClient:
    def __init__(self, token: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bot {token}"})

    def get_bot_info(self) -> requests.Response:
        return self.session.get(f"{DISCORD_API_BASE}/users/@me", timeout=10)

    def regenerate_token(self) -> requests.Response:
        return self.session.post(f"{DISCORD_API_BASE}/applications/@me/oauth2/regenerate", timeout=10)


class TokenRefresher(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Bot Token Refresher")
        self.geometry("800x600")
        self.minsize(700, 500)
        self.resizable(True, True)  # allow full screen and resizing

        # ---- Main Layout (all expandable) ----
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_rowconfigure(5, weight=1)  # output area expands
        main_frame.grid_columnconfigure(0, weight=1)

        # ---- Header ----
        header = ctk.CTkLabel(main_frame, text="Bot Token Refresher", font=("Segoe UI", 24, "bold"))
        header.grid(row=0, column=0, pady=(0, 5), sticky="w")

        desc = ctk.CTkLabel(main_frame, text="Regain control of your bot if a third-party service has your token.",
                             font=("Segoe UI", 12), text_color="gray")
        desc.grid(row=1, column=0, pady=(0, 15), sticky="w")

        # ---- Token Entry ----
        token_frame = ctk.CTkFrame(main_frame)
        token_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        token_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(token_frame, text="Paste your bot token:", font=("Segoe UI", 14)).grid(row=0, column=0, sticky="w")

        self.token_entry = ctk.CTkEntry(token_frame, placeholder_text="Enter your token here...", show="*", height=40)
        self.token_entry.grid(row=1, column=0, sticky="ew", pady=5)

        # Show/Hide Toggle
        self.show_token = False
        show_btn = ctk.CTkButton(token_frame, text="👁️ Show", command=self.toggle_show_token, width=80, height=30)
        show_btn.grid(row=1, column=1, padx=(10, 0), sticky="e")

        # ---- Refresh Button ----
        self.refresh_btn = ctk.CTkButton(main_frame, text="Refresh Token", command=self.start_refresh, height=50, font=("Segoe UI", 16))
        self.refresh_btn.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # ---- Progress Bar ----
        self.progress = ctk.CTkProgressBar(main_frame, height=10)
        self.progress.grid(row=4, column=0, sticky="ew", pady=(0, 5))
        self.progress.set(0)

        # ---- Output Area (expands) ----
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        output_frame.grid_rowconfigure(1, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(output_frame, text="Output", font=("Segoe UI", 14)).grid(row=0, column=0, sticky="w")

        self.output = ctk.CTkTextbox(output_frame, font=("Consolas", 12), wrap="word")
        self.output.grid(row=1, column=0, sticky="nsew", pady=5)
        for tag, color in LOG_COLORS.items():
            self.output._textbox.tag_config(tag, foreground=color)

        # ---- Bottom Buttons ----
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(btn_frame, text="Copy New Token", command=self.copy_token, width=150).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Open Developer Portal", command=self.open_portal, width=200).grid(row=0, column=1, padx=5)

        self.new_token: Optional[str] = None  # store for copy

    def toggle_show_token(self) -> None:
        self.show_token = not self.show_token
        self.token_entry.configure(show="" if self.show_token else "*")

    def log(self, msg: str, color: str = "white") -> None:
        self.after(0, self._write_log, msg, color)

    def _write_log(self, msg: str, color: str) -> None:
        self.output.insert("end", msg + "\n", color)
        self.output.see("end")

    def set_progress(self, value: float) -> None:
        self.after(0, self.progress.set, value)

    def start_refresh(self) -> None:
        token = self.token_entry.get().strip()
        if not token:
            self.log("Please paste your bot token first.", "red")
            return

        self.refresh_btn.configure(state="disabled", text="Refreshing...")
        self.progress.set(0.2)
        self.output.delete("1.0", "end")

        threading.Thread(target=self._refresh_worker, args=(token,), daemon=True).start()

    def _refresh_worker(self, token: str) -> None:
        client = DiscordTokenClient(token)
        try:
            self.log("Verifying token...", "blue")
            self.set_progress(0.4)

            response = client.get_bot_info()
            if response.status_code != 200:
                self.log(f"Invalid token (HTTP {response.status_code})", "red")
                self.set_progress(0)
                return

            bot_info = response.json()
            self.log(f"Bot found: {format_bot_tag(bot_info)}", "green")
            self.set_progress(0.6)

            self.log("Regenerating token...", "blue")
            regen_response = client.regenerate_token()

            if regen_response.status_code == 200:
                self.new_token = regen_response.json().get("token")
                self.log(f"New token generated:\n{self.new_token}", "green")
                self.log("This token invalidates the old one. The third-party service can no longer use it.", "yellow")
                self.set_progress(1.0)
            else:
                self.log(f"Failed to regenerate token (HTTP {regen_response.status_code})", "red")
                self.log("Try regenerating manually in the Developer Portal.", "yellow")
                self.set_progress(0)

            self.log("Opening Discord Developer Portal...", "blue")
            webbrowser.open(DEVELOPER_PORTAL_URL)

        except requests.exceptions.RequestException as e:
            self.log(f"Network error: {e}", "red")
            self.set_progress(0)
        except Exception as e:
            self.log(f"Error: {e}", "red")
            self.set_progress(0)
        finally:
            self.after(0, self._reset_refresh_button)

    def _reset_refresh_button(self) -> None:
        self.refresh_btn.configure(state="normal", text="Refresh Token")

    def copy_token(self) -> None:
        if self.new_token:
            self.clipboard_clear()
            self.clipboard_append(self.new_token)
            self.log("Token copied to clipboard!", "green")
        else:
            self.log("No token to copy. Refresh first.", "red")

    def open_portal(self) -> None:
        webbrowser.open(DEVELOPER_PORTAL_URL)


if __name__ == "__main__":
    app = TokenRefresher()
    app.mainloop()