import miniaudio
import speech_recognition as sr_lib
import io
import wave
import numpy as np

# Load first 180 seconds mono
samples = []
for chunk in miniaudio.mp3_stream_file('audio_samples/100 Ways To Love A Cat Ways 1-100.mp3'):
    s = np.frombuffer(chunk, dtype=np.int16)
    mono_22k = ((s[0::4].astype(np.int32) + s[1::4].astype(np.int32)) // 2).astype(np.int16)
    samples.append(mono_22k)
    if len(samples) * len(mono_22k) >= 180 * 22050:
        break

audio = np.concatenate(samples)[:180 * 22050]
sr = 22050
r = sr_lib.Recognizer()

def recognize_win(t0, t1):
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
    except Exception:
        return "<silent/unrecognized>"

# Test every 4 bars (7.68s) from 0s to 170s
for t in range(0, 165, 4):
    text = recognize_win(t, t + 6.0)
    print(f"t={t:3d}s - {t+6:3d}s: {text}")
