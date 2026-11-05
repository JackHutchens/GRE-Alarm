"""
Base Audio Generator for Psychoacoustic Aversive Alarm Synthesis.
Provides standard 16-bit 44.1kHz audio buffer management, normalization,
soft-clipping, WAV export, and seed management.
"""

import os
import wave
import struct
import numpy as np
from typing import Optional

SAMPLE_RATE = 44100

class BaseAudioGenerator:
    def __init__(self, name: str, seed: Optional[int] = None):
        self.name = name
        self.sample_rate = SAMPLE_RATE
        self.seed = seed if seed is not None else np.random.randint(0, 1000000)
        self.rng = np.random.default_rng(self.seed)

    def generate(self, duration_seconds: float = 30.0) -> np.ndarray:
        """Subclasses must implement this and return a 1D float32/float64 array in range [-1.0, 1.0]."""
        raise NotImplementedError

    def export_wav(self, output_path: str, duration_seconds: float = 30.0) -> str:
        """Generates audio, normalizes, applies soft-knee limiting, and writes to 16-bit PCM WAV."""
        print(f"[{self.name}] Generating {duration_seconds}s audio clip (seed={self.seed})...")
        raw_audio = self.generate(duration_seconds)

        # Safety: check for NaN/Inf
        raw_audio = np.nan_to_num(raw_audio, nan=0.0, posinf=0.9, neginf=-0.9)

        # Soft-knee saturation / limiting to prevent hard clipping: tanh curve
        processed = np.tanh(raw_audio * 1.1)

        # Peak normalization to -0.5 dBFS (~0.94)
        peak = np.max(np.abs(processed))
        if peak > 1e-4:
            processed = processed * (0.94 / peak)
        else:
            processed = np.zeros_like(processed)

        # 5ms gentle fade-in and fade-out to prevent speaker pops
        fade_len = int(0.005 * self.sample_rate)
        if len(processed) > 2 * fade_len:
            fade_in = np.linspace(0.0, 1.0, fade_len)
            fade_out = np.linspace(1.0, 0.0, fade_len)
            processed[:fade_len] *= fade_in
            processed[-fade_len:] *= fade_out

        # Convert to 16-bit PCM
        int16_samples = np.int16(processed * 32767.0)

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(int16_samples.tobytes())

        size_kb = os.path.getsize(output_path) / 1024.0
        print(f"[{self.name}] Exported {output_path} ({size_kb:.1f} KB).")
        return output_path
