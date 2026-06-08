# Setup VB-Audio Virtual Cable (The Solution That Actually Works)

## Step 1: Download VB-Audio Virtual Cable

1. Go to: https://vb-audio.com/Cable/
2. Click **"Download"** under "VB-CABLE Virtual Audio Device"
3. Extract the ZIP file
4. Right-click `VBCABLE_Setup_x64.exe` → **"Run as Administrator"**
5. Click **"Install Driver"**
6. Restart your computer (required!)

## Step 2: Configure Windows Audio

After restart:

1. Right-click speaker icon → **"Open Sound settings"**
2. Scroll down → **"Sound Control Panel"**

### Set up Playback (Output):
1. Go to **"Playback"** tab
2. You should see **"CABLE Input"** (this is the virtual cable's output)
3. Right-click **"CABLE Input"** → **"Set as Default Device"**
4. Click **"Apply"**

⚠️ **IMPORTANT:** You won't hear audio through your headphones anymore! We'll fix this in Step 3.

### Set up Recording (Input):
1. Go to **"Recording"** tab
2. You should see **"CABLE Output"** (this is the virtual cable's input)
3. It should already be listed and active
4. Click **"OK"**

## Step 3: Hear Audio Through Your Headphones Again

Since Spotify is now playing to the virtual cable, you need to route it back to your headphones:

### Option A: Use "Listen to this device" (Simple but slight delay)
1. Right-click speaker icon → **"Sound Control Panel"**
2. **"Recording"** tab
3. Right-click **"CABLE Output"** → **"Properties"**
4. Go to **"Listen"** tab
5. Check **"Listen to this device"**
6. In the dropdown, select your actual headphones/speakers
7. Click **"Apply"** → **"OK"**

### Option B: Use VB-Audio Voicemeeter (Better, no delay)
1. Download Voicemeeter from: https://vb-audio.com/Voicemeeter/
2. Install it
3. Route CABLE to your headphones through Voicemeeter
(More complex but better quality)

## Step 4: Test It

1. Play Spotify
2. You should hear audio through your headphones (via Listen or Voicemeeter)
3. The visualizer will capture from "CABLE Output"

## How It Works

```
Spotify → CABLE Input (virtual speaker) → CABLE Output (virtual mic) → Visualizer
                                        ↓
                                  Your Headphones (via Listen)
```

## Troubleshooting

**No audio in headphones:**
- Make sure "Listen to this device" is enabled on CABLE Output
- Make sure the dropdown is set to your real headphones

**Visualizer not reacting:**
- Check that CABLE Output is enabled in Recording devices
- Make sure Spotify is playing and set to CABLE Input

**Want to go back to normal:**
- Sound settings → Playback → Set your headphones as default again
