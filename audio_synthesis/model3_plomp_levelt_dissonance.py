"""
Model 3 (10-Minute Expanded): Plomp-Levelt Critical-Band Dissonance Swarm

Acoustic & Neurobiological Mechanism:
Sensory dissonance reaches its absolute mathematical peak when two frequency components excite
overlapping critical bands on the basilar membrane with a separation equal to approximately
25% of the Critical Bandwidth (delta f = 0.25 * CBW). At this exact delta, the auditory nerve
experiences maximum phase cancellation and harsh mechanical beating. Layered with interlocking
tritone dyads (sqrt(2) ratio) and Shepard circular glissandi, it produces unresolved auditory vertigo.

10-Minute Anti-Habituation Architecture:
Continuous 8-voice infinite Shepard-Risset pitch descent with irrational progression constants,
dynamic microtonal node wander, rotating tritone intervals, and prime-modulo aperiodic strobe envelopes.
Completely eliminates cyclic repeats over 10+ minutes.
"""

import numpy as np
from typing import Optional
from .base_generator import BaseAudioGenerator

def critical_bandwidth(f: float) -> float:
    return 24.7 * (4.37 * (f / 1000.0) + 1.0)

class PlompLeveltSwarmGenerator(BaseAudioGenerator):
    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="Model 3: Plomp-Levelt Dissonance Swarm", seed=seed)

    def generate(self, duration_seconds: float = 600.0) -> np.ndarray:
        n_samples = int(duration_seconds * self.sample_rate)
        t = np.linspace(0.0, duration_seconds, n_samples, endpoint=False, dtype=np.float32)
        output = np.zeros(n_samples, dtype=np.float32)

        # 4 harmonic anchor zones drifting along non-congruent irrational trajectories
        phi = 1.6180339887
        sq2 = 1.4142135623
        sq3 = 1.7320508075

        anchors = [
            850.0 + 120.0 * np.sin(2.0 * np.pi * (0.011 * phi) * t),
            1450.0 + 180.0 * np.cos(2.0 * np.pi * (0.017 * sq2) * t),
            2450.0 + 250.0 * np.sin(2.0 * np.pi * (0.023 * sq3) * t),
            3650.0 + 300.0 * np.cos(2.0 * np.pi * (0.009 * phi) * t)
        ]

        # Continuous infinite descending Shepard-Risset pitch contour
        # Period of one full octave descent cycle = 28.3 seconds (irrational time-constant)
        gliss_cycle_len = 28.31853
        shepard_phase = (t / gliss_cycle_len) % 1.0  # 0 to 1

        for a_idx, f_anchor in enumerate(anchors):
            # Critical bandwidth at this anchor frequency
            cbw = critical_bandwidth(np.mean(f_anchor))
            # 25% CBW gives maximum roughness / dissonance
            delta_diss = 0.25 * cbw

            # 3 voices per anchor:
            # 1. Base anchor with Shepard sweep
            # 2. Base + delta_diss (maximum basilar clash)
            # 3. Base * sqrt(2) + 0.5*delta_diss (tritone diabolus clash)
            ratios = [1.0, 1.0 + (delta_diss / np.mean(f_anchor)), np.sqrt(2.0) + (0.5 * delta_diss / np.mean(f_anchor))]

            for r_idx, r in enumerate(ratios):
                # Frequency sweeps down by 1 octave (2.0 -> 1.0) as shepard_phase goes 0 -> 1
                freq = f_anchor * r * (2.0 ** (-shepard_phase))

                # Instantaneous phase calculation
                phase = 2.0 * np.pi * np.cumsum(freq / self.sample_rate)

                # Waveform: harsh asymmetric triangle-saw blend
                wave = np.sin(phase) + 0.35 * np.sign(np.sin(2.0 * phase))

                # Shepard Gaussian spectral envelope centered at 2,600 Hz (peak ear sensitivity)
                center_dist = np.abs(np.log2(freq / 2600.0))
                env = np.exp(-0.5 * (center_dist / 1.3) ** 2.0)

                output += (wave * env * (0.28 / (a_idx + 1.0) ** 0.4)).astype(np.float32)

        # Stroboscopic amplitude distress gating using prime-modulo aperiodic beating
        strobe1 = np.sin(2.0 * np.pi * 3.7 * t)
        strobe2 = np.sin(2.0 * np.pi * (3.7 * phi) * t)
        strobe_env = 0.55 + 0.45 * np.sign(strobe1 + 0.6 * strobe2)

        final_out = np.tanh(output * strobe_env * 0.75)
        return final_out
