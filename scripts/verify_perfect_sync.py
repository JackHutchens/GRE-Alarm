import miniaudio
import speech_recognition as sr_lib
import io
import wave
import numpy as np

verse_starts = np.load('scripts/verse_starts.npy')
print("Loaded verse starts for 25 verses.")

# Audio
samples = []
for chunk in miniaudio.mp3_stream_file('audio_samples/100 Ways To Love A Cat Ways 1-100.mp3'):
    s = np.frombuffer(chunk, dtype=np.int16)
    mono_22k = ((s[0::4].astype(np.int32) + s[1::4].astype(np.int32)) // 2).astype(np.int16)
    samples.append(mono_22k)
audio = np.concatenate(samples)
sr = 22050
r = sr_lib.Recognizer()

def recognize_clip(t0, t1):
    seg = audio[int(t0*sr):int(t1*sr)]
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
    except Exception as e:
        return f"<Error: {e}>"

# Let's check Way 1 (Verse 1), Way 17 (Verse 5), Way 37 (Verse 10), Way 57 (Verse 15), Way 77 (Verse 20), Way 97 (Verse 25)
test_ways = [
    (1, 1, 0, "Way 1: keep a tidy house for them"),
    (5, 17, 0, "Way 17: play them some music"),
    (10, 37, 0, "Way 37: praise them lavishly"),
    (15, 57, 0, "Way 57: record precious memories"),
    (20, 77, 0, "Way 77: massage his paws"),
    (25, 97, 0, "Way 97: never leave them behind")
]

for v_num, way_num, k_in_v, expected in test_ways:
    v_start = verse_starts[v_num - 1]
    way_start = v_start + (k_in_v * 15.36)
    advice_start = way_start + 7.68
    # Test advice clip: advice_start to advice_start + 5.5s
    res = recognize_clip(advice_start, advice_start + 5.5)
    print(f"Way {way_num} (V{v_num}) at {advice_start:.2f}s:")
    print(f"  Expected: {expected}")
    print(f"  Heard:    '{res}'")
    print("-" * 50)
