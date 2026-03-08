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
    - Copy `.env.example` to `.env` and configure your settings:
        - Add your Mistral API key to `MISTRAL_API_KEY`
        - Configure `MONITOR_ID` (1 for primary screen, 2 for secondary, etc.)
        - Set `TYPING_SPEED` (keystrokes per minute)
        - Adjust other settings as needed
    - > `typing_speed` doesn't directly correspond to the raw keystrokes per second that atf uses. It's used to calculate the delay between keystrokes using `1 / typing_speed`

### Usage
Run the autotyper with: `python autotype.py`

### Configuration Options
- `MISTRAL_API_KEY`: Your Mistral API key for OCR
- `MONITOR_ID`: Monitor number (1 = primary, 2 = secondary, etc.)
- `TYPING_SPEED`: Typing speed in keystrokes per minute
- `SWITCH_KB_LAYOUT_ON_START`: Switch keyboard layout on start (true/false)
- `FIX_QWERTY`: Fix QWERTY/Z/Y key swap issues (true/false)
- `SCREEN_W`/`SCREEN_H`: Screen dimensions (optional, auto-detected if not set)
