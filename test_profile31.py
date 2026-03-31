import cProfile
import pstats
import numpy as np

def test_scalar_opt_v2():
    ABD_inv = np.random.rand(6, 6)
    Nx = 1000.0
    Ny = 0.0
    Nxy = 0.0

    for _ in range(100000):
        strain_curv = np.empty(6)
        strain_curv[:] = ABD_inv[:, 0] * Nx
        strain_curv[:] += ABD_inv[:, 1] * Ny
        strain_curv[:] += ABD_inv[:, 2] * Nxy

cProfile.run('test_scalar_opt_v2()', 'stats')
p = pstats.Stats('stats')
print("Optimized approach (in-place):")
p.sort_stats('tottime').print_stats(15)
