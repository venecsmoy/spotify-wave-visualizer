import sounddevice as sd
import numpy as np
import tkinter as tk
import queue

class AudioVisualizer:
    def __init__(self):
        self.root = tk.Tk()

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        overlay_height = 150

        # Configure window - transparent overlay at top of screen
        self.root.overrideredirect(True)  # Remove window borders
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-transparentcolor', 'black')  # Make black transparent
        self.root.geometry(f'{screen_width}x{overlay_height}+0+0')

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=screen_width,
            height=overlay_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack()

        # Audio settings
        self.CHUNK = 2048
        self.RATE = 44100
        self.WAVE_POINTS = 200  # Reduced from 300 for better performance

        # Visualization settings
        self.width = screen_width
        self.height = overlay_height
        self.wave_data = [0] * self.WAVE_POINTS

        # Audio queue
        self.audio_queue = queue.Queue()

        # Find and print audio devices
        self.setup_audio()

        # Bind escape key to quit
        self.root.bind('<Escape>', lambda e: self.quit())

        # Start visualization
        self.update_wave()

    def audio_callback(self, indata, frames, time, status):
        """Called by sounddevice for each audio block"""
        if status:
            print(f"Audio status: {status}")
        # Put audio data in queue
        self.audio_queue.put(indata.copy())

    def setup_audio(self):
        """Setup audio stream to capture system audio (loopback)"""
        try:
            # List all devices
            print("Available audio devices:")
            devices = sd.query_devices()

            device_index = None
            for i, device in enumerate(devices):
                print(f"{i}: {device['name']} (in: {device['max_input_channels']}, out: {device['max_output_channels']})")

                # Look for VB-Audio Cable or Stereo Mix
                name_lower = device['name'].lower()

                # Priority 1: VB-Audio Virtual Cable (most reliable)
                if 'cable output' in name_lower or 'vb-audio' in name_lower:
                    if device['max_input_channels'] > 0:
                        device_index = i
                        print(f"\n[OK] Found VB-Audio Virtual Cable: {device['name']}")
                        break

                # Priority 2: Stereo Mix (less reliable)
                if ('stereo mix' in name_lower or 'wave out mix' in name_lower or
                    'loopback' in name_lower or 'what u hear' in name_lower):
                    if device['max_input_channels'] > 0:
                        device_index = i
                        print(f"\n[OK] Found Stereo Mix: {device['name']}")
                        # Don't break - keep looking for VB-Cable

            if device_index is None:
                print("\n[ERROR] No audio loopback device found!")
                print("Please install VB-Audio Virtual Cable (see SETUP-VIRTUAL-CABLE.md)")
                print("Or enable Stereo Mix in Windows Sound settings")
                print("\nUsing default input device (probably won't work)")
                device_index = None  # Use default

            # Start audio stream
            self.stream = sd.InputStream(
                device=device_index,
                channels=1,
                samplerate=self.RATE,
                blocksize=self.CHUNK,
                callback=self.audio_callback
            )
            self.stream.start()

        except Exception as e:
            print(f"Audio setup error: {e}")
            self.stream = None

    def get_audio_data(self):
        """Get audio data from queue"""
        try:
            # Get latest audio data (drain queue to get most recent)
            data = None
            while not self.audio_queue.empty():
                data = self.audio_queue.get()

            if data is not None:
                # Flatten if needed
                return data.flatten()

        except Exception as e:
            print(f"Audio read error: {e}")

        return np.zeros(self.CHUNK)

    def update_wave(self):
        """Update wave visualization"""
        # Get audio data
        audio_data = self.get_audio_data()

        # Calculate RMS (Root Mean Square) to detect actual silence
        rms = np.sqrt(np.mean(audio_data**2))

        # Silence threshold based on RMS
        SILENCE_RMS_THRESHOLD = 0.001  # Adjust if needed

        if rms < SILENCE_RMS_THRESHOLD:
            # True silence detected - fade to flat line
            smoothing = 0.85
            for i in range(len(self.wave_data)):
                self.wave_data[i] = self.wave_data[i] * smoothing
        else:
            # Music is playing - do FFT visualization
            fft_data = np.fft.fft(audio_data)
            fft_magnitude = np.abs(fft_data[:len(fft_data)//2])

            if len(fft_magnitude) > 0:
                # Split frequency spectrum into bands
                # We'll use more of the spectrum to get vocals/high frequencies
                total_freqs = len(fft_magnitude)

                # Use first 40% of FFT (covers 0 Hz to ~8.8 kHz at 44.1kHz sample rate)
                # This captures bass, drums, vocals, and most musical content
                useful_freqs = int(total_freqs * 0.4)
                fft_useful = fft_magnitude[:useful_freqs]

                # Normalize
                max_val = np.max(fft_useful)
                if max_val > 0:
                    normalized = fft_useful / max_val
                else:
                    normalized = fft_useful

                # Map frequencies to wave points using vectorized operations
                indices = np.linspace(0, len(normalized) - 1, self.WAVE_POINTS, dtype=int)
                resampled = normalized[indices]

                # Apply frequency-specific boosts using NumPy (much faster than loops)
                bass_cutoff = int(self.WAVE_POINTS * 0.3)
                mid_cutoff = int(self.WAVE_POINTS * 0.7)

                resampled[:bass_cutoff] *= 1.3  # Bass boost
                resampled[bass_cutoff:mid_cutoff] *= 1.5  # Mid boost (vocals/instruments)
                resampled[mid_cutoff:] *= 1.8  # High boost (hi-hats/cymbals)

                # Smooth using vectorized NumPy operation (much faster than loop)
                smoothing = 0.7
                self.wave_data = [
                    self.wave_data[i] * smoothing + resampled[i] * (1 - smoothing)
                    if i < len(self.wave_data) else resampled[i]
                    for i in range(len(resampled))
                ]

        # Draw wave
        self.draw_wave()

        # Schedule next update
        self.root.after(16, self.update_wave)  # ~60 FPS

    def draw_wave(self):
        """Draw oscillating wave from top"""
        self.canvas.delete('all')

        if not self.wave_data:
            return

        # Vectorized point creation (faster than loop)
        x_step = self.width / self.WAVE_POINTS
        wave_array = np.array(self.wave_data)

        # Create x and y coordinates
        x_coords = np.arange(len(wave_array)) * x_step
        y_coords = wave_array * (self.height * 0.8)

        # Interleave x and y for create_line (much faster than extending in loop)
        smooth_points = np.empty(len(x_coords) * 2, dtype=np.float64)
        smooth_points[0::2] = x_coords
        smooth_points[1::2] = y_coords

        # Draw the wave line with reduced splinesteps for performance
        if len(smooth_points) > 2:
            self.canvas.create_line(
                *smooth_points,
                fill='white',
                width=3,
                smooth=True,
                splinesteps=6  # Reduced from 12 for better performance
            )

    def quit(self):
        """Clean shutdown"""
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
        self.root.destroy()

    def run(self):
        """Start the visualizer"""
        self.root.mainloop()

if __name__ == '__main__':
    print("Audio Visualizer Starting...")
    print("Press ESC to quit")
    print("")

    visualizer = AudioVisualizer()
    visualizer.run()
