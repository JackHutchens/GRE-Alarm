"""
High-fidelity procedural audio generator for the 5 evidence-based background tracks.
Generates 30-second 44.1 kHz 16-bit stereo WAV files into audio_samples/ and brain artifacts:
1. procedural1_circadian_accelerando.wav (Lydian tempo ramp 80->120 BPM)
2. procedural2_gamma_baroque.wav (40Hz gamma entrainment + D Dorian counterpoint)
3. procedural3_fractal_pentatonic.wav (1/f fractal pitch walks, kalimba/harp, 6/8 meter)
4. procedural4_baroque_adagio_60bpm.wav (60 BPM baroreflex sync, string quartet)
5. procedural5_beta_lofi_mixolydian.wav (18Hz beta binaural, Mixolydian polyrhythms)
"""
import os
import math
import wave
import struct
import random

SAMPLE_RATE = 44100
DURATION = 30.0  # 30 seconds
NUM_SAMPLES = int(SAMPLE_RATE * DURATION)
TWO_PI = 2.0 * math.pi

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(PROJECT_ROOT, "audio_samples")
ART_DIR = r"C:\Users\jacka\.gemini\antigravity\brain\ae759fcb-adde-4ada-a1a8-c7f9b73b75ae"
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(ART_DIR, exist_ok=True)

def write_wav(filename, left_samples, right_samples):
    out_paths = [os.path.join(AUDIO_DIR, filename), os.path.join(ART_DIR, filename)]
    
    # Normalize peak to 0.88 to avoid clipping
    peak = max(max(abs(s) for s in left_samples), max(abs(s) for s in right_samples), 0.001)
    scale = 0.88 / peak if peak > 0.88 else 1.0

    frames = bytearray()
    for l, r in zip(left_samples, right_samples):
        # 16-bit signed PCM
        sl = int(max(-32767, min(32767, l * scale * 32767)))
        sr = int(max(-32767, min(32767, r * scale * 32767)))
        frames.extend(struct.pack("<hh", sl, sr))

    for p in out_paths:
        with wave.open(p, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(frames)
    print(f"Generated {filename} ({len(frames):,} bytes) at {out_paths[0]}")

def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))

# -------------------------------------------------------------
# 1. CIRCADIAN ACCELERANDO (Lydian Mode, 80 -> 120 BPM ramp)
# -------------------------------------------------------------
def gen_circadian_accelerando():
    left = [0.0] * NUM_SAMPLES
    right = [0.0] * NUM_SAMPLES

    # C Lydian scale (C, D, E, F#, G, A, B)
    # MIDI: C3=48, D3=50, E3=52, F#3=54, G3=55, A3=57, B3=59
    # C4=60, D4=62, E4=64, F#4=66, G4=67, A4=69, B4=71, C5=72, D5=74, E5=76, F#5=78, G5=79
    scale = [48, 52, 54, 55, 60, 64, 66, 67, 71, 72, 74, 76, 78, 79, 83, 84]

    # Progressive tempo: starts at 80 BPM (0.75s per beat), ramps to 120 BPM (0.50s per beat)
    # Instantaneous tempo at time t: bpm(t) = 80 + 40 * (t / 30)
    # Beat phase phi(t) = integral(bpm/60 dt) = integral((80 + 4/3 t)/60 dt) = (4/3) t + (1/90) t^2
    current_time = 0.0
    note_idx = 0
    melodic_pattern = [0, 2, 4, 7, 5, 8, 10, 12, 11, 9, 7, 5, 3, 2, 1, 0]

    while current_time < DURATION:
        progress = current_time / DURATION
        bpm = 80.0 + 40.0 * progress
        beat_len = 60.0 / bpm
        subdiv = beat_len / 2.0  # Eighth notes

        pitch_deg = melodic_pattern[note_idx % len(melodic_pattern)]
        # Ascend octaves gently
        oct_shift = int(progress * 2) * 2
        midi_pitch = scale[min(len(scale) - 1, pitch_deg + oct_shift)]
        freq = midi_to_freq(midi_pitch)

        start_samp = int(current_time * SAMPLE_RATE)
        dur_samp = int(subdiv * 1.5 * SAMPLE_RATE)
        end_samp = min(NUM_SAMPLES, start_samp + dur_samp)

        # FM synthesis for bell / marimba timbre: carrier freq, mod freq = freq * 2, mod index decays
        pan = 0.35 + 0.3 * math.sin(current_time * 1.5)
        for s in range(start_samp, end_samp):
            t = (s - start_samp) / SAMPLE_RATE
            env = math.exp(-t * 6.5)  # Perceptual decay
            mod_idx = 2.5 * math.exp(-t * 12.0)
            mod = math.sin(TWO_PI * freq * 2.0 * t) * mod_idx
            val = math.sin(TWO_PI * freq * t + mod) * env * 0.45

            # Warm low undertone
            val += math.sin(TWO_PI * (freq * 0.5) * t) * (env ** 1.5) * 0.15

            left[s] += val * (1.0 - pan)
            right[s] += val * pan

        # Bass pulse on downbeats
        if note_idx % 4 == 0:
            bass_freq = midi_to_freq(scale[0] if (note_idx // 4) % 2 == 0 else scale[3])
            b_dur = int(beat_len * 1.8 * SAMPLE_RATE)
            b_end = min(NUM_SAMPLES, start_samp + b_dur)
            for s in range(start_samp, b_end):
                t = (s - start_samp) / SAMPLE_RATE
                b_env = math.exp(-t * 3.0)
                b_val = math.sin(TWO_PI * bass_freq * t) * b_env * 0.38
                left[s] += b_val * 0.5
                right[s] += b_val * 0.5

        note_idx += 1
        current_time += subdiv

    write_wav("procedural1_circadian_accelerando.wav", left, right)

# -------------------------------------------------------------
# 2. 40 Hz GAMMA-ENTRAINED NEO-BAROQUE (D Dorian, 108 BPM)
# -------------------------------------------------------------
def gen_gamma_baroque():
    left = [0.0] * NUM_SAMPLES
    right = [0.0] * NUM_SAMPLES

    # D Dorian: D, E, F, G, A, B, C
    # Cantus firmus (bass): D2=38, F2=41, G2=43, A2=45, C3=48, D3=50
    # Countermelody (treble): D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72, D5=74, E5=76
    bass_notes = [38, 41, 43, 45, 50, 48, 45, 43, 38, 43, 45, 50, 48, 45, 41, 38]
    treble_notes = [74, 72, 69, 71, 72, 74, 76, 74, 69, 67, 65, 67, 69, 72, 71, 74,
                    76, 74, 72, 69, 67, 69, 71, 72, 74, 69, 65, 67, 69, 64, 65, 62]

    bpm = 108.0
    beat_sec = 60.0 / bpm
    half_beat = beat_sec / 2.0

    # 1. 40 Hz Gamma entrainment layer (continuous sustained pad with 40 Hz tremolo)
    for s in range(NUM_SAMPLES):
        t = s / SAMPLE_RATE
        # 40 Hz amplitude modulation depth = 35%
        gamma_lfo = 1.0 + 0.35 * math.sin(TWO_PI * 40.0 * t)
        
        # Fundamental drone in D3 (146.83 Hz) + A3 (220 Hz)
        drone1 = math.sin(TWO_PI * 146.83 * t) * 0.12
        drone2 = math.sin(TWO_PI * 220.00 * t) * 0.08
        pad = (drone1 + drone2) * gamma_lfo

        # Gentle fade in / out
        fade = min(1.0, t / 1.5) * min(1.0, (DURATION - t) / 1.5)
        left[s] += pad * fade * 0.45
        right[s] += pad * fade * 0.45

    # 2. Cantus firmus (Walking Baroque bass, quarter notes)
    t_curr = 0.0
    for idx, pitch in enumerate(bass_notes * 4):
        if t_curr >= DURATION: break
        freq = midi_to_freq(pitch)
        start_samp = int(t_curr * SAMPLE_RATE)
        dur_samp = int(beat_sec * 0.95 * SAMPLE_RATE)
        end_samp = min(NUM_SAMPLES, start_samp + dur_samp)

        for s in range(start_samp, end_samp):
            t = (s - start_samp) / SAMPLE_RATE
            env = math.exp(-t * 2.8)
            # Bowed cello harmonic recipe: fundamental + 2nd harmonic + 3rd
            val = (math.sin(TWO_PI * freq * t) * 0.45 +
                   math.sin(TWO_PI * freq * 2.0 * t) * 0.22 +
                   math.sin(TWO_PI * freq * 3.0 * t) * 0.10) * env * 0.55
            left[s] += val * 0.6
            right[s] += val * 0.4

        t_curr += beat_sec

    # 3. Treble Countermelody (Ornamented Baroque eighth notes)
    t_curr = 0.0
    for idx, pitch in enumerate(treble_notes * 4):
        if t_curr >= DURATION: break
        freq = midi_to_freq(pitch)
        start_samp = int(t_curr * SAMPLE_RATE)
        dur_samp = int(half_beat * 1.2 * SAMPLE_RATE)
        end_samp = min(NUM_SAMPLES, start_samp + dur_samp)

        for s in range(start_samp, end_samp):
            t = (s - start_samp) / SAMPLE_RATE
            env = math.exp(-t * 5.0)
            # Harpsichord/violin plucked attack
            val = (math.sin(TWO_PI * freq * t) * 0.40 +
                   math.sin(TWO_PI * freq * 2.0 * t) * 0.25 +
                   math.sin(TWO_PI * freq * 4.0 * t) * 0.12) * env * 0.48
            left[s] += val * 0.35
            right[s] += val * 0.65

        t_curr += half_beat

    write_wav("procedural2_gamma_baroque.wav", left, right)

# -------------------------------------------------------------
# 3. 1/f FRACTAL PENTATONIC (C Pentatonic, 96 BPM 6/8 Meter)
# -------------------------------------------------------------
def gen_fractal_pentatonic():
    left = [0.0] * NUM_SAMPLES
    right = [0.0] * NUM_SAMPLES

    # Pentatonic scale: C, D, E, G, A
    # C3 to A5
    pent_scale = [48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]

    # Voss-Clarke 1/f noise generator: 4 dice registers
    num_dice = 4
    dice = [random.randint(0, 3) for _ in range(num_dice)]

    bpm = 96.0
    beat_sec = 60.0 / bpm
    eighth_sec = beat_sec / 2.0  # 6/8 feel

    t_curr = 0.0
    step = 0

    while t_curr < DURATION:
        step += 1
        # Update Voss dice depending on binary trailing zeros
        for d in range(num_dice):
            if (step >> d) & 1:
                dice[d] = random.randint(0, 3)
                break
        
        pitch_idx = sum(dice)  # Ranges from 0 to 12
        pitch_idx = min(len(pent_scale) - 1, pitch_idx)
        freq = midi_to_freq(pent_scale[pitch_idx])

        # Kalimba / thumb piano synthesis: pure sine + sharp 3rd harmonic attack
        start_samp = int(t_curr * SAMPLE_RATE)
        dur_samp = int(eighth_sec * 2.2 * SAMPLE_RATE)
        end_samp = min(NUM_SAMPLES, start_samp + dur_samp)

        pan = 0.25 + (pitch_idx / len(pent_scale)) * 0.5  # Stereo spread by pitch

        for s in range(start_samp, end_samp):
            t = (s - start_samp) / SAMPLE_RATE
            env = math.exp(-t * 4.8)
            # Kalimba tine metallic overtone at 5.4x fundamental
            metallic = math.sin(TWO_PI * freq * 5.4 * t) * math.exp(-t * 24.0) * 0.25
            tone = (math.sin(TWO_PI * freq * t) + metallic) * env * 0.42

            left[s] += tone * (1.0 - pan)
            right[s] += tone * pan

        # Soft rolling low ostinato every 3 eighth notes (dotted quarter)
        if step % 3 == 0:
            root_freq = midi_to_freq(pent_scale[0] if (step // 3) % 2 == 0 else pent_scale[3])
            b_dur = int(eighth_sec * 3.0 * SAMPLE_RATE)
            b_end = min(NUM_SAMPLES, start_samp + b_dur)
            for s in range(start_samp, b_end):
                t = (s - start_samp) / SAMPLE_RATE
                b_env = math.exp(-t * 2.2)
                b_val = math.sin(TWO_PI * root_freq * t) * b_env * 0.32
                left[s] += b_val * 0.5
                right[s] += b_val * 0.5

        t_curr += eighth_sec

    write_wav("procedural3_fractal_pentatonic.wav", left, right)

# -------------------------------------------------------------
# 4. 60 BPM BAROQUE ADAGIO (Baroreflex Sync, 60 BPM exact)
# -------------------------------------------------------------
def gen_baroque_adagio_60bpm():
    left = [0.0] * NUM_SAMPLES
    right = [0.0] * NUM_SAMPLES

    # Exact 60 BPM = 1.000s per beat (Heart-Rate Baroreflex Entrainment)
    beat_sec = 1.0
    # G Major Diatonic: G, A, B, C, D, E, F#
    # Cello Basso Continuo: G2=43, D3=50, E3=52, C3=48, G2=43, C3=48, D3=50, G2=43
    basso_seq = [43, 50, 52, 48, 43, 48, 50, 43]
    
    # Cantabile Flute / Oboe solo (ornamented quarter/eighth lines)
    solo_seq = [67, 71, 74, 72, 71, 69, 67, 69, 71, 74, 76, 74, 72, 71, 69, 67]

    # 1. Basso continuo on each second
    for beat in range(int(DURATION)):
        start_samp = int(beat * beat_sec * SAMPLE_RATE)
        dur_samp = int(beat_sec * 0.92 * SAMPLE_RATE)
        end_samp = min(NUM_SAMPLES, start_samp + dur_samp)

        pitch = basso_seq[beat % len(basso_seq)]
        freq = midi_to_freq(pitch)

        for s in range(start_samp, end_samp):
            t = (s - start_samp) / SAMPLE_RATE
            env = (1.0 - math.exp(-t * 18.0)) * math.exp(-t * 1.5)  # Warm bowed attack
            # Bowed string spectrum
            val = (math.sin(TWO_PI * freq * t) * 0.45 +
                   math.sin(TWO_PI * freq * 2.0 * t) * 0.20 +
                   math.sin(TWO_PI * freq * 3.0 * t) * 0.10) * env * 0.52
            left[s] += val * 0.55
            right[s] += val * 0.45

    # 2. Viola arpeggio accompaniment (eighth notes)
    t_curr = 0.0
    arpeg_degrees = [0, 4, 7, 4]  # root, 3rd, 5th, 3rd
    while t_curr < DURATION:
        beat_idx = int(t_curr)
        root_pitch = basso_seq[beat_idx % len(basso_seq)] + 12  # Octave up
        sub_step = int((t_curr % 1.0) * 4)  # 16th/eighth subdivision
        chord_pitch = root_pitch + [0, 4, 7, 11][sub_step % 4]
        freq = midi_to_freq(chord_pitch)

        start_samp = int(t_curr * SAMPLE_RATE)
        dur_samp = int(0.25 * SAMPLE_RATE)
        end_samp = min(NUM_SAMPLES, start_samp + dur_samp)

        for s in range(start_samp, end_samp):
            t = (s - start_samp) / SAMPLE_RATE
            env = math.exp(-t * 6.0)
            val = math.sin(TWO_PI * freq * t) * env * 0.18
            left[s] += val * 0.65
            right[s] += val * 0.35

        t_curr += 0.25

    # 3. Solo Woodwind Cantabile Line
    t_curr = 0.0
    for idx, pitch in enumerate(solo_seq * 2):
        if t_curr >= DURATION: break
        freq = midi_to_freq(pitch)
        note_dur = 1.0 if idx % 3 != 0 else 0.5
        start_samp = int(t_curr * SAMPLE_RATE)
        dur_samp = int(note_dur * 0.95 * SAMPLE_RATE)
        end_samp = min(NUM_SAMPLES, start_samp + dur_samp)

        for s in range(start_samp, end_samp):
            t = (s - start_samp) / SAMPLE_RATE
            # Flute soft breathy attack + subtle vibrato (5.5 Hz)
            vibrato = 1.0 + 0.015 * math.sin(TWO_PI * 5.5 * t)
            env = (1.0 - math.exp(-t * 12.0)) * math.exp(-t * (1.2 / note_dur))
            val = (math.sin(TWO_PI * freq * vibrato * t) * 0.40 +
                   math.sin(TWO_PI * freq * 2.0 * vibrato * t) * 0.12) * env * 0.48
            left[s] += val * 0.45
            right[s] += val * 0.55

        t_curr += note_dur

    write_wav("procedural4_baroque_adagio_60bpm.wav", left, right)

# -------------------------------------------------------------
# 5. 18 Hz BETA LO-FI MIXOLYDIAN (112 BPM, Binaural Beta Beat)
# -------------------------------------------------------------
def gen_beta_lofi_mixolydian():
    left = [0.0] * NUM_SAMPLES
    right = [0.0] * NUM_SAMPLES

    # Mixolydian Mode (G, A, B, C, D, E, F natural)
    # MIDI: G3=55, A3=57, B3=59, C4=60, D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72, D5=74, F5=77
    mixo_chords = [
        [55, 59, 62, 65],  # G7 (I7)
        [65, 69, 72, 76],  # Fmaj7 (bVII)
        [60, 64, 67, 71],  # Cmaj7 (IV)
        [55, 59, 62, 65]   # G7
    ]

    bpm = 112.0
    beat_sec = 60.0 / bpm
    step_sec = beat_sec / 2.0  # 16th/eighth sequence

    # 1. 18 Hz Binaural Beta Beat Carrier Drone:
    # Left Ear = 218 Hz, Right Ear = 200 Hz -> Brain synthesizes 18 Hz Beta
    for s in range(NUM_SAMPLES):
        t = s / SAMPLE_RATE
        fade = min(1.0, t / 2.0) * min(1.0, (DURATION - t) / 2.0)
        carrier_l = math.sin(TWO_PI * 218.0 * t) * 0.08 * fade
        carrier_r = math.sin(TWO_PI * 200.0 * t) * 0.08 * fade
        left[s] += carrier_l
        right[s] += carrier_r

    # 2. Polyrhythmic Lo-Fi Arpeggiator (3 against 4)
    t_curr = 0.0
    chord_idx = 0
    bar_timer = 0.0
    arp_pattern = [0, 2, 1, 3, 2, 0, 3, 1]

    while t_curr < DURATION:
        chord = mixo_chords[chord_idx % len(mixo_chords)]
        note_in_chord = chord[arp_pattern[int(t_curr / step_sec) % len(arp_pattern)]]
        freq = midi_to_freq(note_in_chord)

        start_samp = int(t_curr * SAMPLE_RATE)
        dur_samp = int(step_sec * 1.6 * SAMPLE_RATE)
        end_samp = min(NUM_SAMPLES, start_samp + dur_samp)

        pan = 0.3 + 0.4 * math.sin(t_curr * 2.0)

        for s in range(start_samp, end_samp):
            t = (s - start_samp) / SAMPLE_RATE
            env = math.exp(-t * 6.5)
            # Warm electric Rhodes piano: soft fundamental + gentle 2nd harmonic
            val = (math.sin(TWO_PI * freq * t) * 0.42 +
                   math.sin(TWO_PI * freq * 2.0 * t) * 0.15) * env * 0.50
            left[s] += val * (1.0 - pan)
            right[s] += val * pan

        # Soft Sub-kick / tick on beats 1 and 3
        if int(t_curr / beat_sec) != int((t_curr - step_sec) / beat_sec):
            beat_num = int(t_curr / beat_sec) % 4
            if beat_num in (0, 2):
                k_dur = int(0.25 * SAMPLE_RATE)
                k_end = min(NUM_SAMPLES, start_samp + k_dur)
                for s in range(start_samp, k_end):
                    t = (s - start_samp) / SAMPLE_RATE
                    k_freq = 70.0 * math.exp(-t * 18.0) + 40.0
                    k_val = math.sin(TWO_PI * k_freq * t) * math.exp(-t * 9.0) * 0.38
                    left[s] += k_val * 0.5
                    right[s] += k_val * 0.5

        t_curr += step_sec
        bar_timer += step_sec
        if bar_timer >= beat_sec * 4.0:
            bar_timer = 0.0
            chord_idx += 1

    write_wav("procedural5_beta_lofi_mixolydian.wav", left, right)

def main():
    print("Generating 30s samples for all 5 procedural options...")
    gen_circadian_accelerando()
    gen_gamma_baroque()
    gen_fractal_pentatonic()
    gen_baroque_adagio_60bpm()
    gen_beta_lofi_mixolydian()
    print("All 5 audio samples successfully generated!")

if __name__ == "__main__":
    main()
