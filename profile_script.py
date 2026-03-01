import time
import numpy as np
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate
from lamina.optimization import calculate_safety_factor, GeneticAlgorithm
from lamina.failure import FailureCriterion
from lamina.buckling import BucklingAnalysis

mat = CarbonEpoxy()
stack = [0, 45, -45, 90] * 10 # 40 plies
limits = {'xt': 1500e6, 'xc': 1500e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6}

# Laminate instantiation
t0 = time.time()
for _ in range(1000):
    lam = Laminate(mat, stack)
t1 = time.time()
print(f"Laminate instantiation: {t1-t0:.4f}s")

# Failure envelope
t0 = time.time()
for _ in range(100):
    FailureCriterion.tsai_wu(lam, limits, num_points=360)
t1 = time.time()
print(f"Failure tsai_wu: {t1-t0:.4f}s")

# Optimization calculate_safety_factor
load = {'Nx': 1000, 'Ny': 0, 'Nxy': 0}
t0 = time.time()
for _ in range(1000):
    calculate_safety_factor(lam, load, limits)
t1 = time.time()
print(f"calculate_safety_factor: {t1-t0:.4f}s")

# Polar stiffness
t0 = time.time()
for _ in range(1000):
    lam.polar_stiffness(step=1)
t1 = time.time()
print(f"polar_stiffness: {t1-t0:.4f}s")

# Genetic Algorithm
t0 = time.time()
ga = GeneticAlgorithm(mat, load, {'safety_factor': 1.5, 'limits': limits}, population_size=20, generations=20)
ga.optimize(min_plies=4, max_plies=20)
t1 = time.time()
print(f"Genetic Algorithm: {t1-t0:.4f}s")
