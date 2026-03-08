import random
import string
import cv2
import numpy as np
import pyscreenshot as ImageGrab
import screeninfo
from PIL import Image
from modules.typer import activate_input_kde, type_text, next_slide, switch_keyboard_layouts
from modules.corrector import correct_text
from modules.human_rng import generate_base_offset
from modules.paid_ocr import OCR
import time
import os
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

os.makedirs("screenshots", exist_ok=True)

# ----- CONFIG -----

# Load configuration from environment variables
monitor_id = int(os.getenv("MONITOR_ID", 1))

typing_speed: float = float(os.getenv("TYPING_SPEED", 260))  # keystrokes per minute (approx)
typing_speed = typing_speed / 60  # convert to keystrokes per second

switch_kb_layout_on_start: bool = os.getenv("SWITCH_KB_LAYOUT_ON_START", "false").lower() == "true"
fix_qwerty: bool = os.getenv("FIX_QWERTY", "true").lower() == "true"

screen_w = int(os.getenv("SCREEN_W", 1920))
screen_h = int(os.getenv("SCREEN_H", 1080))

# ----- CONFIG -----

start_point = None
end_point = None
selecting = False
selection_done = False

# Initialize OCR with API key from environment
mistral_api_key = os.getenv("MISTRAL_API_KEY")
if not mistral_api_key:
    raise ValueError("Mistral API key not found in .env file. Please add MISTRAL_API_KEY to your .env file.")
ocr = OCR(mistral_api_key)

ac_source = []
def on_mouse(event, x, y, flags, param):
    global start_point, end_point, selecting, selection_done

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        selecting = True
        selection_done = False

    elif event == cv2.EVENT_MOUSEMOVE and selecting:
        end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        selecting = False
        selection_done = True

def capture_screen(monitor_id: int) -> np.ndarray:
    monitors = screeninfo.get_monitors()
    if monitor_id < 1 or monitor_id > len(monitors):
        raise ValueError(f"Invalid monitor_id {monitor_id}. Available monitors: 1–{len(monitors)}")

    mon = monitors[monitor_id - 1]  # Convert 1-based to 0-based index
    bbox = (mon.x, mon.y, mon.x + mon.width, mon.y + mon.height)

    img = ImageGrab.grab(bbox=bbox)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def extract_text(region, ocr, **kwargs) -> str:
    text = ocr.readtext(region, **kwargs)
    return text

def preprocess(region):
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return gray

if __name__ == "__main__":
    img = capture_screen(monitor_id)
    clone = img.copy()
    
    activate_input_kde()
    time.sleep(2)

    cv2.namedWindow("Select Area")
    cv2.moveWindow("Select Area", screen_w // 2, screen_h // 2)
    cv2.setMouseCallback("Select Area", on_mouse)

    while True:
        display = clone.copy()

        if start_point and end_point:
            cv2.rectangle(display, start_point, end_point, (0, 255, 0), 2)

        cv2.imshow("Select Area", display)
        key = cv2.waitKey(1)

        if selection_done:
            break

        if key == 27:  # ESC to cancel
            cv2.destroyAllWindows()
            exit()

    cv2.destroyAllWindows()

    x1, y1 = start_point if start_point else (0, 0)
    x2, y2 = end_point if end_point else (0, 0)

    # normalize coords
    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)
    width = right - left
    height = bottom - top
    #time.sleep(5)

    if switch_kb_layout_on_start:
        switch_keyboard_layouts()
    time.sleep(1)
    while True:
        img = capture_screen(monitor_id)
        #Image.fromarray(img).show()
        #input()
        #region = img[top:bottom, left:right]
        extracted_text = correct_text(extract_text(img[top:bottom, left:right], ocr), ac_source)
        print(extracted_text)

        make_mistake = False
        type_text(extracted_text.strip(), int(typing_speed + generate_base_offset(extracted_text)), make_mistake, fix_qwerty)
        next_slide(top, left - random.randint(-3, 5), width - random.randint(-40, 30), height - 100 - random.randint(-50, 30), monitor_id)
        time.sleep(0.2)
