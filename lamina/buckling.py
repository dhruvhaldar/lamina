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
        D11, D12, D22, D66 = D[0, 0], D[0, 1], D[1, 1], D[2, 2]

        # Optimization: Precompute loop-invariant constants using explicit math
        # to avoid float exponents and unnecessary division
        pi_sq_b_sq = 9.869604401089358 / (b * b)
        term2 = pi_sq_b_sq * 2 * (D12 + 2 * D66)

        b_a = b / a
        factor1 = D11 * (b_a * b_a) * pi_sq_b_sq

        a_b = a / b
        factor3 = D22 * (a_b * a_b) * pi_sq_b_sq

        # Initialize with m = 1
        min_N = factor1 + term2 + factor3
        best_m = 1

        # Optimization: Unpacking via tuple is marginally faster than range() overhead for small limits
        for m in (2, 3, 4, 5):
            if m > m_max: break
            m2 = m * m
            N = factor1 * m2 + term2 + factor3 / m2

            if N < min_N:
                min_N = N
                best_m = m

        # Fallback for unusually large m_max requirements
        if m_max > 5:
            for m in range(6, m_max + 1):
                m2 = m * m
                N = factor1 * m2 + term2 + factor3 / m2

                if N < min_N:
                    min_N = N
                    best_m = m

        return min_N, best_m
