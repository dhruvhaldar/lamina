import cProfile
import pstats
import numpy as np

def _get_transformation_matrices(angle_deg):
    theta = np.radians(angle_deg)
    c = np.cos(theta)
    s = np.sin(theta)

    if np.ndim(theta) == 0:
        pass
    else:
        c2 = c**2
        s2 = s**2
        cs = c*s

        T_sigma_T = np.array([
            [c2, s2, 2*cs],
            [s2, c2, -2*cs],
            [-cs, cs, c2-s2]
        ])
        T_sigma = T_sigma_T.transpose(2, 0, 1)

        T_epsilon_inv_T = np.array([
            [c2, s2, -cs],
            [s2, c2, cs],
            [2*cs, -2*cs, c2-s2]
        ])
        T_epsilon_inv = T_epsilon_inv_T.transpose(2, 0, 1)

    return T_sigma, T_epsilon_inv

def run_orig():
    angles = np.arange(360)
    for _ in range(1000):
        T_sigma_inv, T_epsilon = _get_transformation_matrices(-angles)

cProfile.run('run_orig()', 'stats')
p = pstats.Stats('stats')
p.sort_stats('time').print_stats(10)
