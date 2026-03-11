import cProfile
import pstats
import sys

def main():
    from lamina.materials import CarbonEpoxy
    from lamina.optimization import GeneticAlgorithm, calculate_safety_factor
    from lamina.clt import Laminate

    mat = CarbonEpoxy()
    load = {'Nx': 1000e3, 'Ny': 0, 'Nxy': 0}
    constraints = {
        'safety_factor': 1.2,
        'limits': {'xt': 1500e6, 'xc': 1200e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6}
    }
    ga = GeneticAlgorithm(mat, load, constraints, population_size=10, generations=5)
    best_stack = ga.optimize(min_plies=4, max_plies=32)

if __name__ == '__main__':
    cProfile.run('main()', 'profile_results4')
    p = pstats.Stats('profile_results4')
    p.sort_stats('tottime').print_stats(30)
