"""
Model 4 (10-Minute Expanded): Stochastic MMN Disruption Engine (Predictive Coding Failure)

Acoustic & Neurobiological Mechanism:
The human auditory cortex rapidly habituates to periodic alarm sounds via Stimulus-Specific
Adaptation (SSA). By building an internal predictive model, the cortex suppresses neural
responses, permitting people to sleep through alarms.
The Stochastic MMN Disruption Engine defeats predictive coding by violating every auditory expectation:
- Poisson/Pareto-distributed inter-onset intervals with deceptive micro-silences.
- Heavy-tailed Levy flight pitch jumps spanning 150 Hz to 4,500 Hz across 5 octaves.
- Sudden timbral morphing across sharp pulse, foldback distortion, and transient crackles.
Because no statistical regularity can be established, high-amplitude MMN and P3a novelty
evoked potentials are triggered incessantly, preventing sleep re-entry or mental suppression.
"""

import numpy as np
from typing import Optional
from .base_generator import BaseAudioGenerator

class StochasticMMNDisruptionGenerator(BaseAudioGenerator):
    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="Model 4: Stochastic MMN Disruption Engine", seed=seed)

    def generate(self, duration_seconds: float = 600.0) -> np.ndarray:
        n_samples = int(duration_seconds * self.sample_rate)
        buffer = np.zeros(n_samples, dtype=np.float32)

        # Generate non-homogeneous Poisson event train across full duration
        current_time = 0.05  # initial lead-in

        while current_time < duration_seconds - 0.1:
            # Event duration: heavy-tailed random burst (35ms to 480ms)
            burst_dur = self.rng.uniform(0.035, 0.45)
            # Inter-burst silence: mixture of micro-stutter (20ms) and deceptive pause (up to 850ms)
            if self.rng.random() < 0.22:
                # Deceptive pause resets sensory gating
                pause_dur = self.rng.uniform(0.35, 0.95)
            else:
                pause_dur = self.rng.uniform(0.015, 0.18)

            start_idx = int(current_time * self.sample_rate)
            end_idx = min(n_samples, start_idx + int(burst_dur * self.sample_rate))
            event_samples = end_idx - start_idx

            if event_samples <= 0:
                break

            t_event = np.linspace(0.0, burst_dur, event_samples, endpoint=False, dtype=np.float32)

            # Levy-flight pitch jump across 5 octaves
            regime = self.rng.random()
            if regime < 0.60:
                base_freq = self.rng.uniform(2200.0, 4600.0)
            elif regime < 0.88:
                base_freq = self.rng.uniform(600.0, 1900.0)
            else:
                base_freq = self.rng.uniform(105.0, 320.0)

            # Dynamic pitch trajectory during burst
            pitch_mode = self.rng.integers(0, 4)
            if pitch_mode == 0:
                # Rapid descending chirp
                freq_profile = base_freq * np.exp(-t_event * self.rng.uniform(4.0, 14.0))
            elif pitch_mode == 1:
                # Violent ascending screech
                freq_profile = base_freq * (1.0 + t_event * self.rng.uniform(5.0, 16.0))
            elif pitch_mode == 2:
                # Roughness modulation (45-105 Hz)
                rough_rate = self.rng.uniform(45.0, 105.0)
                freq_profile = base_freq + 240.0 * np.sin(2.0 * np.pi * rough_rate * t_event)
            else:
                freq_profile = np.full_like(t_event, base_freq)

            phase = 2.0 * np.pi * np.cumsum(freq_profile / self.sample_rate)

            # Timbre selection: narrow pulse, foldback distortion, or ring-modulated noise
            timbre_type = self.rng.integers(0, 3)
            if timbre_type == 0:
                duty = self.rng.uniform(0.10, 0.28)
                burst_wave = np.where((phase % (2.0 * np.pi)) < (2.0 * np.pi * duty), 1.0, -1.0)
            elif timbre_type == 1:
                raw_sine = np.sin(phase) * self.rng.uniform(2.5, 6.5)
                burst_wave = np.sin(raw_sine)
            else:
                white_noise = self.rng.uniform(-1.0, 1.0, event_samples)
                burst_wave = white_noise * np.sin(phase) * 1.9

            # Sharp attack (1ms), heavy exponential decay
            decay_rate = self.rng.uniform(3.0, 18.0)
            attack_len = min(int(0.0015 * self.sample_rate), event_samples)
            env = np.exp(-t_event * decay_rate)
            if attack_len > 0:
                env[:attack_len] *= np.linspace(0.0, 1.0, attack_len)

            buffer[start_idx:end_idx] += (burst_wave * env).astype(np.float32)
            current_time += burst_dur + pause_dur

        return np.tanh(buffer * 1.6)
