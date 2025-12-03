# An autotyper for ATF
This exists because atf is ass and monkeytype is literally free.

### Installation

- **Pre-installation**:
    - Clone this repository (`git clone https://github.com/itsfimes/atf-autotype.git`)
    - cd into it (`cd atf-autotype`)
- **Installation and config**
    - Make sure you have [Python](https://www.python.org/downloads/) installed. (The recommended version is `3.13.7`)
    - Install the requirements
        - (`pip install -r requirements.txt`)
    - Open `autotype.py` and edit it so `monitor_id` and `typing_speed` are correct.
        - > `monitor_id` is 1 if you're using the **primary** screen, 2 if you're using the secondary screen and so on.
        - > `typing_speed` doesn't directly correspond to the raw keystrokes per second that atf uses. It's used to calculate the delay between keystrokes using `1 / typing_speed`

