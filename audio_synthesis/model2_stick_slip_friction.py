"""
Model 2 (10-Minute Expanded): Frictional Stick-Slip "Chalkboard Screech"

Acoustic & Neurobiological Mechanism:
Non-linear stick-slip friction creates violent impulse trains characterized by extreme
spectral kurtosis (sharp non-Gaussian energy spikes) concentrated between 2,800 and 4,500 Hz,
where the human concha and ear canal provide a natural +12 dB to +16 dB mechanical amplification,
inducing instinctive spine-chilling revulsion.

10-Minute Anti-Habituation Architecture:
Driven by an Aperiodic Permutation Engine that sequences through 5 distinct physical scraping
gestures (Heavy Grates, High-Velocity Screeches, Stutter-Slip Bursts, Squeal Glissandi, and
Deceptive Pauses) with continuously shifting contact pressures, slip velocities, and resonant poles.
Zero periodic cadence or repeating gestures across 10+ minutes.
"""

import numpy as np
from scipy import signal
from typing import Optional
from .base_generator import BaseAudioGenerator
from .permutation_engine import AperiodicPermutationEngine

class StickSlipFrictionGenerator(BaseAudioGenerator):
    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="Model 2: Frictional Stick-Slip Screech", seed=seed)
        self.perm_engine = AperiodicPermutationEngine(seed=self.seed)

    def generate(self, duration_seconds: float = 600.0) -> np.ndarray:
        n_samples = int(duration_seconds * self.sample_rate)
        output = np.zeros(n_samples, dtype=np.float32)

        # 5 distinct frictional physical scrape regimes
        scrape_modes = [
            "HEAVY_PRESSURE_GRATE",
            "HIGH_VELOCITY_SCREECH",
            "STUTTER_SLIP_BURST",
            "SQUEAL_GLISSANDO",
            "DECEPTIVE_PAUSE"
        ]

        # Calculate number of scrape gestures required for duration
        # Average gesture is ~1.4s, so 600s needs ~450 gestures
        num_gestures = int(duration_seconds / 1.3) + 30
        gesture_sequence = self.perm_engine.generate_non_repeating_sequence(scrape_modes, length=num_gestures)
        durations = self.perm_engine.get_aperiodic_intervals(len(gesture_sequence), min_val=0.6, max_val=2.2)

        current_time = 0.05
        for mode, dur in zip(gesture_sequence, durations):
            if current_time >= duration_seconds - 0.1:
                break

            start_idx = int(current_time * self.sample_rate)
            event_len = int(dur * self.sample_rate)
            end_idx = min(n_samples, start_idx + event_len)
            act_len = end_idx - start_idx

            if act_len <= 0:
                break

            t_ev = np.linspace(0.0, dur, act_len, endpoint=False, dtype=np.float32)
            norm_t = t_ev / dur
            block = np.zeros(act_len, dtype=np.float32)

            if mode == "HEAVY_PRESSURE_GRATE":
                # High contact pressure, slow abrasive dragging
                f_res = self.rng.uniform(2800.0, 3400.0)
                q = self.rng.uniform(14.0, 22.0)
                slip_freq = self.rng.uniform(110.0, 190.0)
                phase_slip = 2.0 * np.pi * slip_freq * t_ev
                saw_slip = (phase_slip % (2.0 * np.pi)) ** 3.0
                stoch_grains = self.rng.standard_normal(act_len) * (self.rng.uniform(0.0, 1.0, act_len) > 0.85)
                raw = (saw_slip * 0.8 + stoch_grains * 1.6) * (np.sin(np.pi * norm_t) ** 0.8)
                b, a = signal.iirpeak(f_res, q, fs=self.sample_rate)
                block = signal.lfilter(b, a, raw).astype(np.float32) * 3.8

            elif mode == "HIGH_VELOCITY_SCREECH":
                # Fast scrape speed, piercing 3.8-4.6 kHz resonance
                f_res1 = self.rng.uniform(3700.0, 4200.0)
                f_res2 = self.rng.uniform(4300.0, 4800.0)
                noise = self.rng.standard_normal(act_len)
                b1, a1 = signal.iirpeak(f_res1, Q=18.0, fs=self.sample_rate)
                b2, a2 = signal.iirpeak(f_res2, Q=22.0, fs=self.sample_rate)
                filt = signal.lfilter(b1, a1, noise) + 0.6 * signal.lfilter(b2, a2, noise)
                # Amplitude flutter (30-60 Hz)
                flutter = np.sin(2.0 * np.pi * self.rng.uniform(32.0, 55.0) * t_ev)
                block = (filt * (0.6 + 0.4 * flutter) * np.sin(np.pi * norm_t)).astype(np.float32) * 4.2

            elif mode == "STUTTER_SLIP_BURST":
                # Micro-slip chatter (chattering chalk/metal teeth)
                chatter_rate = self.rng.uniform(45.0, 85.0)
                chatter_pulses = (np.sin(2.0 * np.pi * chatter_rate * t_ev) > 0.6).astype(np.float32)
                f_res = self.rng.uniform(3100.0, 3700.0)
                b, a = signal.iirpeak(f_res, Q=16.0, fs=self.sample_rate)
                stoch = self.rng.standard_normal(act_len) * chatter_pulses
                block = signal.lfilter(b, a, stoch).astype(np.float32) * 4.5

            elif mode == "SQUEAL_GLISSANDO":
                # Pure agonizing metallic chalk squeal sliding in pitch
                f_start = self.rng.uniform(3000.0, 3600.0)
                f_end = self.rng.uniform(3800.0, 4600.0)
                f_curve = np.linspace(f_start, f_end, act_len)
                phase_sq = 2.0 * np.pi * np.cumsum(f_curve / self.sample_rate)
                flutter_sq = 60.0 * np.sin(2.0 * np.pi * 38.0 * t_ev)
                squeal = np.sign(np.sin(phase_sq + flutter_sq)) * (np.sin(np.pi * norm_t) ** 1.2)
                block = squeal.astype(np.float32) * 0.45

            elif mode == "DECEPTIVE_PAUSE":
                # Friction release micro-pause to prevent auditory adaptation
                whisper = self.rng.standard_normal(act_len) * 0.03
                block = whisper.astype(np.float32)

            # Smooth block transitions
            fade = min(int(0.003 * self.sample_rate), act_len // 4)
            if fade > 0:
                block[:fade] *= np.linspace(0.0, 1.0, fade)
                block[-fade:] *= np.linspace(1.0, 0.0, fade)

            output[start_idx:end_idx] += block
            current_time += dur

        # Final non-linear saturation
        return np.tanh(output * 1.8)
