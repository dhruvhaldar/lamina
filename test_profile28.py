import cProfile
import pstats
import numpy as np

def test_abd_matrix():
    Q_bars_flat = np.random.rand(9, 100)
    h = np.random.rand(100)
    h2 = np.random.rand(100)
    h3 = np.random.rand(100)

    for _ in range(100000):
        A = np.dot(Q_bars_flat, h).reshape(3, 3)
        B = 0.5 * np.dot(Q_bars_flat, h2).reshape(3, 3)
        D = (1/3) * np.dot(Q_bars_flat, h3).reshape(3, 3)

        ABD = np.empty((6, 6))
        ABD[:3, :3] = A
        ABD[:3, 3:] = B
        ABD[3:, :3] = B
        ABD[3:, 3:] = D

def test_abd_matrix_optimized():
    Q_bars_flat = np.random.rand(9, 100)
    h = np.random.rand(100)
    h2 = np.random.rand(100)
    h3 = np.random.rand(100)

    for _ in range(100000):
        ABD = np.empty((6, 6))
        A = ABD[:3, :3] = np.dot(Q_bars_flat, h).reshape(3, 3)
        B = ABD[:3, 3:] = ABD[3:, :3] = 0.5 * np.dot(Q_bars_flat, h2).reshape(3, 3)
        D = ABD[3:, 3:] = (1/3) * np.dot(Q_bars_flat, h3).reshape(3, 3)

cProfile.run('test_abd_matrix()', 'stats1')
p1 = pstats.Stats('stats1')
print("Current approach:")
p1.sort_stats('tottime').print_stats(15)

cProfile.run('test_abd_matrix_optimized()', 'stats2')
p2 = pstats.Stats('stats2')
print("Optimized approach:")
p2.sort_stats('tottime').print_stats(15)
