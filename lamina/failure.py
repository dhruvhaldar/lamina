import numpy as np
import matplotlib.pyplot as plt

class Envelope:
    def __init__(self, data):
        self.data = data # list of (sigma_x, sigma_y)

    def plot(self, filename="failure_envelope.png"):
        sx = [d[0] for d in self.data]
        sy = [d[1] for d in self.data]

        # Close the loop
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
    def _get_stresses(laminate, angle, h):
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

        results = []
        angles = np.linspace(0, 2*np.pi, num_points)
        h = laminate.total_thickness

        for angle in angles:
            sx_unit, sy_unit, ply_stresses = FailureCriterion._get_stresses(laminate, angle, h)
            min_factor = float('inf')

            for s1, s2, t12 in ply_stresses:
                A = F11*s1**2 + F22*s2**2 + F66*t12**2 + 2*F12*s1*s2
                B = F1*s1 + F2*s2

                if abs(A) < 1e-10:
                    if B > 0: f = 1/B
                    else: f = float('inf')
                else:
                    delta = B**2 + 4*A
                    if delta < 0: f = float('inf')
                    else:
                        f1 = (-B + np.sqrt(delta)) / (2*A)
                        f2 = (-B - np.sqrt(delta)) / (2*A)
                        if f1 > 0: f = f1
                        elif f2 > 0: f = f2
                        else: f = float('inf')

                if f < min_factor:
                    min_factor = f

            if min_factor != float('inf'):
                results.append((sx_unit * min_factor, sy_unit * min_factor))

        return Envelope(results)

    @staticmethod
    def tsai_hill(laminate, limits, num_points=72):
        Xt = limits['xt']
        Xc = limits['xc']
        Yt = limits['yt']
        Yc = limits['yc']
        S = limits.get('s', limits.get('S', Xt/2))

        results = []
        angles = np.linspace(0, 2*np.pi, num_points)
        h = laminate.total_thickness

        for angle in angles:
            sx_unit, sy_unit, ply_stresses = FailureCriterion._get_stresses(laminate, angle, h)
            min_factor = float('inf')

            for s1, s2, t12 in ply_stresses:
                X = Xt if s1 >= 0 else Xc
                Y = Yt if s2 >= 0 else Yc

                # Hill: (s1/X)^2 - (s1*s2/X^2) + (s2/Y)^2 + (t12/S)^2 = 1
                # LHS = factor^2 * ( ... )

                term = (s1/X)**2 - (s1*s2/X**2) + (s2/Y)**2 + (t12/S)**2

                if term > 0:
                    f = np.sqrt(1/term)
                else:
                    f = float('inf')

                if f < min_factor:
                    min_factor = f

            if min_factor != float('inf'):
                results.append((sx_unit * min_factor, sy_unit * min_factor))

        return Envelope(results)

    @staticmethod
    def max_stress(laminate, limits, num_points=72):
        Xt = limits['xt']
        Xc = limits['xc']
        Yt = limits['yt']
        Yc = limits['yc']
        S = limits.get('s', limits.get('S', Xt/2))

        results = []
        angles = np.linspace(0, 2*np.pi, num_points)
        h = laminate.total_thickness

        for angle in angles:
            sx_unit, sy_unit, ply_stresses = FailureCriterion._get_stresses(laminate, angle, h)
            min_factor = float('inf')

            for s1, s2, t12 in ply_stresses:
                # Calculate factor for each mode
                f_s1 = float('inf')
                if s1 > 0: f_s1 = Xt / s1
                elif s1 < 0: f_s1 = -Xc / s1

                f_s2 = float('inf')
                if s2 > 0: f_s2 = Yt / s2
                elif s2 < 0: f_s2 = -Yc / s2

                f_t12 = float('inf')
                if t12 != 0: f_t12 = S / abs(t12)

                f = min(f_s1, f_s2, f_t12)
                if f < min_factor:
                    min_factor = f

            if min_factor != float('inf'):
                results.append((sx_unit * min_factor, sy_unit * min_factor))

        return Envelope(results)
