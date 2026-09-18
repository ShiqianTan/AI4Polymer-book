"""Test bootstrap: put the package on sys.path and expose default scenario inputs."""
import sys
from pathlib import Path

CALCULATIONS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CALCULATIONS / "src"))

from ai4polymer_calc.schema import REQUIRED_KEYS, validate_result  # noqa: E402
from ai4polymer_calc.topics import TOPIC_MODULES  # noqa: E402

DEFAULT_INPUTS = {
    "descriptor-budget": dict(representation="morgan", n_bits=2048, radius=2, atoms=100,
                              bonds=105, library_size=1_000_000),
    "chemical-space": dict(monomers=10, chain_length=100, copolymer="random", stoichiometry="1,1"),
    "md-cost": dict(atoms=5000, timesteps=1_000_000, timestep_fs=1.0, method="md-mlff",
                    device_id="a100-80gb-sxm", efficiency=0.3, gpus=1),
    "gnn-forward": dict(layers=4, hidden=256, atoms=100, bonds=105, edge_features=32, heads=8,
                        readout="attention", device_id="a100-80gb-sxm", efficiency=0.3),
    "learning-curve": dict(mae_inf=0.05, a=1.0, alpha=0.5, target_mae=0.2, n_max=100_000,
                           strict_mae=0.1),
    "closed-loop": dict(space_size=1_000_000, top_fraction=0.001, bo_speedup=5.0,
                        experiments_per_day=50),
    "pareto-screen": dict(monomers=10, chain_length=100, reference=(0.0, 0.0),
                          weight_steps=11, epsilon_steps=21),
    "robust-ranking": dict(means=(205.0, 205.0), half_widths=(20.0, 3.0),
                           spec_low=200.0, spec_high=210.0),
    "polymerization": dict(step_conversions="0.9,0.99,0.999", living_ratios="50,100,200",
                           living_conversion=0.99,
                           copolymer_pairs="0.1:0.1;1:1;10:0.1;0.1:10",
                           feed_fraction=0.5, max_conversion=0.99, drift_steps=100,
                           flory_conversion=0.99, poisson_mean_dp=100, curve_points=80),
    "synthesis-route": dict(branching=50, depth=5, beam=10, step_yield=0.8,
                            target_yield=0.3, initial_candidates=8910, feasibility=0.6,
                            route_length_pass=0.6, yield_pass=0.5, cost_pass=0.4),
    "bo-variants": dict(space_size=1_000_000, top_fraction=0.001, batch_size=8,
                        batch_correlation=0.5, feasible_fraction=0.3,
                        fidelity_cost_ratio=0.05, screening_pass_fraction=0.2,
                        expensive_cost_ratio=20.0, budget=1000),
}


def calculate_all():
    return {name: module.calculate(**DEFAULT_INPUTS[name]) for name, module in TOPIC_MODULES.items()}
