import cProfile
import numpy as np

c = np.random.rand(40)
s = np.random.rand(40)
U1, U2, U3, U4, U5 = np.random.rand(5)

def qbar1():
    for _ in range(5000):
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
        res = np.array([
            [Q_bar_11, Q_bar_12, Q_bar_16],
            [Q_bar_12, Q_bar_22, Q_bar_26],
            [Q_bar_16, Q_bar_26, Q_bar_66]
        ])

def qbar3():
    n_plies = len(c)
    for _ in range(5000):
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

        # Preallocate memory
        res = np.empty((3, 3, n_plies))
        res[0, 0] = U1 + U2_cos2 + U3_cos4
        res[0, 1] = res[1, 0] = U4 - U3_cos4
        res[1, 1] = U1 - U2_cos2 + U3_cos4
        res[0, 2] = res[2, 0] = half_U2_sin2 + U3_sin4
        res[1, 2] = res[2, 1] = half_U2_sin2 - U3_sin4
        res[2, 2] = U5 - U3_cos4

cProfile.run('qbar1()', 'stats1')
cProfile.run('qbar3()', 'stats3')
import pstats
print("Qbar1")
pstats.Stats('stats1').sort_stats('time').print_stats(10)
print("Qbar3")
pstats.Stats('stats3').sort_stats('time').print_stats(10)
