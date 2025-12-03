import mss
import mss.tools
import os

def take_and_save_screenshot(top: int, left:int, width:int, height:int, monitor_num:int = 1) -> None:
    with mss.mss() as sct:
        mon = sct.monitors[monitor_num]

        # The screen part to capture
        monitor = {
            "top": mon["top"] + top,  # 100px from the top
            "left": mon["left"] + left,  # 100px from the left
            "width": width,
            "height": height,
            "mon": monitor_num,
        }
        output = "screenshots/Screenshot-ATF-{width}x{height}.png".format(**monitor)

        while os.path.exists(output):
            output = f"{output}_"

        # Grab the data
        sct_img = sct.grab(monitor)

        # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        print(output)