import cProfile
import pstats
import numpy as np

def test_matmul_vs_scalar():
    ABD_inv = np.random.rand(6, 6)
    Nx = 1000.0
    Ny = 0.0
    Nxy = 0.0

    for _ in range(100000):
        NM_reduced = np.array([Nx, Ny, Nxy])
        strain_curv = ABD_inv[:, :3] @ NM_reduced

def test_scalar_opt():
    ABD_inv = np.random.rand(6, 6)
    Nx = 1000.0
    Ny = 0.0
    Nxy = 0.0

    for _ in range(100000):
        strain_curv = ABD_inv[:, 0] * Nx + ABD_inv[:, 1] * Ny + ABD_inv[:, 2] * Nxy

cProfile.run('test_matmul_vs_scalar()', 'stats1')
p1 = pstats.Stats('stats1')
print("Current approach (np.array + @):")
p1.sort_stats('tottime').print_stats(15)

cProfile.run('test_scalar_opt()', 'stats2')
p2 = pstats.Stats('stats2')
print("Optimized approach (scalar mult):")
p2.sort_stats('tottime').print_stats(15)
