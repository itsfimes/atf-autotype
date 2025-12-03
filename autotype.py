import random
import cv2
import numpy as np
import mss
import easyocr
import pytesseract
from modules.typer import type_text, next_slide
from modules.corrector import correct_text
import time
import os


ocr = easyocr.Reader(["cs", "en"])
os.makedirs("screenshots", exist_ok=True)


monitor_id = 1

char_blocklist = ["1","2","3","4","5","6","7","8","9", "_", "-",
                  "=", "|", "/", r"\\", "[", "]", "{", "}", "(", ")",
                  "<", ">", ":"] # not including 0, cuz that can be mistaken for an "o"

start_point = None
end_point = None
selecting = False
selection_done = False


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
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_id]
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

def extract_text(region, ocr, **kwargs) -> str:
    text = ocr.readtext(preprocess(region), **kwargs)
    return " ".join([item[1] for item in text])

def preprocess(region):
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return gray

if __name__ == "__main__":
    img = capture_screen(monitor_id)
    clone = img.copy()

    cv2.namedWindow("Select Area")
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

    x1, y1 = start_point
    x2, y2 = end_point

    # normalize coords
    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)
    width = right - left
    height = bottom - top

    region = img[top:bottom, left:right]

    time.sleep(5)
    while True:
        img = capture_screen(monitor_id)
        region = img[top:bottom, left:right]
        extracted_text = correct_text(extract_text(region, ocr, blocklist=char_blocklist))
        print(extracted_text)

        type_text(extracted_text.strip(), 180 + random.randint(-2, 1), random.getrandbits(1) if len(extracted_text) > 150 else 0)
        next_slide(top, left - random.randint(-3, 5), width - random.randint(-40, 30), height - 100 - random.randint(-50, 30), monitor_id)
        time.sleep(0.2)