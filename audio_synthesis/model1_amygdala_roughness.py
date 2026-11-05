"""
Model 1 (10-Minute Expanded): Amygdala Roughness Harvester

Acoustic & Neurobiological Mechanism:
Natural human speech strictly stays below 20-30 Hz amplitude modulation. In contrast,
human screams, alarms, and predatory threats selectively occupy the 30-130 Hz "roughness"
envelope. This roughness bypasses cortical speech decoders and directly stimulates the
amygdala, eliciting rapid autonomic arousal, acute stress, and visceral unpleasantness.

10-Minute Anti-Habituation Architecture:
Uses incommensurate irrational frequency modulation sums (phi, sqrt(2), sqrt(3), pi)
and continuous aperiodic carrier drift to guarantee zero periodic recurrence over 10+ minutes.
Periodic panic glitches and distress screech slips occur on a non-repeating golden-ratio schedule.
"""

import numpy as np
from typing import Optional
from .base_generator import BaseAudioGenerator
from .permutation_engine import AperiodicPermutationEngine

class AmygdalaRoughnessGenerator(BaseAudioGenerator):
    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="Model 1: Amygdala Roughness Harvester", seed=seed)
        self.perm_engine = AperiodicPermutationEngine(seed=self.seed)

    def generate(self, duration_seconds: float = 600.0) -> np.ndarray:
        n_samples = int(duration_seconds * self.sample_rate)
        t = np.linspace(0.0, duration_seconds, n_samples, endpoint=False, dtype=np.float32)

        # Incommensurate irrational frequencies for aperiodic continuous macro-drift
        # Golden ratio (phi) and sqrt(2) ensure non-repeating quasi-periodic trajectories
        phi = 1.6180339887
        sq2 = 1.4142135623
        sq3 = 1.7320508075

        # Macro carrier trajectory drifting continuously across the 2,700 - 4,200 Hz resonance zone
        carrier_drift1 = (
            3200.0 +
            400.0 * np.sin(2.0 * np.pi * (0.07 * phi) * t) +
            250.0 * np.sin(2.0 * np.pi * (0.13 * sq2) * t) +
            150.0 * np.cos(2.0 * np.pi * (0.23 * sq3) * t)
        )
        carrier_drift2 = (
            3800.0 +
            350.0 * np.cos(2.0 * np.pi * (0.05 * sq2) * t) +
            200.0 * np.sin(2.0 * np.pi * (0.11 * phi) * t)
        )

        # Non-stationary Roughness Modulators (45 to 115 Hz) with continuous drift
        fm_rate1 = 58.0 + 18.0 * np.sin(2.0 * np.pi * 0.041 * t)
        fm_rate2 = 92.0 + 22.0 * np.cos(2.0 * np.pi * 0.063 * t)

        # Phase accumulation for FM
        phase_fm1 = 2.0 * np.pi * np.cumsum(fm_rate1 / self.sample_rate)
        phase_fm2 = 2.0 * np.pi * np.cumsum(fm_rate2 / self.sample_rate)

        # Non-linear phase modulation
        mod_index1 = 3.2 + 1.2 * np.sin(2.0 * np.pi * 0.027 * t)
        mod_index2 = 2.5 + 0.8 * np.cos(2.0 * np.pi * 0.038 * t)

        phi_fm1 = mod_index1 * np.sin(phase_fm1)
        phi_fm2 = mod_index2 * np.sin(phase_fm2)

        phase_carrier1 = 2.0 * np.pi * np.cumsum(carrier_drift1 / self.sample_rate) + phi_fm1
        phase_carrier2 = 2.0 * np.pi * np.cumsum(carrier_drift2 / self.sample_rate) + phi_fm2

        # Odd-harmonic wave-folded carrier waveforms
        sig1 = np.sin(np.sin(phase_carrier1) * 1.6)
        sig2 = np.cos(np.sin(phase_carrier2) * 1.4)
        combined_carriers = 0.6 * sig1 + 0.4 * sig2

        # Severe amplitude roughness modulation (AM) with aperiodic beating
        am_rate1 = 64.0 + 16.0 * np.sin(2.0 * np.pi * 0.082 * t)
        am_rate2 = 104.0 + 20.0 * np.cos(2.0 * np.pi * 0.054 * t)
        phase_am1 = 2.0 * np.pi * np.cumsum(am_rate1 / self.sample_rate)
        phase_am2 = 2.0 * np.pi * np.cumsum(am_rate2 / self.sample_rate)

        am_comp = 0.5 + 0.3 * np.sign(np.sin(phase_am1)) + 0.2 * np.sin(phase_am2)

        # Aperiodic panic gating: staccato bursts with pseudo-random intervals across the full 10 minutes
        # Sum of prime-modulo square waves creates an aperiodic pulse train
        gate_lfo1 = np.sin(2.0 * np.pi * 2.83 * t)
        gate_lfo2 = np.sin(2.0 * np.pi * (2.83 * phi) * t)
        gate_lfo3 = np.sin(2.0 * np.pi * 0.31 * t)
        panic_gate = 0.4 + 0.6 * (np.sign(gate_lfo1 + 0.7 * gate_lfo2 + 0.5 * gate_lfo3) > 0.0)

        raw_output = combined_carriers * am_comp * panic_gate

        # Intermittent biological distress screech slips at golden-ratio intervals
        slip_intervals = self.perm_engine.get_aperiodic_intervals(
            int(duration_seconds / 2.0), min_val=1.2, max_val=4.5
        )
        distress_track = np.zeros(n_samples, dtype=np.float32)
        cur_t = 0.8
        for interval in slip_intervals:
            if cur_t >= duration_seconds - 0.5:
                break
            idx_start = int(cur_t * self.sample_rate)
            dur_slip = self.rng.uniform(0.12, 0.35)
            idx_end = min(n_samples, idx_start + int(dur_slip * self.sample_rate))
            slip_samples = idx_end - idx_start
            if slip_samples > 0:
                t_sl = np.linspace(0.0, dur_slip, slip_samples, endpoint=False)
                f_sl = self.rng.uniform(3600.0, 4800.0) * (1.0 - t_sl * 2.0)
                phase_sl = 2.0 * np.pi * np.cumsum(f_sl / self.sample_rate)
                env_sl = np.exp(-t_sl * 12.0)
                distress_track[idx_start:idx_end] += (np.sin(phase_sl) * env_sl * 0.75).astype(np.float32)
            cur_t += interval + dur_slip

        composite = raw_output + distress_track
        return np.tanh(composite * 2.2)
