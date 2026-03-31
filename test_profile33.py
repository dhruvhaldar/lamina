import cProfile
import pstats
import numpy as np
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate
from lamina.optimization import calculate_safety_factor

material = CarbonEpoxy()
lam = Laminate(material, stack=[0, 45, -45, 90, 90, -45, 45, 0], symmetry=True)
load = {'Nx': 1000, 'Ny': 0, 'Nxy': 0}
limits = {'xt': 1500e6, 'xc': 1200e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6}

def test_opt_loop():
    for _ in range(10000):
        calculate_safety_factor(lam, load, limits)

cProfile.run('test_opt_loop()', 'stats')
p = pstats.Stats('stats')
p.sort_stats('tottime').print_stats(15)
