import numpy as np
import matplotlib.pyplot as plt

class Envelope:
    def __init__(self, data):
        self.data = data # list of (sigma_x, sigma_y)

    def plot(self, filename="failure_envelope.png"):
        sx = [d[0] for d in self.data]
        sy = [d[1] for d in self.data]

        # Close the loop
        if len(sx) > 0:
            sx.append(sx[0])
            sy.append(sy[0])

        plt.figure()
        plt.plot(sx, sy)
        plt.xlabel("Sigma_x (Pa)")
        plt.ylabel("Sigma_y (Pa)")
        plt.title("Failure Envelope")
        plt.grid(True)
        plt.axis('equal')
        plt.savefig(filename)
        plt.close()

    def plot_2(self):
        self.plot("failure_envelope.png")

class FailureCriterion:
    @staticmethod
    def _get_stresses_vectorized(laminate, angles, h):
        """
        Vectorized version of _get_stresses.
        Args:
            laminate: Laminate object
            angles: numpy array of angles (in radians)
            h: total thickness
        Returns:
            sx_unit: array of cos(angle)
            sy_unit: array of sin(angle)
            s1_all: 2D array of sigma 1 for each ply and angle
            s2_all: 2D array of sigma 2 for each ply and angle
            t12_all: 2D array of tau 12 for each ply and angle
        """
        sx_unit = np.cos(angles)
        sy_unit = np.sin(angles)

        # Optimization: Only explicitly allocate the non-zero rows of the NM matrix
        # and slice the abd matrix to avoid processing known zeros, which significantly
        # reduces redundant floating-point operations during matrix multiplication.
        NM_reduced = np.empty((2, len(angles)))
        NM_reduced[0, :] = sx_unit * h
        NM_reduced[1, :] = sy_unit * h

        # strain_curvature: (6, n_angles)
        strain_curvature = laminate.abd[:, :2] @ NM_reduced
        eps0 = strain_curvature[:3, :] # (3, n_angles)
        kappa = strain_curvature[3:, :] # (3, n_angles)

        # Optimization: Use precomputed K_all and K_all_z matrices from Laminate
        # to avoid recalculating T_all matrices and K_all @ kappa for every point/loop
        S_all = laminate.K_all @ eps0 + laminate.K_all_z @ kappa

        return sx_unit, sy_unit, S_all[:, 0, :], S_all[:, 1, :], S_all[:, 2, :]

    @staticmethod
    def _get_stresses(laminate, angle, h):
        # Keep for backward compatibility if needed, but updated methods won't use it.
        # It's better to implement it using the vectorized version to avoid duplication?
        # Or just keep it as is.
        # I'll keep it as is for now to avoid breaking anything unexpected,
        # but updated methods below will use vectorized one.
        sx_unit = np.cos(angle)
        sy_unit = np.sin(angle)
        txy_unit = 0

        N = np.array([sx_unit, sy_unit, txy_unit]) * h
        M = np.zeros(3)

        NM = np.concatenate([N, M])
        strain_curvature = laminate.abd @ NM
        eps0 = strain_curvature[:3]
        kappa = strain_curvature[3:]

        ply_stresses = []

        for i, ply_angle in enumerate(laminate.stack):
            z = laminate.z_coords[i] + laminate.ply_thickness/2 # Mid-ply
            eps_global = eps0 + z * kappa

            # Transform to local strain
            theta = np.radians(ply_angle)
            c = np.cos(theta)
            s = np.sin(theta)

            ex = eps_global[0]
            ey = eps_global[1]
            gxy = eps_global[2]

            e1 = c**2 * ex + s**2 * ey + c*s*gxy
            e2 = s**2 * ex + c**2 * ey - c*s*gxy
            g12 = -2*c*s * ex + 2*c*s * ey + (c**2 - s**2) * gxy

            Q = laminate.material.Q()
            s1 = Q[0,0]*e1 + Q[0,1]*e2
            s2 = Q[1,0]*e1 + Q[1,1]*e2
            t12 = Q[2,2]*g12

            ply_stresses.append((s1, s2, t12))

        return sx_unit, sy_unit, ply_stresses

    @staticmethod
    def tsai_wu(laminate, limits, num_points=72):
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

        # Optimization: np.arange and simple math is significantly faster than np.linspace for small arrays
        angles = np.arange(num_points, dtype=np.float64) * (2 * np.pi / max(1, num_points - 1))
        h = laminate.total_thickness

        sx_unit, sy_unit, s1_all, s2_all, t12_all = FailureCriterion._get_stresses_vectorized(laminate, angles, h)

        A = F11*s1_all**2 + F22*s2_all**2 + F66*t12_all**2 + 2*F12*s1_all*s2_all
        B = F1*s1_all + F2*s2_all

        delta = np.square(B) + 4 * A

        with np.errstate(divide='ignore', invalid='ignore'):
            # Optimization: Mathematically, A is always non-negative because the
            # Tsai-Wu coefficients form a positive-definite matrix. Thus, delta >= 0
            # and sqrt_delta >= |B|. The only positive root is f1_quad.
            # This completely avoids allocating and selecting between intermediate root arrays.
            sqrt_delta = np.sqrt(delta)
            f1_quad = (-B + sqrt_delta) / (2 * A)

            f_lin = 1.0 / B

            f_all = np.where(A < 1e-10,
                             np.where(B > 0, f_lin, np.inf),
                             f1_quad)

        min_factor = np.min(f_all, axis=0)

        valid_points = min_factor != np.inf
        final_sx = sx_unit[valid_points] * min_factor[valid_points]
        final_sy = sy_unit[valid_points] * min_factor[valid_points]

        return Envelope(list(zip(final_sx, final_sy)))

    @staticmethod
    def tsai_hill(laminate, limits, num_points=72):
        Xt = limits['xt']
        Xc = limits['xc']
        Yt = limits['yt']
        Yc = limits['yc']
        S = limits.get('s', limits.get('S', Xt/2))

        # Optimization: np.arange and simple math is significantly faster than np.linspace for small arrays
        angles = np.arange(num_points, dtype=np.float64) * (2 * np.pi / max(1, num_points - 1))
        h = laminate.total_thickness

        sx_unit, sy_unit, s1_all, s2_all, t12_all = FailureCriterion._get_stresses_vectorized(laminate, angles, h)

        X = np.where(s1_all >= 0, Xt, Xc)
        Y = np.where(s2_all >= 0, Yt, Yc)

        s1_X = s1_all / X
        term = s1_X * (s1_X - s2_all / X) + np.square(s2_all / Y) + np.square(t12_all / S)

        f_all = np.full_like(term, np.inf)
        valid = term > 0
        f_all[valid] = np.sqrt(1.0/term[valid])

        min_factor = np.min(f_all, axis=0)

        valid_points = min_factor != np.inf
        final_sx = sx_unit[valid_points] * min_factor[valid_points]
        final_sy = sy_unit[valid_points] * min_factor[valid_points]

        return Envelope(list(zip(final_sx, final_sy)))

    @staticmethod
    def max_stress(laminate, limits, num_points=72):
        Xt = limits['xt']
        Xc = limits['xc']
        Yt = limits['yt']
        Yc = limits['yc']
        S = limits.get('s', limits.get('S', Xt/2))

        # Optimization: np.arange and simple math is significantly faster than np.linspace for small arrays
        angles = np.arange(num_points, dtype=np.float64) * (2 * np.pi / max(1, num_points - 1))
        h = laminate.total_thickness

        sx_unit, sy_unit, s1_all, s2_all, t12_all = FailureCriterion._get_stresses_vectorized(laminate, angles, h)

        with np.errstate(divide='ignore', invalid='ignore'):
            f_s1 = np.where(s1_all > 0, Xt, -Xc) / s1_all
            f_s1 = np.where(s1_all == 0, np.inf, f_s1)

            f_s2 = np.where(s2_all > 0, Yt, -Yc) / s2_all
            f_s2 = np.where(s2_all == 0, np.inf, f_s2)

            f_t12 = S / np.abs(t12_all)
            f_t12 = np.where(t12_all == 0, np.inf, f_t12)

        f_all = np.minimum(f_s1, np.minimum(f_s2, f_t12))
        min_factor = np.min(f_all, axis=0)

        valid_points = min_factor != np.inf
        final_sx = sx_unit[valid_points] * min_factor[valid_points]
        final_sy = sy_unit[valid_points] * min_factor[valid_points]

        return Envelope(list(zip(final_sx, final_sy)))
