# ATF Autotyper

> ⚠️ **Disclaimer**: This is a "vibecoded" project — written quickly to get something working. It doesn't represent my usual standards for code quality, maintainability, or best practices. Expect messiness, hacks, and things that could be done much better.

An automated typing tool that captures text from your screen using OCR and types it for you. Useful for automating typing tests on [atf](https://atf.lol).

## Features

- OCR-powered text recognition using Mistral AI
- Automatic typing with human-like timing variations
- GUI and CLI modes
- Configurable typing speed
- Keyboard layout fixing (QWERTY/Y/Z swap)
- Region selection for targeted OCR

## Prerequisites

- Python 3.13+ (recommended)
- Mistral API key

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/itsfimes/atf-autotype.git
   cd atf-autotype
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env` with your settings**

   Required:
   - `MISTRAL_API_KEY` — Your Mistral API key (get one at [mistral.ai](https://mistral.ai))

   Optional:
   - `MONITOR_ID` — Monitor number (1 = primary, 2 = secondary, etc.) [default: 1]
   - `TYPING_SPEED` — Keystrokes per minute [default: 260]
   - `SWITCH_KB_LAYOUT_ON_START` — Switch keyboard layout on start (`true`/`false`) [default: false]
   - `FIX_QWERTY` — Fix QWERTY Z/Y key swap (`true`/`false`) [default: true]
   - `SCREEN_W` / `SCREEN_H` — Screen dimensions (auto-detected if not set)

   > **Note**: `TYPING_SPEED` doesn't directly correspond to ATF's raw keystrokes/second. It's used to calculate delay: `delay = 1 / (typing_speed / 60)`

## Usage

### GUI Mode (Recommended)
```bash
python gui.py
```
or
```bash
python main.py
```

The GUI lets you configure settings visually and select the screen region to capture.

### CLI Mode
```bash
python autotype.py
```

1. A window will appear — draw a rectangle around the text area you want to capture
2. Press **ESC** to cancel
3. The autotyper will start capturing text and typing automatically

## Troubleshooting

- **OCR not recognizing text**: Ensure good contrast on screen, adjust the selection region
- **Typing too fast/slow**: Adjust `TYPING_SPEED` in `.env`
- **Wrong characters typed**: Enable `FIX_QWERTY` if you have a non-US keyboard
- **Wrong monitor**: Set `MONITOR_ID` to match your display

## License

MIT
