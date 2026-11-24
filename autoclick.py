import time
import threading
import customtkinter as ctk
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

DEFAULT_DELAY = 0.001
START_STOP_KEY = KeyCode(char="/")  # inicia/para
EXIT_KEY = KeyCode(char="-")        # encerra
mouse = Controller()


class ClickMouse(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.delay = DEFAULT_DELAY
        self.button = Button.left
        self.running = False
        self.program_running = True
        self.lock = threading.Lock()

    def toggle(self):
        with self.lock:
            self.running = not self.running

    def exit(self):
        with self.lock:
            self.running = False
            self.program_running = False

    def run(self):
        while self.program_running:
            with self.lock:
                running, delay, button = self.running, self.delay, self.button
            if running:
                mouse.click(button)
                time.sleep(max(delay, 0.001))
            else:
                time.sleep(0.01)


class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("AutoClicker")
        self.geometry("460x600")
        self.resizable(False, False)

        self.click_thread = ClickMouse()
        self.click_thread.start()
        self.listener = None
        self.pressed_keys = set()
        self.closing = False

        self.create_widgets()
        self.listener = Listener(on_press=self.on_key_press,
                                 on_release=self.on_key_release)
        self.listener.daemon = True
        self.listener.start()
        self.update_interface()
        self.protocol("WM_DELETE_WINDOW", self.close_application)

    def create_widgets(self):
        ctk.CTkLabel(self, text="AUTOCLICKER",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(28, 4))
        ctk.CTkLabel(self, text="Controle pelo teclado",
                     text_color="gray").pack(pady=(0, 0))
        ctk.CTkLabel(self,text="Criado por: arthursearom",
                     font=ctk.CTkFont(size=11),
                     text_color="gray").pack(pady=(0, 0))

        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.pack(fill="x", padx=28, pady=8)
        self.status_label = ctk.CTkLabel(
            panel, text="● PARADO",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ff5555")
        self.status_label.pack(pady=16)

        ctk.CTkLabel(self, text="Intervalo entre cliques (segundos)").pack(pady=(18, 5))
        self.delay_entry = ctk.CTkEntry(self, width=250, placeholder_text="Ex.: 0.001")
        self.delay_entry.insert(0, str(DEFAULT_DELAY))
        self.delay_entry.pack(pady=4)
        ctk.CTkLabel(self, text="0.001 = 1 ms (mínimo: 1 ms)",
                     text_color="gray").pack(pady=(2, 12))

        ctk.CTkLabel(self, text="Botão do mouse").pack(pady=(6, 5))
        self.button_menu = ctk.CTkOptionMenu(
            self, width=250, values=["Esquerdo", "Direito", "Meio"],
            command=self.change_button)
        self.button_menu.set("Esquerdo")
        self.button_menu.pack(pady=4)

        ctk.CTkButton(self, text="Aplicar configurações", width=250,
                      command=self.apply_settings).pack(pady=(12, 15))

        hotkeys = ctk.CTkFrame(self, corner_radius=12)
        hotkeys.pack(fill="x", padx=28, pady=5)
        ctk.CTkLabel(hotkeys, text="ATALHOS DO TECLADO",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(12, 6))
        ctk.CTkLabel(hotkeys, text="/ — Iniciar / parar autoclicker").pack(pady=3)
        ctk.CTkLabel(hotkeys, text="- — Encerrar aplicativo").pack(pady=(3, 12))
        ctk.CTkLabel(self, text="Não existem botões de iniciar/parar.",
                     text_color="gray").pack(pady=(10, 0))

    def change_button(self, choice):
        self.click_thread.button = {
            "Esquerdo": Button.left,
            "Direito": Button.right,
            "Meio": Button.middle
        }[choice]

    def apply_settings(self):
        try:
            delay = float(self.delay_entry.get().strip().replace(",", "."))
            if delay < 0.001:
                raise ValueError
        except ValueError:
            self.status_label.configure(text="● INTERVALO INVÁLIDO",
                                        text_color="#ffb020")
            return
        self.click_thread.delay = delay
        self.update_interface()

    def on_key_press(self, key):
        if key in self.pressed_keys:
            return
        self.pressed_keys.add(key)
        if key == START_STOP_KEY:
            self.click_thread.toggle()
            self.after(0, self.update_interface)
        elif key == EXIT_KEY:
            self.after(0, self.close_application)

    def on_key_release(self, key):
        self.pressed_keys.discard(key)

    def update_interface(self):
        if self.closing:
            return
        if self.click_thread.running:
            self.status_label.configure(text="● CLICANDO — pressione / para parar",
                                        text_color="#00d26a")
        else:
            self.status_label.configure(text="● PARADO — pressione / para iniciar",
                                        text_color="#ff5555")

    def close_application(self):
        if self.closing:
            return
        self.closing = True
        self.click_thread.exit()
        if self.listener:
            self.listener.stop()
        self.destroy()


if __name__ == "__main__":
    app = AutoClickerApp()
    app.mainloop()
