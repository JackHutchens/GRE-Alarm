from .base_generator import BaseAudioGenerator
from .model1_amygdala_roughness import AmygdalaRoughnessGenerator
from .model2_stick_slip_friction import StickSlipFrictionGenerator
from .model3_plomp_levelt_dissonance import PlompLeveltSwarmGenerator
from .model4_stochastic_mmn import StochasticMMNDisruptionGenerator
from .model5_hyperbolic_looming import HyperbolicLoomingGenerator
from .model6_apex_felid_roar import ApexFelidRoarGenerator
from .model7_serpentine_stridulation import SerpentineStridulationGenerator

MODELS = {
    "model1": AmygdalaRoughnessGenerator,
    "model2": StickSlipFrictionGenerator,
    "model3": PlompLeveltSwarmGenerator,
    "model4": StochasticMMNDisruptionGenerator,
    "model5": HyperbolicLoomingGenerator,
    "model6": ApexFelidRoarGenerator,
    "model7": SerpentineStridulationGenerator,
}

__all__ = [
    "BaseAudioGenerator",
    "AmygdalaRoughnessGenerator",
    "StickSlipFrictionGenerator",
    "PlompLeveltSwarmGenerator",
    "StochasticMMNDisruptionGenerator",
    "HyperbolicLoomingGenerator",
    "ApexFelidRoarGenerator",
    "SerpentineStridulationGenerator",
    "MODELS"
]
