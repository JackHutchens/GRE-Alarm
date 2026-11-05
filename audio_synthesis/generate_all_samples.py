"""
Script to generate 30-second test clips for all 5 Psychoacoustic Aversive Alarm Models.
Outputs to audio_samples/ and copies to the artifact directory for interactive browser auditioning.
"""

import os
import sys
import shutil
import json

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
from audio_synthesis import (
    AmygdalaRoughnessGenerator,
    StickSlipFrictionGenerator,
    PlompLeveltSwarmGenerator,
    StochasticMMNDisruptionGenerator,
    HyperbolicLoomingGenerator,
    ApexFelidRoarGenerator,
    SerpentineStridulationGenerator
)

ARTIFACT_DIR = r"C:\Users\jacka\.gemini\antigravity\brain\ae759fcb-adde-4ada-a1a8-c7f9b73b75ae"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "audio_samples")

def generate_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    generators = [
        (
            "model1_amygdala_roughness.wav",
            AmygdalaRoughnessGenerator(seed=42069),
            "Model 1: Amygdala Roughness Harvester",
            "Human scream roughness modulation (30-130 Hz) targeting subcortical amygdalar threat circuits."
        ),
        (
            "model2_stick_slip_friction.wav",
            StickSlipFrictionGenerator(seed=1337),
            "Model 2: Frictional Stick-Slip Screech",
            "Chalkboard / metal-on-glass stick-slip modeling with sharp spectral kurtosis in 2.8-4.5 kHz."
        ),
        (
            "model3_plomp_levelt_dissonance.wav",
            PlompLeveltSwarmGenerator(seed=80085),
            "Model 3: Plomp-Levelt Dissonance Swarm",
            "Basilar membrane critical band clash (0.25*CBW) with tritone diabolus dyads and Shepard vertigo."
        ),
        (
            "model4_stochastic_mmn_disruption.wav",
            StochasticMMNDisruptionGenerator(seed=99999),
            "Model 4: Stochastic MMN Disruption Engine",
            "Predictive coding destroyer: Poisson pauses, Levy pitch jumps across 5 octaves, zero habituation."
        ),
        (
            "model5_hyperbolic_looming.wav",
            HyperbolicLoomingGenerator(seed=77711),
            "Model 5: Hyperbolic Auditory Looming",
            "Exponential looming crash acceleration with 8.5 Hz infrasonic vestibular intermodulation."
        ),
        (
            "model6_apex_felid_roar.wav",
            ApexFelidRoarGenerator(seed=66601),
            "Model 6: Apex Felid Non-Linear Roar",
            "Non-linear laryngeal cavitation, biphonic subharmonics (f0/2), and chest resonance panic."
        ),
        (
            "model7_serpentine_stridulation.wav",
            SerpentineStridulationGenerator(seed=88802),
            "Model 7: Serpentine Venom-Stridulation",
            "Phylogenetically prepared threat: 35-50 Hz scale rattle, glottal hiss, and sudden ambush strikes."
        )
    ]

    results = []
    print("=" * 70)
    print("GENERATING 30-SECOND PSYCHOACOUSTIC ALARM AUDIO CLIPS")
    print("=" * 70)

    for filename, gen, title, desc in generators:
        local_path = os.path.join(OUTPUT_DIR, filename)
        artifact_path = os.path.join(ARTIFACT_DIR, filename)

        gen.export_wav(local_path, duration_seconds=30.0)

        # Copy to artifact directory for HTML embedding
        shutil.copyfile(local_path, artifact_path)

        file_size_mb = os.path.getsize(local_path) / (1024 * 1024)
        results.append({
            "filename": filename,
            "title": title,
            "description": desc,
            "seed": gen.seed,
            "duration_seconds": 30.0,
            "size_mb": round(file_size_mb, 2),
            "local_path": local_path,
            "artifact_path": artifact_path
        })
        print(f"Generated {filename} -> Size: {file_size_mb:.2f} MB")

    # Save metadata JSON in audio_samples
    meta_path = os.path.join(OUTPUT_DIR, "models_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    print("ALL 5 AUDIO CLIPS SUCCESSFULLY GENERATED AND EXPORTED")
    print("=" * 70)
    return results

if __name__ == "__main__":
    generate_all()
