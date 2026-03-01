import cProfile
import pstats
import numpy as np
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate
from lamina.optimization import calculate_safety_factor, GeneticAlgorithm
from lamina.failure import FailureCriterion
from lamina.buckling import BucklingAnalysis

mat = CarbonEpoxy()
stack = [0, 45, -45, 90] * 10
limits = {'xt': 1500e6, 'xc': 1500e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6}

def run_work():
    lam = Laminate(mat, stack)
    for _ in range(100):
        FailureCriterion.tsai_wu(lam, limits, num_points=360)

    load = {'Nx': 1000, 'Ny': 0, 'Nxy': 0}
    for _ in range(1000):
        calculate_safety_factor(lam, load, limits)

    for _ in range(1000):
        lam.polar_stiffness(step=1)

cProfile.run('run_work()', 'stats')
p = pstats.Stats('stats')
p.sort_stats('cumulative').print_stats(20)
p.sort_stats('time').print_stats(20)
