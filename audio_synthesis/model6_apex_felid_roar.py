"""
Model 6 (V2 - Upgraded): Apex Felid Aperiodic Attack & Laryngeal Cavitation

Scientific Literature:
- Fitch, W. T., Neubauer, J., & Herzel, H. (2002).
  "Calls out of chaos: the adaptive significance of nonlinear phenomena in mammalian vocal production."
  Animal Behaviour, 63(3), 407-418.
- Blumstein, D. T., Davitian, R., & Han, P. D. (2010).
  "Nonlinear sonics in movie soundtracks evoke fear: abnormal acoustic features arouse negative emotions."
  Biology Letters, 6(6), 810-813.
- Yeomans, J. S., & Frankland, P. W. (1995).
  "The acoustic startle reflex: neurons and pathways." Brain Research Reviews, 21(3), 301-314.

Upgraded Architecture:
Driven by an Aperiodic Derangement Permutation Engine to eliminate all periodicity.
Sequences through 6 distinct predatory behavioral assault modes:
0. AMBUSH_CHARGE: Accelerating heavy-mass predatory sprint thumps (40-80 Hz ground impact).
1. LARYNGEAL_TEAR: Piercing vocal-fold shredding at 700-1100 Hz with subharmonic biphonation.
2. SUB_CAVITATION: Massive 22-34 Hz infrasonic chest shockwave exciting the saccular vestibular pathway.
3. CHAOTIC_THROAT_SHEAR: Complete deterministic aerodynamic turbulence and mucosal ripping.
4. DECEPTIVE_STALK: Low-level guttural breathing designed to reset auditory sensory gating.
5. POINT_BLANK_ROAR: Instantaneous full-scale explosive acoustic strike with throat formants.
"""

import numpy as np
from scipy import signal
from typing import Optional
from .base_generator import BaseAudioGenerator
from .permutation_engine import AperiodicPermutationEngine

class ApexFelidRoarGenerator(BaseAudioGenerator):
    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="Model 6: Apex Felid Non-Linear Assault", seed=seed)
        self.perm_engine = AperiodicPermutationEngine(seed=self.seed)

    def generate(self, duration_seconds: float = 30.0) -> np.ndarray:
        n_samples = int(duration_seconds * self.sample_rate)
        t = np.linspace(0.0, duration_seconds, n_samples, endpoint=False)
        output = np.zeros(n_samples)

        # 6 distinct predatory behavioral threat modes
        modes = [
            "AMBUSH_CHARGE",
            "LARYNGEAL_TEAR",
            "SUB_CAVITATION",
            "CHAOTIC_THROAT_SHEAR",
            "DECEPTIVE_STALK",
            "POINT_BLANK_ROAR"
        ]

        # Calculate number of events needed to fill full duration
        num_events = int(duration_seconds / 1.1) + 40
        event_sequence = self.perm_engine.generate_non_repeating_sequence(modes, length=num_events)
        # Generate aperiodic event durations (0.7s to 2.4s) using golden-ratio scattering
        durations = self.perm_engine.get_aperiodic_intervals(len(event_sequence), min_val=0.7, max_val=2.4)

        current_time = 0.05
        for mode, dur in zip(event_sequence, durations):
            if current_time >= duration_seconds - 0.1:
                break

            start_idx = int(current_time * self.sample_rate)
            event_len = int(dur * self.sample_rate)
            end_idx = min(n_samples, start_idx + event_len)
            act_len = end_idx - start_idx

            if act_len <= 0:
                break

            t_ev = np.linspace(0.0, dur, act_len, endpoint=False)
            norm_t = t_ev / dur

            block = np.zeros(act_len)

            if mode == "AMBUSH_CHARGE":
                # Accelerating predatory footfall thumps (simulates 500lb apex predator sprinting toward listener)
                # Pacing accelerates from 3.5 Hz to 9.5 Hz
                accel_rate = np.linspace(3.5, 9.5, act_len)
                phase_thump = 2.0 * np.pi * np.cumsum(accel_rate / self.sample_rate)
                thump_triggers = np.sin(phase_thump) ** 16.0  # Sharp impacts
                thump_freq = self.rng.uniform(45.0, 75.0)
                thump_body = np.sin(2.0 * np.pi * thump_freq * t_ev) * np.exp(-((phase_thump % (2.0 * np.pi)) / 2.0))
                # Add ground-impact sub-rumble
                block = thump_body * thump_triggers * 2.8 + 0.3 * self.rng.standard_normal(act_len) * thump_triggers

            elif mode == "LARYNGEAL_TEAR":
                # High-frequency laryngeal snarl shredding (700-1100 Hz with subharmonic split)
                f0 = self.rng.uniform(750.0, 1150.0)
                phase_tear = 2.0 * np.pi * f0 * t_ev
                # Subharmonic biphonation f0/2 and f0/3
                wave_tear = (
                    np.sin(phase_tear) +
                    0.7 * np.sin(0.5 * phase_tear) +
                    0.5 * np.sin(0.333 * phase_tear) +
                    0.4 * np.sin(2.0 * phase_tear)
                )
                # Wave-folding distortion for agonizing harshness
                wave_folded = np.sin(wave_tear * 2.2)
                # Formant resonance at 3.2 kHz (ear-canal laceration)
                b_tear, a_tear = signal.iirpeak(3200.0, Q=8.0, fs=self.sample_rate)
                block = signal.lfilter(b_tear, a_tear, wave_folded) * 3.5

            elif mode == "SUB_CAVITATION":
                # Massive 22-34 Hz infrasonic cavitation exciting the saccular vestibular pathway
                f_cav = self.rng.uniform(22.0, 34.0)
                infra = np.sin(2.0 * np.pi * f_cav * t_ev)
                # Modulated guttural mucosal roar
                f_guttural = self.rng.uniform(60.0, 85.0)
                guttural = np.sign(np.sin(2.0 * np.pi * f_guttural * t_ev))
                # Formant filter F1 (450 Hz) and F2 (1150 Hz)
                b_c1, a_c1 = signal.iirpeak(480.0, Q=5.0, fs=self.sample_rate)
                b_c2, a_c2 = signal.iirpeak(1180.0, Q=7.0, fs=self.sample_rate)
                filtered_guttural = signal.lfilter(b_c1, a_c1, guttural) + 0.7 * signal.lfilter(b_c2, a_c2, guttural)
                block = (filtered_guttural * 2.2 + infra * 1.5) * (np.sin(np.pi * norm_t) ** 0.6)

            elif mode == "CHAOTIC_THROAT_SHEAR":
                # Deterministic aerodynamic chaos: vocal folds completely decoupled
                turbulent_noise = self.rng.standard_normal(act_len)
                b_turb, a_turb = signal.butter(2, [350.0, 4500.0], btype='bandpass', fs=self.sample_rate)
                turb_filt = signal.lfilter(b_turb, a_turb, turbulent_noise)
                # Chaotic amplitude chop (35-75 Hz roughness)
                chop_rate = self.rng.uniform(38.0, 68.0)
                chop = 0.5 + 0.5 * np.sign(np.sin(2.0 * np.pi * chop_rate * t_ev))
                block = turb_filt * chop * 3.0

            elif mode == "DECEPTIVE_STALK":
                # Eerie low-level guttural breathing & pacing rasp (resets sensory gating, preparing startle shock)
                breath_noise = self.rng.standard_normal(act_len)
                b_br, a_br = signal.butter(2, [1200.0, 3600.0], btype='bandpass', fs=self.sample_rate)
                breath_filt = signal.lfilter(b_br, a_br, breath_noise)
                growl_sub = np.sin(2.0 * np.pi * 42.0 * t_ev)
                block = (breath_filt * 0.18 + growl_sub * 0.15) * (0.6 + 0.4 * np.sin(2.0 * np.pi * 1.2 * t_ev))

            elif mode == "POINT_BLANK_ROAR":
                # Instantaneous full-scale acoustic hammer blow (0.5ms attack shock)
                f_roar = np.linspace(self.rng.uniform(140.0, 180.0), self.rng.uniform(50.0, 70.0), act_len)
                phase_roar = 2.0 * np.pi * np.cumsum(f_roar / self.sample_rate)
                raw_roar = np.sin(phase_roar) + 0.8 * np.sign(np.sin(2.0 * phase_roar)) + 0.6 * np.sin(0.5 * phase_roar)
                # Formants
                b_p1, a_p1 = signal.iirpeak(620.0, Q=6.0, fs=self.sample_rate)
                b_p2, a_p2 = signal.iirpeak(1450.0, Q=8.0, fs=self.sample_rate)
                b_p3, a_p3 = signal.iirpeak(2900.0, Q=10.0, fs=self.sample_rate)
                roar_shaped = (
                    0.5 * signal.lfilter(b_p1, a_p1, raw_roar) +
                    0.35 * signal.lfilter(b_p2, a_p2, raw_roar) +
                    0.35 * signal.lfilter(b_p3, a_p3, raw_roar)
                )
                # Hard exponential attack (shock impact)
                impact_env = np.exp(-norm_t * 1.8)
                impact_env[:int(0.002 * self.sample_rate)] = np.linspace(0.0, 1.0, int(0.002 * self.sample_rate))
                block = roar_shaped * impact_env * 4.2

            # Smooth block boundaries to avoid micro-clicks
            fade = min(int(0.004 * self.sample_rate), act_len // 4)
            if fade > 0:
                block[:fade] *= np.linspace(0.0, 1.0, fade)
                block[-fade:] *= np.linspace(1.0, 0.0, fade)

            output[start_idx:end_idx] += block
            current_time += dur

        # Saccular high-intensity low-frequency baseline tension
        t_base = np.linspace(0.0, duration_seconds, n_samples, endpoint=False)
        base_infra = np.sin(2.0 * np.pi * 28.0 * t_base) * 0.15
        output += base_infra

        # Extreme non-linear dynamic saturation (creates terrifying acoustic density)
        final_saturated = np.tanh(output * 2.2)
        return final_saturated
