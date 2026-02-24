import random
import numpy as np
from lamina.clt import Laminate
from lamina.buckling import BucklingAnalysis

def calculate_safety_factor(laminate, load, limits):
    """
    Calculates the minimum safety factor using Tsai-Wu criterion.
    Vectorized implementation for performance.
    """
    Nx = load.get('Nx', 0)
    Ny = load.get('Ny', 0)
    Nxy = load.get('Nxy', 0)

    ABD_inv = laminate.abd
    N = np.array([Nx, Ny, Nxy])
    M = np.zeros(3)
    NM = np.concatenate([N, M])
    strain_curv = ABD_inv @ NM
    eps0 = strain_curv[:3]
    kap = strain_curv[3:]

    Xt = limits['xt']
    Xc = limits['xc']
    Yt = limits['yt']
    Yc = limits['yc']
    S = limits.get('s', limits.get('S', Xt/2))

    F1 = 1/Xt - 1/Xc
    F2 = 1/Yt - 1/Yc
    F11 = 1/(Xt * Xc)
    F22 = 1/(Yt * Yc)
    F66 = 1/(S**2)
    F12 = -0.5 * np.sqrt(F11 * F22)

    # Vectorized operations
    # Optimization: Use precomputed trig values from Laminate if available
    if hasattr(laminate, 'c') and hasattr(laminate, 's'):
        c = laminate.c
        s = laminate.s
    else:
        angles = np.array(laminate.stack)
        theta = np.radians(angles)
        c = np.cos(theta)
        s = np.sin(theta)

    c2 = c**2
    s2 = s**2
    cs = c*s

    # z coordinates (midpoints)
    # laminate.z_coords is size N+1
    z = (laminate.z_coords[:-1] + laminate.z_coords[1:]) / 2

    # eps_global: (3, N)
    # eps0: (3,) -> (3, 1)
    # kap: (3,) -> (3, 1)
    # z: (N,) -> (1, N)
    eps_global = eps0[:, np.newaxis] + kap[:, np.newaxis] * z[np.newaxis, :]

    ex = eps_global[0]
    ey = eps_global[1]
    gxy = eps_global[2]

    e1 = c2 * ex + s2 * ey + cs * gxy
    e2 = s2 * ex + c2 * ey - cs * gxy
    g12 = -2*cs * ex + 2*cs * ey + (c2 - s2) * gxy

    # Use laminate.material.Q() (Material Q matrix is constant)
    Q = laminate.material.Q()
    s1 = Q[0,0]*e1 + Q[0,1]*e2
    s2 = Q[1,0]*e1 + Q[1,1]*e2
    t12 = Q[2,2]*g12

    # Tsai-Wu: A f^2 + B f - 1 = 0
    A = F11*s1**2 + F22*s2**2 + F66*t12**2 + 2*F12*s1*s2
    B = F1*s1 + F2*s2

    # Initialize f with infinity
    f_all = np.full_like(A, np.inf)

    # Handle A near 0 (linear case)
    mask_linear = np.abs(A) < 1e-10

    # Linear: B*f - 1 = 0 => f = 1/B
    # Only if B > 0
    mask_lin_pos = mask_linear & (B > 0)
    f_all[mask_lin_pos] = 1 / B[mask_lin_pos]

    # Quadratic
    mask_quad = ~mask_linear

    if np.any(mask_quad):
        A_q = A[mask_quad]
        B_q = B[mask_quad]
        delta = B_q**2 + 4*A_q

        # Check for valid solutions (delta >= 0)
        mask_delta = delta >= 0

        if np.any(mask_delta):
            sqrt_delta = np.sqrt(delta[mask_delta])
            A_valid = A_q[mask_delta]
            B_valid = B_q[mask_delta]

            f1 = (-B_valid + sqrt_delta) / (2*A_valid)
            f2 = (-B_valid - sqrt_delta) / (2*A_valid)

            f_sol = np.full_like(f1, np.inf)

            # Prefer f1 if > 0
            mask_f1 = f1 > 0
            f_sol[mask_f1] = f1[mask_f1]

            # Else try f2
            mask_f2 = (~mask_f1) & (f2 > 0)
            f_sol[mask_f2] = f2[mask_f2]

            # Map back to f_all
            # Create array for quadratic subset
            f_quad_subset = np.full(mask_quad.sum(), np.inf)
            f_quad_subset[mask_delta] = f_sol

            f_all[mask_quad] = f_quad_subset

    return np.min(f_all)

class GeneticAlgorithm:
    def __init__(self, material, load, constraints, population_size=20, generations=10):
        self.material = material
        self.load = load
        self.constraints = constraints
        self.pop_size = population_size
        self.generations = generations
        self.valid_angles = [0, 45, -45, 90]

    def optimize(self, min_plies=4, max_plies=16):
        # Try finding min weight
        for n_plies in range(min_plies, max_plies + 1, 2):
            half_n = n_plies // 2

            # Run GA
            solution = self._run_ga(half_n)

            if solution:
                return solution # Found minimal weight solution

        return None

    def _run_ga(self, n_plies):
        population = [self._random_stack(n_plies) for _ in range(self.pop_size)]

        # Keep track of best ever found in this run
        best_ever_stack = None
        best_ever_score = -float('inf')

        for gen in range(self.generations):
            fitness_scores = []
            for stack in population:
                score = self._evaluate(stack)
                fitness_scores.append((score, stack))

            fitness_scores.sort(key=lambda x: x[0], reverse=True)

            if fitness_scores[0][0] > best_ever_score:
                best_ever_score = fitness_scores[0][0]
                best_ever_stack = fitness_scores[0][1]

            # Elitism
            parents = fitness_scores[:max(2, self.pop_size//2)]
            next_gen = [p[1] for p in parents]

            while len(next_gen) < self.pop_size:
                p1 = random.choice(parents)[1]
                p2 = random.choice(parents)[1]
                child = self._crossover(p1, p2)
                self._mutate(child)
                next_gen.append(child)

            population = next_gen

        if best_ever_score > 0:
            return best_ever_stack + best_ever_stack[::-1] # Return full symmetric stack
        return None

    def _random_stack(self, n):
        return [random.choice(self.valid_angles) for _ in range(n)]

    def _crossover(self, p1, p2):
        if len(p1) < 2: return p1
        point = random.randint(1, len(p1)-1)
        return p1[:point] + p2[point:]

    def _mutate(self, stack):
        if random.random() < 0.2:
            idx = random.randint(0, len(stack)-1)
            stack[idx] = random.choice(self.valid_angles)

    def _evaluate(self, half_stack):
        full_stack = half_stack + half_stack[::-1]
        lam = Laminate(self.material, full_stack, symmetry=False)

        score = 1.0

        # Buckling
        if 'buckling_load' in self.constraints:
             a = self.constraints.get('a', 1.0)
             b = self.constraints.get('b', 1.0)
             crit_load, _ = BucklingAnalysis.critical_load(lam, a, b)
             req = self.constraints['buckling_load']
             if crit_load < req:
                 return -1.0 # Invalid
             score += (crit_load / req) * 0.1 # Add bonus for extra buckling

        # Strength
        if 'safety_factor' in self.constraints:
            sf_req = self.constraints['safety_factor']
            limits = self.constraints['limits']
            sf = calculate_safety_factor(lam, self.load, limits)

            if sf < sf_req:
                return -1.0
            score += sf # Maximize safety factor

        return score
