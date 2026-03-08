import time
import random
from pynput.keyboard import Controller, Key
from modules.screenshots import take_and_save_screenshot
from modules.human_rng import typing_jitter

keyboard = Controller()

_stop_event = None

def set_stop_event(event):
    global _stop_event
    _stop_event = event

def type_text(text, cps=10, make_one_error=False, fix_qwerty: bool = False):
    if _stop_event is not None and _stop_event.is_set():
        return
        
    delay = 1.0 / cps
    if fix_qwerty:
        text = _fix_qwerty(text)
    mistake_index = None

    if make_one_error and len(text) > 2:
        mistake_index = random.randint(1, len(text) - 2)

    for i, ch in enumerate(text):
        if _stop_event is not None and _stop_event.is_set():
            return
            
        if make_one_error and i == mistake_index:
            print("Making mistake")
            wrong = random.choice("abcdefghijklmnopqrstuvwxyz")
            if wrong == ch:
                wrong = chr((ord(ch) + 3) % 122)
            keyboard.type(wrong)
            time.sleep(delay)

            time.sleep(typing_jitter(delay, i))
            keyboard.press(Key.backspace)
            keyboard.release(Key.backspace)
            time.sleep(delay + random.random())

        print(ch)
        _type_char(ch, delay, i)

def _type_char(ch: str, delay, idx) -> None:
    if ch.isupper():
        keyboard.press(Key.shift)
    keyboard.type(ch)
    if ch.isupper():
        keyboard.release(Key.shift)
    time.sleep(random.uniform(0.002, 0.007))
    # keyboard.release(ch)
    time.sleep(delay + typing_jitter(delay, idx))  # tiny jitter so it seems legit


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

    switch_keyboard_layouts()

def switch_keyboard_layouts() -> None:
    keyboard.press(Key.cmd)
    keyboard.tap(Key.space)
    keyboard.release(Key.cmd)

def _fix_qwerty(text: str) -> str:
    text_fixed = []
    for char in text:
        if char == "z":
            text_fixed.append("y")
        elif char == "y":
            text_fixed.append("z")
        elif char == "Z":
            text_fixed.append("Y")
        elif char == "Y":
            text_fixed.append("Z")
        else:
            text_fixed.append(char)
    return "".join(text_fixed)

def activate_input_kde() -> None:
    keyboard.tap(Key.ctrl)
