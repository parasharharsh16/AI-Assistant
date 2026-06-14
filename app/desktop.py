import threading
import tkinter as tk
from tkinter import ttk

from .assistant import JarvisAssistant


class JarvisDesktopApp:
    BACKGROUND = "#121318"
    PANEL = "#161b23"
    USER_BUBBLE = "#2f6cff"
    ASSISTANT_BUBBLE = "#212830"
    TEXT = "#eef2ff"
    MUTED = "#8b95a1"
    ACCENT = "#6eb1ff"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Jarvis Assistant")
        self.root.geometry("820x720")
        self.root.configure(bg=self.BACKGROUND)
        self.root.minsize(720, 600)
        self.assistant = None

        self._create_widgets()
        self._load_assistant()

    def _create_widgets(self):
        header = tk.Frame(self.root, bg=self.PANEL, bd=0)
        header.pack(fill="x", padx=16, pady=(16, 8))

        title = tk.Label(
            header,
            text="Jarvis Assistant",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 22, "bold"),
        )
        title.pack(anchor="w", padx=12, pady=(12, 0))

        subtitle = tk.Label(
            header,
            text="A modern local assistant with native app style chat.",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", padx=12, pady=(0, 14))

        self.chat_canvas = tk.Canvas(
            self.root,
            bg=self.BACKGROUND,
            highlightthickness=0,
        )
        self.chat_canvas.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.chat_canvas.yview,
        )
        self.scrollbar.place(relx=0.99, rely=0.13, relheight=0.72)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.chat_container = tk.Frame(self.chat_canvas, bg=self.BACKGROUND)
        self.canvas_window = self.chat_canvas.create_window(
            (0, 0), window=self.chat_container, anchor="nw"
        )
        self.chat_container.bind("<Configure>", self._on_frame_configure)
        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)

        self.status_label = tk.Label(
            self.root,
            text="Loading assistant...",
            bg=self.BACKGROUND,
            fg=self.MUTED,
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 8))

        controls = tk.Frame(self.root, bg=self.PANEL)
        controls.pack(fill="x", padx=16, pady=(0, 16))

        self.input_text = tk.Text(
            controls,
            height=4,
            wrap=tk.WORD,
            bg="#181d26",
            fg=self.TEXT,
            insertbackground=self.TEXT,
            font=("Segoe UI", 11),
            bd=0,
            padx=12,
            pady=10,
        )
        self.input_text.pack(fill="both", side="left", expand=True, padx=(12, 10), pady=12)
        self.input_text.bind("<Control-Return>", self._on_ctrl_enter)

        button_frame = tk.Frame(controls, bg=self.PANEL)
        button_frame.pack(side="right", padx=(0, 12), pady=12)

        self.send_button = ttk.Button(button_frame, text="Send", command=self._on_send, state="disabled")
        self.send_button.pack(fill="x", pady=(0, 8))

        self.clear_button = ttk.Button(button_frame, text="Clear", command=self._clear_chat)
        self.clear_button.pack(fill="x")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            foreground=self.TEXT,
            background=self.ACCENT,
            borderwidth=0,
            focusthickness=0,
            padding=10,
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#5c9dfd")],
        )
        self.send_button.configure(style="Accent.TButton")

    def _load_assistant(self):
        thread = threading.Thread(target=self._initialize_assistant, daemon=True)
        thread.start()

    def _initialize_assistant(self):
        try:
            self.assistant = JarvisAssistant()
            self._append_message("system", "Assistant loaded. Press Ctrl+Enter or Send to chat.")
            self._set_status("Ready")
            self.send_button.config(state="normal")
        except Exception as exc:
            self._append_message("system", f"Failed to initialize assistant: {exc}")
            self._set_status("Initialization failed")

    def _set_status(self, text: str):
        self.status_label.config(text=text)

    def _on_frame_configure(self, event):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.chat_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _append_message(self, role: str, text: str):
        bubble_frame = tk.Frame(self.chat_container, bg=self.BACKGROUND)
        bubble_frame.pack(fill="x", pady=6, padx=12)

        if role == "user":
            anchor = "e"
            bg = self.USER_BUBBLE
            fg = "#ffffff"
            padx = (80, 10)
        elif role == "assistant":
            anchor = "w"
            bg = self.ASSISTANT_BUBBLE
            fg = self.TEXT
            padx = (10, 80)
        else:
            anchor = "w"
            bg = self.PANEL
            fg = self.MUTED
            padx = (10, 80)

        bubble = tk.Frame(bubble_frame, bg=bg, bd=0, padx=14, pady=10)
        bubble.pack(anchor=anchor, padx=padx)

        label_text = text if role != "system" else f"{text}"
        label = tk.Label(
            bubble,
            text=label_text,
            justify=tk.LEFT,
            wraplength=520,
            bg=bg,
            fg=fg,
            font=("Segoe UI", 10),
        )
        label.pack()

        if role == "assistant":
            sub_label = tk.Label(
                bubble_frame,
                text="Jarvis",
                bg=self.BACKGROUND,
                fg=self.MUTED,
                font=("Segoe UI", 8, "italic"),
            )
            sub_label.pack(anchor="w", padx=(24, 0), pady=(2, 0))

        self.chat_canvas.yview_moveto(1.0)

    def _on_ctrl_enter(self, event):
        self._on_send()
        return "break"

    def _on_send(self):
        if not self.assistant:
            return

        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            return

        self.input_text.delete("1.0", tk.END)
        self._append_message("user", message)
        self.send_button.config(state="disabled")
        self._set_status("Thinking...")

        thread = threading.Thread(target=self._generate_response, args=(message,), daemon=True)
        thread.start()

    def _clear_chat(self):
        for child in self.chat_container.winfo_children():
            child.destroy()
        self._append_message("system", "Chat cleared. Ready for a new conversation.")

    def _generate_response(self, message: str):
        try:
            response = self.assistant.reply(message)
            self._append_message("assistant", response)
            self._set_status("Ready")
        except Exception as exc:
            self._append_message("system", f"Error generating response: {exc}")
            self._set_status("Error")
        finally:
            self.send_button.config(state="normal")


def main():
    root = tk.Tk()
    JarvisDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
