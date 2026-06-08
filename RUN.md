# Audio Visualizer for Spotify

## Quick Start
```bash
cd ~/spotify-wave-visualizer && python visualizer.py
```

## What This Does
- Creates a transparent overlay at the TOP of your screen
- Full width, 150px height
- White oscillating wave visualization
- Reacts to system audio (Spotify)
- Press ESC to close

## First Time Setup
```bash
pip install -r requirements.txt
```

## Prerequisites
- Enable **Stereo Mix** in Windows Sound settings (same as before)
- Python with pip installed

## How It Works
- Uses PyAudio to capture system audio
- Performs FFT (Fast Fourier Transform) for frequency analysis
- Draws smooth wave coming down from top
- 60 FPS animation
- Fully transparent background (black = transparent)

## Controls
- **ESC key**: Close the visualizer
- Overlay is always on top
- No window borders

## Expected Behavior
1. Window appears at top of screen, full width
2. White wave oscillates based on audio
3. Transparent background
4. Automatically finds and uses Stereo Mix if enabled
