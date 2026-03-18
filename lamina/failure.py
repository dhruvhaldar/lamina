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

        NM = np.zeros((6, len(angles)))
        NM[0, :] = sx_unit * h
        NM[1, :] = sy_unit * h

        # strain_curvature: (6, n_angles)
        strain_curvature = laminate.abd @ NM
        eps0 = strain_curvature[:3, :] # (3, n_angles)
        kappa = strain_curvature[3:, :] # (3, n_angles)

        Q = laminate.material.Q() # (3, 3)

        # Use precomputed trig values from laminate.c and laminate.s
        c = laminate.c
        s = laminate.s

        c2 = c*c
        s2 = s*s
        cs = c*s

        n_plies = len(laminate.stack)

        # Vectorized computation of T for all plies at once
        T_all = np.empty((n_plies, 3, 3))
        T_all[:, 0, 0] = c2
        T_all[:, 0, 1] = s2
        T_all[:, 0, 2] = cs
        T_all[:, 1, 0] = s2
        T_all[:, 1, 1] = c2
        T_all[:, 1, 2] = -cs
        T_all[:, 2, 0] = -2*cs
        T_all[:, 2, 1] = 2*cs
        T_all[:, 2, 2] = c2 - s2

        # Vectorized matmul: K = Q @ T
        # Q is (3,3), T_all is (n_plies, 3, 3). Result K_all is (n_plies, 3, 3)
        K_all = Q @ T_all

        # Vectorized computation of A_all and B_all
        # K_all: (n_plies, 3, 3), eps0/kappa: (3, n_angles)
        # Result A_all/B_all: (n_plies, 3, n_angles)
        A_all = K_all @ eps0
        B_all = K_all @ kappa

        z_mids = (laminate.z_coords[:-1] + laminate.z_coords[1:]) / 2
        z_mids = z_mids[:, np.newaxis, np.newaxis]

        S_all = A_all + z_mids * B_all

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
            sqrt_delta = np.sqrt(delta)

            # Quadratic solutions
            two_A = 2 * A
            f1_quad = (-B + sqrt_delta) / two_A
            f2_quad = (-B - sqrt_delta) / two_A

            # Linear solutions
            f_lin = 1.0 / B

            # Handle solutions efficiently using nested np.where to avoid generating multiple boolean masks and arrays
            f_quad = np.where((delta >= 0) & (f1_quad > 0), f1_quad,
                              np.where((delta >= 0) & (f2_quad > 0), f2_quad, np.inf))

            f_all = np.where(np.abs(A) < 1e-10,
                             np.where(B > 0, f_lin, np.inf),
                             f_quad)

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

        term = (s1_all/X)**2 - (s1_all*s2_all/X**2) + (s2_all/Y)**2 + (t12_all/S)**2

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

        f_s1 = np.full_like(s1_all, np.inf)
        f_s1 = np.where(s1_all > 0, Xt/s1_all, f_s1)
        # Avoid division by zero naturally as 0 is not < 0
        f_s1 = np.where(s1_all < 0, -Xc/s1_all, f_s1)

        f_s2 = np.full_like(s2_all, np.inf)
        f_s2 = np.where(s2_all > 0, Yt/s2_all, f_s2)
        f_s2 = np.where(s2_all < 0, -Yc/s2_all, f_s2)

        f_t12 = np.full_like(t12_all, np.inf)
        with np.errstate(divide='ignore', invalid='ignore'):
            f_t12 = np.where(t12_all != 0, S/np.abs(t12_all), np.inf)

        f_all = np.minimum(f_s1, np.minimum(f_s2, f_t12))
        min_factor = np.min(f_all, axis=0)

        valid_points = min_factor != np.inf
        final_sx = sx_unit[valid_points] * min_factor[valid_points]
        final_sy = sy_unit[valid_points] * min_factor[valid_points]

        return Envelope(list(zip(final_sx, final_sy)))
