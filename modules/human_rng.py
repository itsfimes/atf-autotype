# Random human silliness like speed, jitter etc. gets calculated here
import random


def typing_jitter(delay: float, char_index: int) -> float:
    base_num = random.uniform(-(delay * 0.5), delay * 0.2)

    if char_index > 250:
        char_index -= random.randint(-30, char_index)

    base_num += (char_index / 100) ** 1 / random.randint(2, 50)

    return base_num if base_num > 0 else base_num * -1