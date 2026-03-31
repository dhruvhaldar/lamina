import cProfile
import pstats
import numpy as np

def test_errstate_where_combined():
    A = np.random.rand(100)
    B = np.random.rand(100)
    C = np.random.rand(100)

    for _ in range(100000):
        with np.errstate(divide='ignore', invalid='ignore'):
            res = np.where(A > 0.5, B / A, C / A)

def test_errstate_where_combined_opt():
    A = np.random.rand(100)
    B = np.random.rand(100)
    C = np.random.rand(100)

    with np.errstate(divide='ignore', invalid='ignore'):
        for _ in range(100000):
            res = np.where(A > 0.5, B / A, C / A)

cProfile.run('test_errstate_where_combined()', 'stats1')
p1 = pstats.Stats('stats1')
print("errstate inside loop:")
p1.sort_stats('tottime').print_stats(15)

cProfile.run('test_errstate_where_combined_opt()', 'stats2')
p2 = pstats.Stats('stats2')
print("errstate outside loop:")
p2.sort_stats('tottime').print_stats(15)
