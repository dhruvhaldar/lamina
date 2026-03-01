import cProfile
import numpy as np
from lamina.materials import CarbonEpoxy

mat = CarbonEpoxy()
angles = np.array([0, 45, -45, 90] * 10)
rads = np.radians(angles)
c = np.cos(rads)
s = np.sin(rads)

def _get_Q_bar_from_trig_old(c, s):
    U1, U2, U3, U4, U5 = mat.invariants

    c2 = c*c
    s2 = s*s

    cos2 = c2 - s2
    sin2 = 2 * c * s

    cos2_sq = cos2*cos2
    sin2_sq = sin2*sin2

    cos4 = cos2_sq - sin2_sq
    sin4 = 2 * cos2 * sin2

    Q_bar_11 = U1 + U2*cos2 + U3*cos4
    Q_bar_12 = U4 - U3*cos4
    Q_bar_22 = U1 - U2*cos2 + U3*cos4
    Q_bar_16 = 0.5*U2*sin2 + U3*sin4
    Q_bar_26 = 0.5*U2*sin2 - U3*sin4
    Q_bar_66 = U5 - U3*cos4

    return np.array([
        [Q_bar_11, Q_bar_12, Q_bar_16],
        [Q_bar_12, Q_bar_22, Q_bar_26],
        [Q_bar_16, Q_bar_26, Q_bar_66]
    ])

def run_old():
    for _ in range(5000):
        _get_Q_bar_from_trig_old(c, s)

def _get_Q_bar_from_trig_new(c, s):
    U1, U2, U3, U4, U5 = mat.invariants

    c2 = c*c
    s2 = s*s

    cos2 = c2 - s2
    sin2 = 2 * c * s

    cos2_sq = cos2*cos2
    sin2_sq = sin2*sin2

    cos4 = cos2_sq - sin2_sq
    sin4 = 2 * cos2 * sin2

    U2_cos2 = U2 * cos2
    U3_cos4 = U3 * cos4
    half_U2_sin2 = 0.5 * U2 * sin2
    U3_sin4 = U3 * sin4

    res = np.empty((3, 3, len(c)))
    res[0, 0] = U1 + U2_cos2 + U3_cos4
    res[0, 1] = res[1, 0] = U4 - U3_cos4
    res[1, 1] = U1 - U2_cos2 + U3_cos4
    res[0, 2] = res[2, 0] = half_U2_sin2 + U3_sin4
    res[1, 2] = res[2, 1] = half_U2_sin2 - U3_sin4
    res[2, 2] = U5 - U3_cos4
    return res

def run_new():
    for _ in range(5000):
        _get_Q_bar_from_trig_new(c, s)

cProfile.run('run_old()', 'stats_old')
cProfile.run('run_new()', 'stats_new')
import pstats
print("Old:")
pstats.Stats('stats_old').sort_stats('time').print_stats(10)
print("New:")
pstats.Stats('stats_new').sort_stats('time').print_stats(10)
