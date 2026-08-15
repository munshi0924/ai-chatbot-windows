import os
import threading
import customtkinter as ctk
from openai import OpenAI


class ChatbotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Settings ---
        self.title("My AI Chatbot — Multi-Model")
        self.geometry("950x750")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # --- OpenAI Client ---
        self.client = OpenAI()

        # --- Available Models ---
        self.models = {
            "GPT-5.6 Sol  ⭐ Best (Flagship)": "gpt-5.6-sol",
            "GPT-5.6 Terra  ⚖️ Balanced": "gpt-5.6-terra",
            "GPT-5.6 Luna  🚀 Fast/Cheap": "gpt-5.6-luna",
            "GPT-5.5 Instant  💬 Default": "gpt-5.5-instant",
            "GPT-4o  🧠 Smart": "gpt-4o",
            "GPT-4o-mini  💰 Cheapest": "gpt-4o-mini",
        }
        self.current_model = ctk.StringVar(value="GPT-5.6 Sol  ⭐ Best (Flagship)")

        # --- Conversation Memory ---
        self.messages = [
            {"role": "system", "content": "You are a helpful, friendly assistant."}
        ]

        # --- UI Layout ---
        self._build_ui()

    def _build_ui(self):
        # ===== MODEL SELECTOR FRAME =====
        model_frame = ctk.CTkFrame(self, fg_color="transparent")
        model_frame.pack(padx=15, pady=(15, 5), fill="x")

        model_label = ctk.CTkLabel(
            model_frame,
            text="Model:",
            font=("Segoe UI", 13, "bold")
        )
        model_label.pack(side="left", padx=(0, 10))

        self.model_dropdown = ctk.CTkOptionMenu(
            model_frame,
            values=list(self.models.keys()),
            variable=self.current_model,
            font=("Segoe UI", 13),
            dropdown_font=("Segoe UI", 12),
            width=320,
            command=self._on_model_change
        )
        self.model_dropdown.pack(side="left")

        self.model_info_label = ctk.CTkLabel(
            model_frame,
            text="Flagship reasoning model. Best for complex coding, research & science.",
            font=("Segoe UI", 11),
            text_color="gray"
        )
        self.model_info_label.pack(side="left", padx=(15, 0))

        # ===== CHAT DISPLAY =====
        self.chat_display = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Segoe UI", 14),
            state="disabled"
        )
        self.chat_display.pack(padx=15, pady=(10, 5), fill="both", expand=True)

        # ===== INPUT FRAME =====
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(padx=15, pady=(5, 5), fill="x")

        self.user_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message and press Enter...",
            font=("Segoe UI", 14),
            height=42
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            font=("Segoe UI", 14, "bold"),
            width=110,
            height=42,
            command=self.send_message
        )
        self.send_button.pack(side="right")

        # ===== STATUS BAR =====
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready  |  Using: GPT-5.6 Sol",
            font=("Segoe UI", 11),
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 12))

        # Welcome message
        self._add_text("System", "Welcome! Select a model from the dropdown and start chatting.\n")

    def _on_model_change(self, selected_name):
        """Update info label and status when user switches models."""
        model_id = self.models[selected_name]

        descriptions = {
            "gpt-5.6-sol": "Flagship reasoning model. Best for complex coding, research & science.",
            "gpt-5.6-terra": "Balanced everyday model. Matches GPT-5.5 quality at half the price.",
            "gpt-5.6-luna": "Lightning-fast & ultra-cheap. Great for high-volume simple tasks.",
            "gpt-5.5-instant": "OpenAI's default ChatGPT model. Fast, natural everyday responses.",
            "gpt-4o": "Highly capable multimodal model. Great for vision, coding, and writing.",
            "gpt-4o-mini": "Smallest & cheapest. Good for simple Q&A and classification.",
        }

        self.model_info_label.configure(text=descriptions.get(model_id, ""))
        self.status_label.configure(text=f"Ready  |  Using: {selected_name.split('  ')[0]}")
        self._add_text("System", f"Switched to {selected_name.split('  ')[0]}.\n")

    def send_message(self):
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self.user_input.delete(0, "end")
        self.send_button.configure(state="disabled")
        self.status_label.configure(text="Thinking...")

        self._add_text("You", user_text)
        self.messages.append({"role": "user", "content": user_text})

        thread = threading.Thread(target=self._fetch_response, daemon=True)
        thread.start()

    def _fetch_response(self):
        try:
            selected_name = self.current_model.get()
            model_id = self.models[selected_name]

            stream = self.client.chat.completions.create(
                model=model_id,
                messages=self.messages,
                stream=True
            )

            self.after(0, lambda: self._start_bot_message())

            full_response = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    self.after(0, lambda t=delta: self._append_bot_text(t))

            # ═══════════════════════════════════════════════════════
            # FIX ADDED HERE: Insert blank lines after bot finishes
            # so the next "You: ..." appears on a new line.
            # ═══════════════════════════════════════════════════════
            self.after(0, lambda: self._append_bot_text("\n\n"))

            self.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            self.after(0, lambda: self._add_text("Error", str(e)))

        finally:
            self.after(0, self._reset_ui)

    def _start_bot_message(self):
        self._add_text("Bot", "", end="")

    def _append_bot_text(self, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _add_text(self, sender, message, end="\n\n"):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}{end}")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _reset_ui(self):
        self.send_button.configure(state="normal")
        selected_name = self.current_model.get()
        self.status_label.configure(text=f"Ready  |  Using: {selected_name.split('  ')[0]}")
        self.user_input.focus()


if __name__ == "__main__":
    app = ChatbotApp()
    app.mainloop()