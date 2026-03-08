import pyscreenshot as ImageGrab
import screeninfo
import os

def take_and_save_screenshot(top: int, left: int, width: int, height: int, monitor_num: int = 1) -> None:
    os.makedirs("screenshots", exist_ok=True)

    # Get monitor offset (screeninfo uses 0-based index)
    monitors = screeninfo.get_monitors()
    if monitor_num < 1 or monitor_num > len(monitors):
        raise ValueError(f"Invalid monitor_num {monitor_num}. Available monitors: 1–{len(monitors)}")

    mon = monitors[monitor_num - 1]  # Convert 1-based to 0-based index

    # Apply monitor offset to coordinates (like mss did with mon["top"] / mon["left"])
    abs_left = mon.x + left
    abs_top = mon.y + top

    bbox = (abs_left, abs_top, abs_left + width, abs_top + height)

    output = f"screenshots/Screenshot-ATF-{width}x{height}.png"
    while os.path.exists(output):
        output = f"{output}_"

    img = ImageGrab.grab(bbox=bbox)
    img.save(output)
    print(output)
