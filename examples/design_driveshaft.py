import numpy as np
from lamina.materials import CarbonEpoxy
from lamina.optimization import GeneticAlgorithm
from lamina.clt import Laminate

def design_driveshaft():
    mat = CarbonEpoxy()

    # Load: Pure Torsion
    R = 0.05 # 50mm radius
    T = 2000 # Nm
    # Shear flow q = T / (2 A_m) for thin walled
    # q = T / (2 * pi * R^2)
    # Nxy = q
    Nxy = T / (2 * np.pi * R**2)
    print(f"Applied Shear Load Nxy: {Nxy:.2f} N/m")

    load = {'Nx': 0, 'Ny': 0, 'Nxy': Nxy}

    constraints = {
        'safety_factor': 2.0,
        'limits': {'xt': 1500e6, 'xc': 1200e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6}
    }

    # Optimize
    print("Running Genetic Algorithm...")
    ga = GeneticAlgorithm(mat, load, constraints, population_size=20, generations=10)
    best_stack = ga.optimize(min_plies=4, max_plies=16)

    if best_stack:
        print(f"Optimal Stacking Sequence: {best_stack}")
        lam = Laminate(mat, best_stack, symmetry=False)
        print(f"Total Thickness: {lam.total_thickness * 1000} mm")
    else:
        print("No solution found.")

if __name__ == "__main__":
    design_driveshaft()
