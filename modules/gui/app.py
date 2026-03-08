import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import screeninfo

from modules.gui import (
    AppConfig,
    AppConstants,
    ConfigManager,
    RegionSelector,
    Region,
    AutotyperEngine,
    Stats
)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AutotypeGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ATF Autotyper")
        self.geometry(f"{AppConstants.WINDOW_WIDTH}x{AppConstants.WINDOW_HEIGHT}")
        self.resizable(False, False)

        self.region: Region = None
        self.running = False
        self.thread: threading.Thread = None
        self.stop_event: threading.Event = None
        self.stats = Stats()
        self.config: AppConfig = None
        self.engine: AutotyperEngine = None

        self.load_config()
        self.create_widgets()
        self.bind_shortcuts()

    def load_config(self):
        self.config = ConfigManager.load()

    def save_config(self):
        if self.config:
            ConfigManager.save(self.config)

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_config_panel()
        self.create_status_panel()
        self.create_stats_panel()
        self.create_control_bar()

    def create_config_panel(self):
        config_frame = ctk.CTkFrame(self, corner_radius=10)
        config_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        title = ctk.CTkLabel(config_frame, text="Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=(15, 10))

        monitors = screeninfo.get_monitors() or []
        monitor_options = [str(i + 1) for i in range(len(monitors))] if monitors else ["1"]

        ctk.CTkLabel(config_frame, text="Monitor:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.monitor_combo = ctk.CTkComboBox(config_frame, values=monitor_options, state="readonly")
        self.monitor_combo.set(str(self.config.monitor_id))
        self.monitor_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(config_frame, text="Speed (KPM):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.speed_slider = ctk.CTkSlider(
            config_frame, 
            from_=AppConstants.SPEED_MIN, 
            to=AppConstants.SPEED_MAX, 
            number_of_steps=AppConstants.SPEED_MAX - AppConstants.SPEED_MIN
        )
        self.speed_slider.set(self.config.typing_speed)
        self.speed_slider.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.speed_label = ctk.CTkLabel(config_frame, text=f"{self.config.typing_speed} KPM")
        self.speed_label.grid(row=3, column=0, columnspan=2, pady=0)
        self.speed_slider.configure(command=self.on_speed_change)

        self.switch_kb_check = ctk.CTkCheckBox(
            config_frame, 
            text="Switch KB Layout on Start", 
            command=self.on_config_change
        )
        self.switch_kb_check.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        if self.config.switch_kb_layout:
            self.switch_kb_check.select()

        self.fix_qwerty_check = ctk.CTkCheckBox(config_frame, text="Fix QWERTY Z/Y", command=self.on_config_change)
        self.fix_qwerty_check.grid(row=5, column=0, columnspan=2, padx=10, pady=5)
        if self.config.fix_qwerty:
            self.fix_qwerty_check.select()

        ctk.CTkLabel(config_frame, text="API Key:").grid(row=6, column=0, padx=10, pady=(10, 5), sticky="nw")
        self.api_key_entry = ctk.CTkEntry(config_frame, show="*", placeholder_text="Mistral API Key")
        self.api_key_entry.insert(0, self.config.api_key)
        self.api_key_entry.grid(row=6, column=1, padx=10, pady=(10, 5), sticky="ew")

        save_btn = ctk.CTkButton(
            config_frame, 
            text="Save Config", 
            command=self.save_config, 
            fg_color="green", 
            hover_color="darkgreen"
        )
        save_btn.grid(row=7, column=0, columnspan=2, padx=10, pady=15)

    def create_status_panel(self):
        status_frame = ctk.CTkFrame(self, corner_radius=10)
        status_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew", rowspan=2)
        status_frame.grid_rowconfigure(5, weight=1)

        title = ctk.CTkLabel(status_frame, text="Status Dashboard", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=(15, 10))

        ctk.CTkLabel(status_frame, text="State:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.state_label = ctk.CTkLabel(status_frame, text="Idle", text_color="gray", font=ctk.CTkFont(weight="bold"))
        self.state_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(status_frame, text="Region:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.region_label = ctk.CTkLabel(status_frame, text="Not selected", text_color="gray")
        self.region_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(status_frame, text="Current WPM:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.wpm_label = ctk.CTkLabel(status_frame, text="--", text_color="gray", font=ctk.CTkFont(weight="bold"))
        self.wpm_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(status_frame, text="Last Text:").grid(row=4, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nw")
        self.last_text_box = ctk.CTkTextbox(status_frame, wrap="word")
        self.last_text_box.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.last_text_box.insert("1.0", "(none)")
        self.last_text_box.configure(state="disabled")

    def create_stats_panel(self):
        stats_frame = ctk.CTkFrame(self, corner_radius=10)
        stats_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        title = ctk.CTkLabel(stats_frame, text="Statistics", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 10))

        self.slides_label = ctk.CTkLabel(stats_frame, text="Slides: 0", font=ctk.CTkFont(size=14))
        self.slides_label.grid(row=1, column=0, padx=20, pady=5)

        self.errors_label = ctk.CTkLabel(stats_frame, text="Errors: 0", font=ctk.CTkFont(size=14))
        self.errors_label.grid(row=1, column=1, padx=20, pady=5)

        self.chars_label = ctk.CTkLabel(stats_frame, text="Characters: 0", font=ctk.CTkFont(size=14))
        self.chars_label.grid(row=2, column=0, padx=20, pady=5)

        self.time_label = ctk.CTkLabel(stats_frame, text="Time: 0:00", font=ctk.CTkFont(size=14))
        self.time_label.grid(row=2, column=1, padx=20, pady=5)

    def create_control_bar(self):
        control_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        control_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

        self.select_btn = ctk.CTkButton(
            control_frame, 
            text="Select Region", 
            command=self.select_region, 
            height=40
        )
        self.select_btn.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        self.start_btn = ctk.CTkButton(
            control_frame, 
            text="START (F5)", 
            command=self.start_autotype, 
            fg_color="green", 
            hover_color="darkgreen", 
            height=40, 
            state="disabled"
        )
        self.start_btn.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.stop_btn = ctk.CTkButton(
            control_frame, 
            text="STOP (F6)", 
            command=self.stop_autotype,
            fg_color="red", 
            hover_color="darkred", 
            height=40, 
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

    def bind_shortcuts(self):
        self.bind("<F5>", lambda e: self.start_autotype())
        self.bind("<F6>", lambda e: self.stop_autotype())

    def on_speed_change(self, value):
        self.config.typing_speed = int(value)
        self.speed_label.configure(text=f"{self.config.typing_speed} KPM")
        self.on_config_change()

    def on_config_change(self):
        self.config.monitor_id = int(self.monitor_combo.get())
        self.config.switch_kb_layout = self.switch_kb_check.get() == 1
        self.config.fix_qwerty = self.fix_qwerty_check.get() == 1

    def select_region(self):
        self.config.monitor_id = int(self.monitor_combo.get())
        selector = RegionSelector(self.config.monitor_id)
        self.iconify()
        self.update()
        time.sleep(0.3)
        region = selector.select_region()
        self.deiconify()
        self.focus_force()
        
        if region:
            self.region = region
            self.region_label.configure(text=str(region), text_color="green")
            self.start_btn.configure(state="normal")
        else:
            self.region_label.configure(text="Cancelled", text_color="gray")

    def start_autotype(self):
        if not self.region:
            messagebox.showwarning("No Region", "Please select a region first.")
            return

        self.config.api_key = self.api_key_entry.get()
        if not self.config.api_key:
            messagebox.showerror("No API Key", "Please enter your Mistral API Key.")
            return

        self.save_config()

        self.running = True
        self.stop_event = threading.Event()
        self.stats = Stats()
        self.stats.start_time = time.time()

        self.state_label.configure(text="Running", text_color="green")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.select_btn.configure(state="disabled")

        self.engine = AutotyperEngine(self.config, self.region, self.stop_event, self.stats)
        self.thread = threading.Thread(target=self._run_engine, daemon=True)
        self.thread.start()
        
        self._update_stats_loop()

    def _run_engine(self):
        try:
            self.engine.run(on_text_extracted=self._on_text_extracted)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, self.stop_autotype)

    def _on_text_extracted(self, text: str):
        self.after(0, lambda t=text: self.update_last_text(t))

    def _update_stats_loop(self):
        if self.running:
            minutes, seconds = self.stats.get_elapsed()
            self.time_label.configure(text=f"{minutes}:{seconds:02d}")
            self.slides_label.configure(text=f"Slides: {self.stats.slides}")
            self.chars_label.configure(text=f"Characters: {self.stats.characters}")
            
            wpm = self.stats.get_wpm()
            if wpm > 0:
                self.wpm_label.configure(text=str(wpm), text_color="green")
            
            self.after(500, self._update_stats_loop)

    def stop_autotype(self):
        self.running = False
        if self.stop_event:
            self.stop_event.set()
        if self.engine:
            self.engine.stop()
        
        self.state_label.configure(text="Idle", text_color="gray")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.select_btn.configure(state="normal")
        self.wpm_label.configure(text="--", text_color="gray")

    def update_last_text(self, text):
        self.last_text_box.configure(state="normal")
        self.last_text_box.delete("1.0", "end")
        self.last_text_box.insert("1.0", text)
        self.last_text_box.configure(state="disabled")


def main():
    app = AutotypeGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
