import time
import threading
from dataclasses import dataclass, field
from typing import Optional, Callable
import random

import cv2
import numpy as np
import pyscreenshot as ImageGrab
import screeninfo

from modules.typer import (
    activate_input_kde, 
    type_text, 
    next_slide as typer_next_slide, 
    switch_keyboard_layouts,
    set_stop_event as set_typer_stop_event
)
from modules.corrector import correct_text
from modules.human_rng import generate_base_offset
from modules.paid_ocr import OCR

from modules.gui.config import AppConfig, AppConstants


@dataclass
class Stats:
    slides: int = 0
    errors: int = 0
    characters: int = 0
    start_time: Optional[float] = None
    
    def get_wpm(self) -> int:
        if self.slides == 0 or self.start_time is None:
            return 0
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        return int((self.characters / AppConstants.WPM_DIVISOR) / (elapsed / 60))
    
    def get_elapsed(self) -> tuple[int, int]:
        if self.start_time is None:
            return 0, 0
        elapsed = int(time.time() - self.start_time)
        return elapsed // 60, elapsed % 60
    
    def reset(self):
        self.slides = 0
        self.errors = 0
        self.characters = 0
        self.start_time = None


class AutotyperEngine:
    def __init__(self, config: AppConfig, region, stop_event: threading.Event, stats: Stats):
        self.config = config
        self.region = region
        self.stop_event = stop_event
        self.stats = stats
        self._running = False
        
    def run(self, on_text_extracted: Optional[Callable] = None):
        self._running = True
        set_typer_stop_event(self.stop_event)
        
        try:
            ocr = OCR(self.config.api_key)
            monitors = screeninfo.get_monitors()
            if not monitors:
                raise RuntimeError("No monitors found")
            mon = monitors[self.config.monitor_id - 1]
            
            activate_input_kde()
            time.sleep(AppConstants.START_DELAY)
            
            if self.config.switch_kb_layout:
                switch_keyboard_layouts()
            time.sleep(1)
            
            ac_source = []
            typing_speed_sec = self.config.typing_speed / 60
            
            while self._running and not self.stop_event.is_set():
                text = self._process_slide(ocr, ac_source, typing_speed_sec, mon)
                
                if on_text_extracted:
                    on_text_extracted(text or "")
                
                if not self._running or self.stop_event.is_set():
                    break
                    
                time.sleep(AppConstants.SLIDE_DELAY)
                
        except Exception:
            raise
        finally:
            self._running = False
    
    def _process_slide(self, ocr, ac_source, typing_speed_sec, mon) -> str:
        bbox = (
            self.region.left,
            self.region.top,
            self.region.left + self.region.width,
            self.region.top + self.region.height
        )
        img = ImageGrab.grab(bbox=bbox)
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        extracted_text = correct_text(ocr.readtext(img_np), ac_source)
        self.stats.characters += len(extracted_text.strip())
        
        type_text(
            extracted_text.strip(),
            int(typing_speed_sec + generate_base_offset(extracted_text)),
            False,
            self.config.fix_qwerty
        )
        
        self._next_slide(mon)
        
        return extracted_text
    
    def _next_slide(self, mon):
        time.sleep(AppConstants.PRE_SLIDE_DELAY)
        
        from modules.screenshots import take_and_save_screenshot
        take_and_save_screenshot(
            self.region.top - mon.y,
            self.region.left - mon.x + random.randint(-3, 5),
            self.region.width - random.randint(-40, 30),
            self.region.height - 100 - random.randint(-50, 30),
            self.config.monitor_id
        )
        
        time.sleep(AppConstants.POST_SLIDE_DELAY)
        from modules.typer import _next_slide
        _next_slide()
        time.sleep(AppConstants.POST_SLIDE_DELAY)
        switch_keyboard_layouts()
        
        self.stats.slides += 1
    
    def stop(self):
        self._running = False
