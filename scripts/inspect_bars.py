import miniaudio
import numpy as np
import scipy.signal

# Read first 150 seconds (stereo 44.1kHz -> mono 22050)
target_samples = 150 * 88200
samples = []
for chunk in miniaudio.mp3_stream_file('audio_samples/100 Ways To Love A Cat Ways 1-100.mp3'):
    samples.extend(chunk)
    if len(samples) >= target_samples:
        break

audio = np.array(samples[:target_samples], dtype=np.float32)
mono = (audio[0::4] + audio[1::4]) * 0.5 # 22050 Hz
sr = 22050

# Let's save mono as a 16-bit WAV file so we can analyze it cleanly or inspect
# But also let's look at the energy envelope in bars (1.92s = 42336 samples)
bar_len = int(1.92 * sr)
n_bars = len(mono) // bar_len
bar_energies = []
for b in range(n_bars):
    segment = mono[b*bar_len : (b+1)*bar_len]
    rms = np.sqrt(np.mean(segment**2))
    bar_energies.append(rms)

print(f"Total bars in 150s: {n_bars}")
for b in range(n_bars):
    t_start = b * 1.92
    print(f"Bar {b:2d} (t={t_start:5.2f}s): RMS = {bar_energies[b]:6.1f}")
