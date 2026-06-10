import sounddevice as sd
import numpy as np
import tkinter as tk
import queue

class AudioVisualizer:
    def __init__(self):
        self.root = tk.Tk()

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        overlay_height = 250  # Increased height for more space
        y_offset = 5  # Move down 5 pixels from top

        # Configure window - transparent overlay at top of screen
        self.root.overrideredirect(True)  # Remove window borders
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.5)  # 50% transparency
        self.root.attributes('-transparentcolor', 'black')  # Make black transparent
        self.root.geometry(f'{screen_width}x{overlay_height}+0+{y_offset}')

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
        self.wave_velocity = np.zeros(self.WAVE_POINTS)  # For spring-damper motion

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

        # Compute the target wave shape — zeros when silent, FFT-derived otherwise.
        # Physics + spatial coupling run uniformly on the target each frame, so the
        # silent path becomes a natural spring decay to zero.
        target = np.zeros(self.WAVE_POINTS)

        if rms >= SILENCE_RMS_THRESHOLD:
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

                # Custom frequency band distribution:
                # Left 40%: 20-300 Hz (bass)
                # Middle 40%: 300-2000 Hz (vocals/instruments)
                # Right 20%: 2000-8000 Hz (highs)

                # Calculate frequency per bin
                freq_per_bin = (self.RATE / 2) / len(fft_magnitude)  # Hz per FFT bin

                # Find bin indices for each frequency range
                bin_20hz = max(1, int(20 / freq_per_bin))
                bin_300hz = int(300 / freq_per_bin)
                bin_2000hz = int(2000 / freq_per_bin)
                bin_8000hz = min(len(normalized), int(8000 / freq_per_bin))

                # Calculate how many wave points per section
                left_points = int(self.WAVE_POINTS * 0.4)  # 40% for bass
                mid_points = int(self.WAVE_POINTS * 0.4)   # 40% for mids
                right_points = self.WAVE_POINTS - left_points - mid_points  # Remaining 20% for highs

                # Sample from each frequency band
                bass_band = normalized[bin_20hz:bin_300hz]
                mid_band = normalized[bin_300hz:bin_2000hz]
                high_band = normalized[bin_2000hz:bin_8000hz]

                # Apply averaging to bass band to make it smoother and more wave-like
                if len(bass_band) > 10:
                    # Use moving average with larger window size to smooth bass frequencies
                    window_size = 10  # Increased from 5 for smoother wave
                    bass_band_smoothed = np.convolve(bass_band, np.ones(window_size)/window_size, mode='same')
                else:
                    bass_band_smoothed = bass_band

                # Create indices for each band
                bass_indices = np.linspace(0, len(bass_band_smoothed) - 1, left_points, dtype=int) if len(bass_band_smoothed) > 0 else []
                mid_indices = np.linspace(0, len(mid_band) - 1, mid_points, dtype=int) if len(mid_band) > 0 else []
                high_indices = np.linspace(0, len(high_band) - 1, right_points, dtype=int) if len(high_band) > 0 else []

                # Sample and concatenate
                resampled = np.concatenate([
                    bass_band_smoothed[bass_indices] if len(bass_indices) > 0 else np.zeros(left_points),
                    mid_band[mid_indices] if len(mid_indices) > 0 else np.zeros(mid_points),
                    high_band[high_indices] if len(high_indices) > 0 else np.zeros(right_points)
                ])

                # Apply frequency-specific boosts using NumPy (much faster than loops)
                bass_cutoff = int(self.WAVE_POINTS * 0.4)
                mid_cutoff = int(self.WAVE_POINTS * 0.8)

                resampled[:bass_cutoff] *= 2.3  # Bass boost (left 40%)
                resampled[bass_cutoff:mid_cutoff] *= 2.15  # Mid boost (middle 40%)
                resampled[mid_cutoff:] *= 2.5  # High boost (right 20%)

                target = resampled

        # Spring-damper physics: each point chases its target with momentum,
        # producing sway on transients and graceful settle on sustained notes.
        # Per-band tuning keeps bass slow/heavy and highs snappy.
        bass_cutoff = int(self.WAVE_POINTS * 0.4)
        mid_cutoff = int(self.WAVE_POINTS * 0.8)

        spring_k = np.empty(self.WAVE_POINTS)
        damping = np.empty(self.WAVE_POINTS)
        spring_k[:bass_cutoff], damping[:bass_cutoff] = 0.10, 0.78   # Bass: slow chase, smooth sway
        spring_k[bass_cutoff:mid_cutoff], damping[bass_cutoff:mid_cutoff] = 0.16, 0.68  # Mids: balanced
        spring_k[mid_cutoff:], damping[mid_cutoff:] = 0.22, 0.62     # Highs: fast chase, light damp

        positions = np.array(self.wave_data)
        self.wave_velocity = self.wave_velocity * damping + (target - positions) * spring_k
        positions = positions + self.wave_velocity

        # Spatial coupling: adjacent points pull each other so the wave
        # moves as a connected sheet rather than independent bars.
        positions = np.convolve(positions, [0.25, 0.5, 0.25], mode='same')

        self.wave_data = positions.tolist()

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
        left_margin = 10  # Clip left side by 10 pixels
        available_width = self.width - left_margin
        x_step = available_width / self.WAVE_POINTS
        wave_array = np.array(self.wave_data)

        # Create x and y coordinates with left margin
        x_coords = (np.arange(len(wave_array)) * x_step) + left_margin
        # Keep wave size same as 200px height: 200 * 0.8 = 160
        y_coords = wave_array * 160

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
