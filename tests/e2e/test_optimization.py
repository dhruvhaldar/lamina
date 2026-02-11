import pytest
from lamina.materials import CarbonEpoxy
from lamina.optimization import GeneticAlgorithm, calculate_safety_factor
from lamina.clt import Laminate

def test_stacking_optimization():
    mat = CarbonEpoxy()
    # Moderate load
    load = {'Nx': 100e3, 'Ny': 0, 'Nxy': 0} # 100 kN/m

    # 100 kN/m on 4 plies (0.5mm) => 200 MPa approx.
    # Strength is 1500 MPa. SF should be huge.
    # Let's increase load to make it challenging.
    # 1000 kN/m => 2000 MPa > 1500. So 4 plies fail.
    # Needs more plies.

    load = {'Nx': 1000e3, 'Ny': 0, 'Nxy': 0}

    constraints = {
        'safety_factor': 1.2,
        'limits': {'xt': 1500e6, 'xc': 1200e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6}
    }

    # Run optimization with small pop for speed
    ga = GeneticAlgorithm(mat, load, constraints, population_size=10, generations=5)
    best_stack = ga.optimize(min_plies=4, max_plies=32)

    assert best_stack is not None
    assert len(best_stack) >= 4

    # Verify the result satisfies constraints
    lam = Laminate(mat, best_stack, symmetry=False)
    sf = calculate_safety_factor(lam, load, constraints['limits'])

    print(f"Best stack: {best_stack}, SF: {sf}")
    assert sf >= 1.2
