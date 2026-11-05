"""
Model 7 (V2 - Upgraded): Serpentine Venom-Stridulation & Supersonic Ambush Strike

Scientific Literature:
- Öhman, A., & Mineka, S. (2001).
  "Fears, phobias, and preparedness: Toward an evolved module of fear and fear learning."
  Psychological Review, 108(3), 483-522.
- Young, B. A. (2003).
  "Snake bioacoustics: toward a richer understanding of the behavioral ecology of snakes."
  Quarterly Review of Biology, 78(3), 303-325.
- Isbell, L. A. (2006).
  "Snakes as agents of evolutionary change in primate brain and behavior."
  Journal of Human Evolution, 51(1), 1-35.
- Yeomans, J. S., & Frankland, P. W. (1995).
  "The acoustic startle reflex: neurons and pathways." Brain Research Reviews.

Upgraded Architecture:
Driven by an Aperiodic Derangement Permutation Engine to eliminate all predictable cadence.
Sequences through 5 terrifying reptilian assault regimes:
0. SUPERSONIC_STRIKE_CRACK: 0.2ms full-amplitude whip-crack strike snap (8.5 kHz -> 400 Hz collapse).
1. DUAL_VIPER_CROSS_STRIDULATION: Desynchronized serrated keeled-scale rasping at 37 Hz & 53 Hz.
2. SUFFOCATING_GLOTTAL_HISS: High-pressure pulmonary expulsion with agitated throat formants (5.5 kHz).
3. SCALE_MICRO_FRACTURE_RATTLE: Chaotic dry-bone acoustic rattling with extreme temporal jitter.
4. COILED_SUSPENSE_FEINT: Eerie micro-flick tongue clicks and near-silence to reset the startle reflex.
"""

import numpy as np
from scipy import signal
from typing import Optional
from .base_generator import BaseAudioGenerator
from .permutation_engine import AperiodicPermutationEngine

class SerpentineStridulationGenerator(BaseAudioGenerator):
    def __init__(self, seed: Optional[int] = None):
        super().__init__(name="Model 7: Serpentine Venom Assault", seed=seed)
        self.perm_engine = AperiodicPermutationEngine(seed=self.seed)

    def generate(self, duration_seconds: float = 30.0) -> np.ndarray:
        n_samples = int(duration_seconds * self.sample_rate)
        t = np.linspace(0.0, duration_seconds, n_samples, endpoint=False)
        output = np.zeros(n_samples)

        # 5 distinct reptilian threat states
        states = [
            "SUPERSONIC_STRIKE_CRACK",
            "DUAL_VIPER_CROSS_STRIDULATION",
            "SUFFOCATING_GLOTTAL_HISS",
            "SCALE_MICRO_FRACTURE_RATTLE",
            "COILED_SUSPENSE_FEINT"
        ]

        # Calculate number of states needed to fill full duration
        num_states = int(duration_seconds / 0.9) + 40
        state_sequence = self.perm_engine.generate_non_repeating_sequence(states, length=num_states)
        # Aperiodic state durations using golden-ratio scattering
        durations = self.perm_engine.get_aperiodic_intervals(len(state_sequence), min_val=0.5, max_val=2.1)

        current_time = 0.05
        for state, dur in zip(state_sequence, durations):
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

            if state == "SUPERSONIC_STRIKE_CRACK":
                # Instantaneous full-scale supersonic whip-crack strike snap
                # 0.2ms attack time, 8,500 Hz crashing to 400 Hz
                snap_len = min(int(0.045 * self.sample_rate), act_len)
                t_snap = np.linspace(0.0, 0.045, snap_len, endpoint=False)
                # Exponential frequency collapse
                f_snap = 8800.0 * np.exp(-t_snap * 110.0) + 450.0
                phase_snap = 2.0 * np.pi * np.cumsum(f_snap / self.sample_rate)
                # Whip-crack shock envelope: instant attack, violent 15ms decay
                env_snap = np.exp(-t_snap * 85.0)
                crack = (np.sin(phase_snap) + 0.8 * np.sign(np.sin(2.0 * phase_snap))) * env_snap * 4.5
                block[:snap_len] += crack
                # Trailing venom hiss
                tail_noise = self.rng.standard_normal(act_len)
                b_tail, a_tail = signal.butter(2, [4000.0, 8500.0], btype='bandpass', fs=self.sample_rate)
                block += signal.lfilter(b_tail, a_tail, tail_noise) * np.exp(-norm_t * 3.0) * 1.5

            elif state == "DUAL_VIPER_CROSS_STRIDULATION":
                # Desynchronized dual-viper scale-on-scale stridulation (37 Hz & 53 Hz clash)
                rate1 = self.rng.uniform(34.0, 42.0)
                rate2 = self.rng.uniform(50.0, 62.0)
                # Non-linear saw-tooth scale scrape pulses
                p1 = ((2.0 * np.pi * rate1 * t_ev) % (2.0 * np.pi)) ** 3.5
                p2 = ((2.0 * np.pi * rate2 * t_ev) % (2.0 * np.pi)) ** 3.5
                # Abrasive high-frequency friction noise (3.8 kHz to 8.2 kHz)
                fric_noise = self.rng.standard_normal(act_len)
                b_fric, a_fric = signal.butter(3, [3600.0, 8200.0], btype='bandpass', fs=self.sample_rate)
                fric_filtered = signal.lfilter(b_fric, a_fric, fric_noise)
                block = fric_filtered * (0.6 * p1 + 0.5 * p2) * 3.2

            elif state == "SUFFOCATING_GLOTTAL_HISS":
                # High-velocity pulmonary air expulsion through an obstructed glottis (King Cobra threat)
                hiss_raw = self.rng.standard_normal(act_len)
                # Throat resonance at 5.2 kHz with secondary peak at 7.1 kHz
                b_h1, a_h1 = signal.iirpeak(5200.0, Q=6.0, fs=self.sample_rate)
                b_h2, a_h2 = signal.iirpeak(7100.0, Q=8.0, fs=self.sample_rate)
                hiss_res = signal.lfilter(b_h1, a_h1, hiss_raw) + 0.6 * signal.lfilter(b_h2, a_h2, hiss_raw)
                # Violent respiratory swell envelope
                swell = np.sin(np.pi * norm_t) ** 1.4
                tremolo = 0.7 + 0.3 * np.sin(2.0 * np.pi * self.rng.uniform(18.0, 32.0) * t_ev)
                block = hiss_res * swell * tremolo * 4.0

            elif state == "SCALE_MICRO_FRACTURE_RATTLE":
                # Chaotic, irregular bone/keratin rattle burst with high temporal jitter
                base_rattle = self.rng.uniform(42.0, 58.0)
                jitter_rattle = base_rattle + 20.0 * np.sin(2.0 * np.pi * 7.5 * t_ev)
                phase_r = 2.0 * np.pi * np.cumsum(jitter_rattle / self.sample_rate)
                rattle_clicks = (np.sin(phase_r) > 0.85).astype(float)
                # Abrasive click impulse filter
                click_noise = self.rng.standard_normal(act_len) * rattle_clicks
                b_clk, a_clk = signal.butter(2, [2800.0, 7500.0], btype='bandpass', fs=self.sample_rate)
                block = signal.lfilter(b_clk, a_clk, click_noise) * 4.0

            elif state == "COILED_SUSPENSE_FEINT":
                # Eerie micro-flick tongue clicks and quiet tense breathing (resets sensory gating for startle)
                flick_rate = self.rng.uniform(6.0, 12.0)
                flick_phase = 2.0 * np.pi * flick_rate * t_ev
                flick_pulses = (np.sin(flick_phase) > 0.96).astype(float)
                flick_sound = np.sin(2.0 * np.pi * 3200.0 * t_ev) * flick_pulses * 0.4
                whisper_noise = self.rng.standard_normal(act_len)
                b_wh, a_wh = signal.butter(2, [1800.0, 4500.0], btype='bandpass', fs=self.sample_rate)
                block = flick_sound + signal.lfilter(b_wh, a_wh, whisper_noise) * 0.12

            # Smooth block boundaries
            fade = min(int(0.003 * self.sample_rate), act_len // 4)
            if fade > 0:
                block[:fade] *= np.linspace(0.0, 1.0, fade)
                block[-fade:] *= np.linspace(1.0, 0.0, fade)

            output[start_idx:end_idx] += block
            current_time += dur

        # Asymmetric non-linear clipping to produce sharp ear-canal overload on sudden strike snaps
        saturated = np.tanh(output * 2.4)
        return saturated
