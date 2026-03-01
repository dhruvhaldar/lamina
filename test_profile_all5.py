import cProfile
import numpy as np

angles = np.array([0, 45, -45, 90] * 10)

def orig():
    for _ in range(5000):
        rads = np.radians(angles)
        c = np.cos(rads)
        s = np.sin(rads)

def new1():
    for _ in range(5000):
        # We can precompute radians, but Laminate accepts angles which can be anything
        rads = angles * (np.pi / 180.0)
        c = np.cos(rads)
        s = np.sin(rads)

cProfile.run('orig()', 'stats1')
cProfile.run('new1()', 'stats2')
import pstats
print("Orig")
pstats.Stats('stats1').sort_stats('time').print_stats(10)
print("New1")
pstats.Stats('stats2').sort_stats('time').print_stats(10)
