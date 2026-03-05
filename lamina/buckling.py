import numpy as np

class BucklingAnalysis:
    @staticmethod
    def critical_load(laminate, a, b, m_max=5):
        """
        Calculates critical buckling load Nx for a simply supported rectangular plate.

        Args:
            laminate (Laminate): Laminate object.
            a (float): Length in x-direction (m).
            b (float): Width in y-direction (m).
            m_max (int): Maximum mode number to check.

        Returns:
            float: Critical load N_cr (N/m).
            int: Mode number m.
        """
        D = laminate.D
        D11 = D[0, 0]
        D12 = D[0, 1]
        D22 = D[1, 1]
        D66 = D[2, 2]

        min_N = float('inf')
        best_m = 1

        # Optimization: Precompute loop-invariant constants
        pi_b_sq = np.pi**2 / b**2
        term2_b2_pi2 = pi_b_sq * 2 * (D12 + 2 * D66)
        factor1 = D11 * (b / a)**2 * pi_b_sq
        factor3 = D22 * (a / b)**2 * pi_b_sq

        # Check modes m = 1 to m_max
        for m in range(1, m_max + 1):
            m2 = m * m
            N = factor1 * m2 + term2_b2_pi2 + factor3 / m2

            if N < min_N:
                min_N = N
                best_m = m

        return min_N, best_m
