import cProfile
import pstats
import numpy as np

def test_matmul_vs_dot():
    ABD_inv = np.random.rand(6, 6)
    Nx = 1000.0
    Ny = 0.0
    Nxy = 0.0

    for _ in range(100000):
        NM_reduced = np.array([Nx, Ny, Nxy])
        strain_curv = ABD_inv[:, :3] @ NM_reduced

def test_dot_opt():
    ABD_inv = np.random.rand(6, 6)
    Nx = 1000.0
    Ny = 0.0
    Nxy = 0.0

    for _ in range(100000):
        NM_reduced = np.array([Nx, Ny, Nxy])
        strain_curv = np.dot(ABD_inv[:, :3], NM_reduced)

cProfile.run('test_matmul_vs_dot()', 'stats1')
p1 = pstats.Stats('stats1')
print("Current approach (np.array + @):")
p1.sort_stats('tottime').print_stats(15)

cProfile.run('test_dot_opt()', 'stats2')
p2 = pstats.Stats('stats2')
print("Optimized approach (np.array + np.dot):")
p2.sort_stats('tottime').print_stats(15)
