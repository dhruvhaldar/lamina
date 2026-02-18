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
            ply_stresses: list of (s1, s2, t12) arrays for each ply
        """
        sx_unit = np.cos(angles)
        sy_unit = np.sin(angles)
        txy_unit = np.zeros_like(angles)

        # N shape: (3, n_angles)
        N = np.vstack([sx_unit, sy_unit, txy_unit]) * h
        # M shape: (3, n_angles)
        M = np.zeros_like(N)

        NM = np.vstack([N, M]) # (6, n_angles)

        # strain_curvature: (6, n_angles)
        strain_curvature = laminate.abd @ NM
        eps0 = strain_curvature[:3, :] # (3, n_angles)
        kappa = strain_curvature[3:, :] # (3, n_angles)

        Q = laminate.material.Q() # (3, 3)

        # Cache for angle-dependent terms to avoid redundant calculations
        # Key: angle, Value: (A_term, B_term) where s = A_term + z * B_term
        angle_cache = {}
        unique_angles = set(laminate.stack)

        for angle in unique_angles:
            theta = np.radians(angle)
            c = np.cos(theta)
            s = np.sin(theta)
            c2 = c*c
            s2 = s*s
            cs = c*s

            # T_epsilon matrix: strain transformation global -> local
            T = np.array([
                [c2, s2, cs],
                [s2, c2, -cs],
                [-2*cs, 2*cs, c2-s2]
            ])

            # K = Q @ T
            # s_local = Q @ eps_local = Q @ T @ eps_global
            # s_local = K @ (eps0 + z * kappa) = (K @ eps0) + z * (K @ kappa)
            K = Q @ T

            A_term = K @ eps0 # (3, n_angles)
            B_term = K @ kappa # (3, n_angles)
            angle_cache[angle] = (A_term, B_term)

        def stress_generator():
            # Z coordinates midpoints
            z_mids = (laminate.z_coords[:-1] + laminate.z_coords[1:]) / 2

            for i, angle in enumerate(laminate.stack):
                z = z_mids[i]
                A, B = angle_cache[angle]

                # Compute component-wise to avoid allocating intermediate (3, N) array
                # and keep operations cache-friendly
                yield A[0] + z * B[0], A[1] + z * B[1], A[2] + z * B[2]

        return sx_unit, sy_unit, stress_generator()

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

        angles = np.linspace(0, 2*np.pi, num_points)
        h = laminate.total_thickness

        sx_unit, sy_unit, ply_stresses = FailureCriterion._get_stresses_vectorized(laminate, angles, h)

        min_factor = np.full_like(angles, np.inf)

        for s1, s2, t12 in ply_stresses:
            A = F11*s1**2 + F22*s2**2 + F66*t12**2 + 2*F12*s1*s2
            B = F1*s1 + F2*s2

            mask_linear = np.abs(A) < 1e-10
            f_ply = np.full_like(angles, np.inf)

            # Linear case
            # Using simple boolean indexing where possible
            if np.any(mask_linear):
                B_lin = B[mask_linear]
                # Avoid div by zero
                with np.errstate(divide='ignore', invalid='ignore'):
                    f_lin = np.where(B_lin > 0, 1.0/B_lin, np.inf)
                f_ply[mask_linear] = f_lin

            # Quadratic case
            mask_quad = ~mask_linear
            if np.any(mask_quad):
                A_q = A[mask_quad]
                B_q = B[mask_quad]
                delta = B_q**2 + 4*A_q

                # We need to process only where delta >= 0
                valid_delta = delta >= 0

                # Indices in the subset that are valid
                if np.any(valid_delta):
                    # Extract only valid ones
                    A_vq = A_q[valid_delta]
                    B_vq = B_q[valid_delta]
                    sqrt_delta = np.sqrt(delta[valid_delta])

                    f1 = (-B_vq + sqrt_delta) / (2*A_vq)
                    f2 = (-B_vq - sqrt_delta) / (2*A_vq)

                    f_final = np.full_like(f1, np.inf)

                    mask_f1 = f1 > 0
                    mask_f2 = (f2 > 0) & (~mask_f1)

                    f_final[mask_f1] = f1[mask_f1]
                    f_final[mask_f2] = f2[mask_f2]

                    # Now map back to f_ply
                    # We have f_ply[mask_quad] which has length of mask_quad.sum()
                    # We need to update only those where valid_delta is true within that

                    # Create a temporary array for quadratic results
                    f_quad = np.full(mask_quad.sum(), np.inf)
                    f_quad[valid_delta] = f_final

                    f_ply[mask_quad] = f_quad

            min_factor = np.minimum(min_factor, f_ply)

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

        angles = np.linspace(0, 2*np.pi, num_points)
        h = laminate.total_thickness

        sx_unit, sy_unit, ply_stresses = FailureCriterion._get_stresses_vectorized(laminate, angles, h)
        min_factor = np.full_like(angles, np.inf)

        for s1, s2, t12 in ply_stresses:
            X = np.where(s1 >= 0, Xt, Xc)
            Y = np.where(s2 >= 0, Yt, Yc)

            term = (s1/X)**2 - (s1*s2/X**2) + (s2/Y)**2 + (t12/S)**2

            f_ply = np.full_like(term, np.inf)
            valid = term > 0
            f_ply[valid] = np.sqrt(1.0/term[valid])

            min_factor = np.minimum(min_factor, f_ply)

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

        angles = np.linspace(0, 2*np.pi, num_points)
        h = laminate.total_thickness

        sx_unit, sy_unit, ply_stresses = FailureCriterion._get_stresses_vectorized(laminate, angles, h)
        min_factor = np.full_like(angles, np.inf)

        for s1, s2, t12 in ply_stresses:
            f_s1 = np.full_like(s1, np.inf)
            f_s1 = np.where(s1 > 0, Xt/s1, f_s1)
            # Avoid division by zero naturally as 0 is not < 0
            f_s1 = np.where(s1 < 0, -Xc/s1, f_s1)

            f_s2 = np.full_like(s2, np.inf)
            f_s2 = np.where(s2 > 0, Yt/s2, f_s2)
            f_s2 = np.where(s2 < 0, -Yc/s2, f_s2)

            f_t12 = np.full_like(t12, np.inf)
            with np.errstate(divide='ignore'):
                f_t12 = np.where(t12 != 0, S/np.abs(t12), np.inf)

            f_ply = np.minimum(f_s1, np.minimum(f_s2, f_t12))
            min_factor = np.minimum(min_factor, f_ply)

        valid_points = min_factor != np.inf
        final_sx = sx_unit[valid_points] * min_factor[valid_points]
        final_sy = sy_unit[valid_points] * min_factor[valid_points]

        return Envelope(list(zip(final_sx, final_sy)))
