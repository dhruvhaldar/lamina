import cProfile
import pstats
import numpy as np

def test_errstate_overhead():
    A = np.random.rand(100)
    for _ in range(100000):
        with np.errstate(divide='ignore', invalid='ignore'):
            pass

def test_no_errstate_overhead():
    A = np.random.rand(100)
    for _ in range(100000):
        pass

cProfile.run('test_errstate_overhead()', 'stats1')
p1 = pstats.Stats('stats1')
print("errstate:")
p1.sort_stats('tottime').print_stats(15)

cProfile.run('test_no_errstate_overhead()', 'stats2')
p2 = pstats.Stats('stats2')
print("no errstate:")
p2.sort_stats('tottime').print_stats(15)
