import cProfile
import numpy as np

Q_bars = np.random.rand(3, 3, 40)
h = np.random.rand(40)
h2 = np.random.rand(40)
h3 = np.random.rand(40)

def orig():
    for _ in range(5000):
        A = (Q_bars.reshape(9, -1) @ h).reshape(3, 3)
        B = 0.5 * (Q_bars.reshape(9, -1) @ h2).reshape(3, 3)
        D = (1/3) * (Q_bars.reshape(9, -1) @ h3).reshape(3, 3)

def new2():
    for _ in range(5000):
        H = np.vstack([h, 0.5*h2, (1/3)*h3]).T # 40x3
        ABD = Q_bars.reshape(9, -1) @ H # 9x3
        # A is ABD[:, 0].reshape(3, 3)
        # B is ABD[:, 1].reshape(3, 3)
        # D is ABD[:, 2].reshape(3, 3)

cProfile.run('orig()', 'stats1')
cProfile.run('new2()', 'stats2')
import pstats
print("Orig")
pstats.Stats('stats1').sort_stats('time').print_stats(10)
print("New2")
pstats.Stats('stats2').sort_stats('time').print_stats(10)
