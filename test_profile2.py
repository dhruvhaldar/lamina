import cProfile
import pstats
import numpy as np
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate
from lamina.optimization import calculate_safety_factor

mat = CarbonEpoxy()
stack = [0, 45, -45, 90] * 10
limits = {'xt': 1500e6, 'xc': 1500e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6}
load = {'Nx': 1000, 'Ny': 0, 'Nxy': 0}

lam = Laminate(mat, stack)

def run_work():
    for _ in range(1000):
        calculate_safety_factor(lam, load, limits)

cProfile.run('run_work()', 'stats')
p = pstats.Stats('stats')
p.sort_stats('time').print_stats(20)
