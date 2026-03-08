from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np
import pyscreenshot as ImageGrab
import screeninfo


@dataclass
class Region:
    left: int
    top: int
    width: int
    height: int
    
    def __str__(self):
        return f"{self.width}x{self.height}"


class RegionSelector:
    def __init__(self, monitor_id: int):
        self.monitor_id = monitor_id
        self.start_point: Optional[tuple] = None
        self.end_point: Optional[tuple] = None
        self.selecting = False
        self.selection_done = False
        self.region: Optional[Region] = None

    def capture_screen(self) -> np.ndarray:
        monitors = screeninfo.get_monitors()
        if not monitors:
            raise RuntimeError("No monitors found")
        mon = monitors[self.monitor_id - 1]
        bbox = (mon.x, mon.y, mon.x + mon.width, mon.y + mon.height)
        img = ImageGrab.grab(bbox=bbox)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def _on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_point = (x, y)
            self.selecting = True
            self.selection_done = False
        elif event == cv2.EVENT_MOUSEMOVE and self.selecting:
            self.end_point = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.end_point = (x, y)
            self.selecting = False
            self.selection_done = True

    def select_region(self) -> Optional[Region]:
        img = self.capture_screen()
        clone = img.copy()

        window_name = "Select Region - Drag to select, ESC to cancel"
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, 100, 100)
        cv2.setMouseCallback(window_name, self._on_mouse)

        while True:
            display = clone.copy()
            if self.start_point and self.end_point:
                cv2.rectangle(display, self.start_point, self.end_point, (0, 255, 0), 2)
            cv2.imshow(window_name, display)
            key = cv2.waitKey(10) & 0xFF
            
            if self.selection_done and self.start_point and self.end_point:
                break
            if key == 27:
                cv2.destroyAllWindows()
                return None

        cv2.destroyAllWindows()
        return self._calculate_region()

    def _calculate_region(self) -> Optional[Region]:
        if not self.start_point or not self.end_point:
            return None

        x1, y1 = self.start_point
        x2, y2 = self.end_point
        
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        monitors = screeninfo.get_monitors()
        if not monitors:
            return None
        mon = monitors[self.monitor_id - 1]

        self.region = Region(
            left=left + mon.x,
            top=top + mon.y,
            width=right - left,
            height=bottom - top
        )
        return self.region
