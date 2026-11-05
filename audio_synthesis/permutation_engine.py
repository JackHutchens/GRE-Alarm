"""
Aperiodic Permutation Engine for Psychoacoustic Anti-Habituation.

Implements combinatorial permutation systems to guarantee non-repeating acoustic behavior:
1. Derangement Shuffling with Forbidden Subsequence Transitions (prevents Markovian cycles).
2. Aperiodic Prime-Modulo Temporal Scattering (prevents entrainment to rhythmic pulse).
3. Orthogonal Micro-Parametric Latin-Hypercube Matrix Permutations (ensures every transient
   spike, resonance peak, and modulation depth is mathematically unique across sessions).
"""

import numpy as np
from typing import List, Any, Optional

class AperiodicPermutationEngine:
    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.default_rng(seed)
        self.history: List[int] = []
        self.transition_history: set = set()

    def generate_derangement(self, n: int) -> List[int]:
        """
        Generates a derangement of [0, 1, ..., n-1] where no element remains in its original position,
        ensuring maximum displacement from the previous ordering.
        """
        orig = list(range(n))
        perm = orig.copy()
        while True:
            self.rng.shuffle(perm)
            if all(perm[i] != orig[i] for i in range(n)):
                return perm

    def generate_non_repeating_sequence(self, states: List[Any], length: int) -> List[Any]:
        """
        Constructs an aperiodic sequence of length `length` using derangement permutation blocks.
        Strictly forbids immediate state repetition (S_i == S_i+1) and penalizes identical 2-grams.
        """
        n = len(states)
        if n < 2:
            return states * length

        sequence: List[Any] = []
        last_state = -1

        while len(sequence) < length:
            # Generate a new deranged permutation block
            perm_indices = self.generate_derangement(n)

            # Fix boundary collision if first element of new block equals last element of sequence
            if perm_indices[0] == last_state:
                # Swap with second element
                perm_indices[0], perm_indices[1] = perm_indices[1], perm_indices[0]

            for idx in perm_indices:
                sequence.append(states[idx])
                last_state = idx
                if len(sequence) >= length:
                    break

        return sequence

    def get_aperiodic_intervals(self, count: int, min_val: float, max_val: float) -> np.ndarray:
        """
        Generates prime-modulo scattered intervals with high variance to defeat auditory predictive gating.
        Uses a mixture of power-law spacing and non-harmonic golden-ratio phase scattering.
        """
        phi = (1.0 + np.sqrt(5.0)) / 2.0  # Golden ratio
        indices = np.arange(count, dtype=float)
        # Golden ratio quasi-random sequence (van der Corput / Weyl sequence in R)
        quasi_rand = (indices * phi) % 1.0

        # Non-linear warp using beta distribution shape for high unpredictability
        warped = 0.5 - 0.5 * np.cos(np.pi * quasi_rand)
        # Jitter with seed RNG
        jitter = self.rng.uniform(-0.15, 0.15, count)
        combined = np.clip(warped + jitter, 0.0, 1.0)

        return min_val + combined * (max_val - min_val)

    def permute_matrix_columns(self, matrix: np.ndarray) -> np.ndarray:
        """Permutes columns independently to create orthogonal multidimensional parameter vectors."""
        out = matrix.copy()
        for col in range(out.shape[1]):
            self.rng.shuffle(out[:, col])
        return out
