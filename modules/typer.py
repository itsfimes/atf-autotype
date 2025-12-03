import time
import random
from pynput.keyboard import Controller, Key
from modules.screenshots import take_and_save_screenshot
from modules.human_rng import typing_jitter


keyboard = Controller()

def type_text(text, cps=10, make_one_error=False):
    delay = 1.0 / cps
    mistake_index = None

    if make_one_error and len(text) > 2:
        mistake_index = random.randint(1, len(text) - 2)

    for i, ch in enumerate(text):
        # introduce the one mistake if this is the chosen spot
        if make_one_error and i == mistake_index:
            wrong = random.choice("abcdefghijklmnopqrstuvwxyz")
            if wrong == ch:
                wrong = chr((ord(ch) + 3) % 122)  # guaranteed different
            keyboard.type(wrong)
            time.sleep(delay)

            # backspace to fix
            time.sleep(typing_jitter(delay, i))
            keyboard.press(Key.backspace)
            keyboard.release(Key.backspace)
            time.sleep(delay + random.random())

        # type correct character
        keyboard.press(ch)
        time.sleep(random.uniform(0.002, 0.007))
        keyboard.release(ch)
        time.sleep(delay + typing_jitter(delay, i))  # tiny human jitter

def _next_slide() -> None:
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    keyboard.press(Key.ctrl)
    keyboard.press("d")
    keyboard.release("d")
    keyboard.release(Key.ctrl)

def next_slide(top: int, left:int, width:int, height:int, monitor_num:int = 1) -> None:
    time.sleep(0.1)
    take_and_save_screenshot(top, left, width, height, monitor_num)
    time.sleep(0.1)
    _next_slide()
    time.sleep(0.1)

    keyboard.press(Key.cmd)
    keyboard.tap(Key.space)
    keyboard.release(Key.cmd)