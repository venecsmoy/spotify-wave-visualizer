# Spotify Wave Visualizer

A real-time audio visualizer that creates a transparent overlay at the top of your screen, displaying smooth waveform visualizations synchronized with Spotify (or any audio) playback.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Transparent Overlay**: Full-width window at top of screen with transparent background
- **Real-Time FFT Analysis**: Fast Fourier Transform visualization of audio frequencies
- **Frequency-Mapped Waves**: Bass on left, vocals/mids in center, highs on right
- **Smart Silence Detection**: RMS-based detection that fades to flat when music is paused
- **Smooth 60 FPS Animation**: Bezier curve smoothing for fluid motion
- **VB-CABLE Integration**: Captures system-wide audio via virtual audio cable
- **Always-on-Top**: Stays visible over all applications including fullscreen

## Installation

### Prerequisites

1. **Python 3.8+** with pip
2. **VB-Audio Virtual Cable** - [Download here](https://vb-audio.com/Cable/)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Setup

### 1. Install VB-Audio Virtual Cable

1. Download from https://vb-audio.com/Cable/
2. Extract and run `VBCABLE_Setup_x64.exe` as Administrator
3. Click "Install Driver"
4. **Restart your computer** (required!)

### 2. Configure Windows Audio

1. Right-click speaker icon → "Open Sound settings"
2. Click "Sound Control Panel"

**Playback Tab:**
1. Right-click **"CABLE Input"** → **"Set as Default Device"**
2. Click "Apply"

**Recording Tab:**
1. Right-click **"CABLE Output"** → **"Properties"**
2. Go to **"Listen"** tab
3. Check **"Listen to this device"**
4. Select your real headphones/speakers from dropdown
5. Click "Apply" → "OK"

Now Spotify audio will:
- Play through the virtual cable (captured by visualizer)
- Route back to your headphones (so you can hear it)

## Usage

```bash
python visualizer.py
```

**Controls:**
- **ESC** - Close visualizer

## How It Works

### Audio Pipeline

```
Spotify → CABLE Input (virtual speaker)
    ↓
CABLE Output (virtual microphone) → Visualizer (FFT)
    ↓
Listen Mode → Your Headphones
```

### Technical Details

- **Sample Rate**: 44.1 kHz
- **Chunk Size**: 2048 samples
- **Wave Points**: 200 frequency bands
- **Overlay Height**: 250 px (full screen width)
- **Update Rate**: ~60 FPS (16ms intervals)
- **Frequency Range**: 0 Hz - 8.8 kHz (40% of FFT spectrum)
- **Silence Threshold**: RMS < 0.001 (with 0.85 decay-to-flat per frame)

### Frequency Distribution

- **Left 40%**: Bass & kick drums (20-300 Hz) - 2.3x boost
- **Middle 40%**: Vocals & instruments (300-2000 Hz) - 2.15x boost
- **Right 20%**: Hi-hats, cymbals (2-8 kHz) - 2.5x boost

### Adaptive Smoothing

Each band uses a different smoothing coefficient (prior-frame retention) so bass stays stable while highs respond quickly:

- **Bass**: 0.90 — heavy smoothing to suppress low-frequency jitter while letting beats pop
- **Mids**: 0.80 — moderate smoothing for vocals/instruments
- **Highs**: 0.75 — light smoothing for snappy hi-hat / cymbal response

## Troubleshooting

**No audio in headphones:**
- Make sure "Listen to this device" is enabled on CABLE Output
- Check that the dropdown is set to your real headphones

**Visualizer not reacting:**
- Verify CABLE Output is enabled in Recording devices
- Make sure Spotify is set to play through CABLE Input
- Check that music is actually playing

**Want to go back to normal audio:**
- Sound settings → Playback → Set your headphones as default again

## Project Structure

```
spotify-wave-visualizer/
├── visualizer.py           # Main visualizer application
├── requirements.txt        # Python dependencies
├── RUN.md                 # Quick start guide
├── SETUP-VIRTUAL-CABLE.md # Detailed VB-CABLE setup
└── README.md              # This file
```

## Technical Stack

- **Python 3.8+**
- **Tkinter** - Transparent overlay window
- **SoundDevice** - Audio capture
- **NumPy** - FFT and array operations

## License

MIT License - See [LICENSE](LICENSE) file for details

## Author

**Venec Moy** - [Portfolio](https://venecsmoy.github.io/portfolio/) | [GitHub](https://github.com/venecsmoy)

## Acknowledgments

- VB-Audio for the Virtual Cable driver
- NumPy/SciPy for FFT implementation
- Spotify for inspiring the project
