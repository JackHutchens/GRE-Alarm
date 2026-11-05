import miniaudio
import numpy as np
import scipy.signal

print("Streaming audio and computing band energies...")
sr = 22050
chunk_sec = 0.1 # 100ms
chunk_len = int(sr * chunk_sec)

# Filter coefficients for vocal band (300 Hz - 3000 Hz)
sos_vocal = scipy.signal.butter(4, [300, 3000], btype='bandpass', fs=sr, output='sos')
# Low band for drum kick (40 - 150 Hz)
sos_kick = scipy.signal.butter(4, [40, 150], btype='bandpass', fs=sr, output='sos')

vocal_energy = []
kick_energy = []
total_samples = 0

buffer = []
for segment in miniaudio.mp3_stream_file('audio_samples/100 Ways To Love A Cat Ways 1-100.mp3'):
    # segment is 16-bit stereo at 44100 Hz. Downsample to mono 22050 by taking every 4th sample
    s = np.frombuffer(segment, dtype=np.int16)
    mono_22k = ((s[0::4].astype(np.float32) + s[1::4].astype(np.float32)) * 0.5)
    buffer.append(mono_22k)
    total_samples += len(mono_22k)
    
    if total_samples >= chunk_len * 100: # process in ~10s blocks
        block = np.concatenate(buffer)
        buffer = []
        total_samples = 0
        
        # Filter
        vocal_sig = scipy.signal.sosfilt(sos_vocal, block)
        kick_sig = scipy.signal.sosfilt(sos_kick, block)
        
        # Reshape into chunks
        n_chunks = len(block) // chunk_len
        v_e = np.sqrt(np.mean(vocal_sig[:n_chunks * chunk_len].reshape(n_chunks, chunk_len)**2, axis=1))
        k_e = np.sqrt(np.mean(kick_sig[:n_chunks * chunk_len].reshape(n_chunks, chunk_len)**2, axis=1))
        
        vocal_energy.extend(v_e)
        kick_energy.extend(k_e)

print(f"Processed {len(vocal_energy)} chunks ({len(vocal_energy)*chunk_sec:.1f}s)")
vocal_arr = np.array(vocal_energy)
kick_arr = np.array(kick_energy)
np.savez('scripts/cat_song_energy.npz', vocal=vocal_arr, kick=kick_arr, dt=chunk_sec)
print("Saved cat_song_energy.npz")
