import cProfile
import pstats
import numpy as np
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate

mat = CarbonEpoxy()
stack = [0, 45, -45, 90] * 10

def run_work():
    for _ in range(5000):
        Laminate(mat, stack)

cProfile.run('run_work()', 'stats')
p = pstats.Stats('stats')
p.sort_stats('time').print_stats(20)
