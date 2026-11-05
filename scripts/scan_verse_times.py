import miniaudio
import speech_recognition as sr_lib
import io
import wave
import numpy as np

print("Loading full audio into memory...")
# Full song is 35 minutes: 2120s * 22050 * 2 bytes = ~93 MB. Extremely small and fast!
samples = []
for chunk in miniaudio.mp3_stream_file('audio_samples/100 Ways To Love A Cat Ways 1-100.mp3'):
    s = np.frombuffer(chunk, dtype=np.int16)
    # Downsample from 44100 to 22050 mono
    mono_22k = ((s[0::4].astype(np.int32) + s[1::4].astype(np.int32)) // 2).astype(np.int16)
    samples.append(mono_22k)

audio = np.concatenate(samples)
sr = 22050
duration = len(audio) / sr
print(f"Audio loaded: {duration:.2f} seconds ({len(audio)} samples)")

r = sr_lib.Recognizer()

def recognize_window(t_start, t_duration):
    s0 = int(t_start * sr)
    s1 = int((t_start + t_duration) * sr)
    if s1 > len(audio):
        s1 = len(audio)
    seg = audio[s0:s1]
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(seg.tobytes())
    buf.seek(0)
    with sr_lib.AudioFile(buf) as source:
        audio_data = r.record(source)
    try:
        return r.recognize_google(audio_data)
    except Exception:
        return ""

# Let's inspect where "Way" appears across the timeline!
# In the lyrics, there are 25 verses:
# Verse 1: Ways 1, 2, 3, 4
# Verse 2: Ways 5, 6, 7, 8
# Verse 3: Ways 9, 10, 11, 12
# ...
# Verse 25: Ways 97, 98, 99, 100

# Let's test predicted start of each verse from V1 to V25:
# In our previous model: V_n = 3.84 + (n-1)*84.48
# Let's check V5 (predicted 341.76s), V10 (predicted 764.16s), V15 (predicted 1186.56s), V20 (predicted 1608.96s), V25 (predicted 2031.36s)
check_points = [
    (1, 0, "Way one"),
    (2, 84, "Way five"),
    (5, 340, "Way seventeen"),
    (10, 760, "Way thirty-seven"),
    (15, 1180, "Way fifty-seven"),
    (20, 1600, "Way seventy-seven"),
    (25, 2030, "Way ninety-seven")
]

for v_idx, t_guess, label in check_points:
    # Test windows around t_guess: t_guess - 20, t_guess - 10, t_guess, t_guess + 10, t_guess + 20
    print(f"\n--- Checking {label} (around {t_guess}s) ---")
    for offset in [-20, -10, 0, 10, 20]:
        t = t_guess + offset
        if t < 0 or t >= duration: continue
        res = recognize_window(t, 12)
        if res:
            print(f"  t={t}s: {res}")
