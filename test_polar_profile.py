import cProfile
import pstats
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate

mat = CarbonEpoxy()
stack = [0, 45, -45, 90] * 10
lam = Laminate(mat, stack)

def run_work():
    for _ in range(1000):
        lam.polar_stiffness(step=1)

cProfile.run('run_work()', 'stats')
p = pstats.Stats('stats')
p.sort_stats('time').print_stats(20)
