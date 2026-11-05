import miniaudio
import speech_recognition as sr_lib
import io
import wave
import numpy as np

# Load audio
samples = []
for chunk in miniaudio.mp3_stream_file('audio_samples/100 Ways To Love A Cat Ways 1-100.mp3'):
    s = np.frombuffer(chunk, dtype=np.int16)
    mono_22k = ((s[0::4].astype(np.int32) + s[1::4].astype(np.int32)) // 2).astype(np.int16)
    samples.append(mono_22k)

audio = np.concatenate(samples)
sr = 22050
r = sr_lib.Recognizer()

def recognize_snippet(t_start, t_dur=6.0):
    s0 = int(t_start * sr)
    s1 = int((t_start + t_dur) * sr)
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

verse_starts = [4.0] # Verse 1 starts at 4.0s
print("Verse 1 start: 4.0s")

# Let's find the start of Verse 2 through Verse 25
current_t = 4.0
for v in range(2, 26):
    # Search around current_t + 78s to current_t + 83s
    # Specifically, look for "there are 100 ways" or "way"
    best_t = current_t + 80.0 # default 80s
    found = False
    for t_test in np.arange(current_t + 76.0, current_t + 85.0, 1.92):
        text = recognize_snippet(t_test, 5.0)
        if "100" in text or "cat" in text or "way" in text or "love" in text:
            best_t = t_test
            found = True
            print(f"Verse {v:2d} found at {best_t:.2f}s: '{text}' (delta: {best_t - current_t:.2f}s)")
            break
    if not found:
        print(f"Verse {v:2d} estimated at {best_t:.2f}s (delta: {best_t - current_t:.2f}s)")
    verse_starts.append(best_t)
    current_t = best_t

np.save('scripts/verse_starts.npy', np.array(verse_starts))
print("Saved verse_starts.npy")
