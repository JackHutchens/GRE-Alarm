"""
Model 5 (10-Minute Expanded): Hyperbolic Auditory Looming & Infrasonic Intermodulation

Acoustic & Neurobiological Mechanism:
Primates possess an evolutionary auditory looming bias: sounds with accelerating pitch
and rising volume are hardwired into the periaqueductal gray (PAG) as an approaching
projectile on a direct collision course. Looming sounds trigger defensive motor priming,
muscle tension, and sympathetic spikes. When paired with an 8.5 Hz infrasonic intermodulation
beat, it stimulates the saccular vestibular pathway, generating somatic dizziness, tension, and nausea.

10-Minute Anti-Habituation Architecture:
Driven by an Aperiodic Permutation Engine that randomizes collision durations (0.9s to 3.2s),
acceleration exponents (gamma in [1.9, 4.8]), frequency horizons (f_start from 450-1400 Hz,
f_end from 3400-5200 Hz), and vestibular beat offsets across the full 10-minute window.
"""

import numpy as np
from typing import Optional
from .base_generator import BaseAudioGenerator
from .permutation_engine import AperiodicPermutationEngine

class HyperbolicLoomingGenerator(BaseAudioGenerator):
    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="Model 5: Hyperbolic Auditory Looming", seed=seed)
        self.perm_engine = AperiodicPermutationEngine(seed=self.seed)

    def generate(self, duration_seconds: float = 600.0) -> np.ndarray:
        n_samples = int(duration_seconds * self.sample_rate)
        t = np.linspace(0.0, duration_seconds, n_samples, endpoint=False, dtype=np.float32)
        output = np.zeros(n_samples, dtype=np.float32)

        # Estimate number of looming cycles for duration
        num_cycles = int(duration_seconds / 1.6) + 40
        cycle_durations = self.perm_engine.get_aperiodic_intervals(num_cycles, min_val=0.85, max_val=2.9)

        current_time = 0.0
        for dur in cycle_durations:
            if current_time >= duration_seconds:
                break

            start_idx = int(current_time * self.sample_rate)
            cycle_samples = int(dur * self.sample_rate)
            end_idx = min(n_samples, start_idx + cycle_samples)
            act_len = end_idx - start_idx

            if act_len <= 0:
                break

            t_cyc = np.linspace(0.0, dur, act_len, endpoint=False, dtype=np.float32)
            norm_t = t_cyc / dur

            # Permute looming trajectory parameters per cycle
            f_start = self.rng.uniform(500.0, 1200.0)
            f_end = self.rng.uniform(3600.0, 5000.0)
            curvature = self.rng.uniform(2.2, 4.5)
            f_infra = self.rng.uniform(7.0, 11.2)

            freq_curve = f_start + (f_end - f_start) * (norm_t ** curvature)

            phase1 = 2.0 * np.pi * np.cumsum(freq_curve / self.sample_rate)
            phase2 = 2.0 * np.pi * np.cumsum((freq_curve + f_infra) / self.sample_rate)

            # Asymmetric looming crescendo (exponential approaching velocity)
            amp_env = (np.exp(norm_t * 3.6) - 1.0) / (np.exp(3.6) - 1.0)

            carrier1 = np.sin(phase1) + 0.35 * np.sign(np.sin(2.0 * phase1))
            carrier2 = np.sin(phase2)

            wave = (0.55 * carrier1 + 0.45 * carrier2) * amp_env

            # Cliff-edge cutoff right before collision to elicit acoustic startle
            cutoff = min(int(0.006 * self.sample_rate), act_len)
            if cutoff > 0:
                wave[-cutoff:] *= np.linspace(1.0, 0.0, cutoff)

            output[start_idx:end_idx] += wave.astype(np.float32)
            current_time += dur

        # Dissonant high-frequency pedestal background to maintain tension between crashes
        pedestal_freq = 3450.0 + 200.0 * np.sin(2.0 * np.pi * 0.015 * t)
        pedestal = np.sin(2.0 * np.pi * np.cumsum(pedestal_freq / self.sample_rate)) * 0.14
        output += pedestal

        return np.tanh(output * 1.6)
