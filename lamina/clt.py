import numpy as np
import matplotlib.pyplot as plt
from lamina.materials import Material

def _transform_stiffness(Q, angle_deg):
    """
    Transforms stiffness matrix Q by rotating coordinate system by angle_deg.
    Q' = T_sigma @ Q @ T_epsilon_inv
    """
    theta = np.radians(angle_deg)
    c = np.cos(theta)
    s = np.sin(theta)

    # T_sigma (stress transformation)
    T_sigma = np.array([
        [c**2, s**2, 2*c*s],
        [s**2, c**2, -2*c*s],
        [-c*s, c*s, c**2-s**2]
    ])

    # T_epsilon_inv (strain transformation inverse)
    # T_epsilon_inv = T_epsilon(-theta)
    T_epsilon_inv = np.array([
        [c**2, s**2, -c*s],
        [s**2, c**2, c*s],
        [2*c*s, -2*c*s, c**2-s**2]
    ])

    return T_sigma @ Q @ T_epsilon_inv

class PolarResult:
    def __init__(self, data):
        self.data = data # list of dicts

    def plot(self, filename="polar_plot.png"):
        # Generate plot using matplotlib
        angles = [d['angle'] for d in self.data]
        Ex = [d['Ex'] for d in self.data]

        rads = np.radians(angles)

        plt.figure()
        ax = plt.subplot(111, projection='polar')
        ax.plot(rads, Ex)
        ax.set_title("Stiffness Polar Plot (Ex)")
        plt.savefig(filename)
        plt.close()

class Laminate:
    def __init__(self, material, stack, thickness=0.125e-3, symmetry=False):
        """
        Args:
            material (Material): Material object.
            stack (list): List of ply angles in degrees.
            thickness (float): Thickness of a single ply (m).
            symmetry (bool): If True, mirrors the stack.
        """
        self.material = material
        self.raw_stack = stack
        if symmetry:
            self.stack = stack + stack[::-1]
        else:
            self.stack = stack
        self.ply_thickness = thickness
        self.total_thickness = len(self.stack) * thickness

        self.Q_mat = material.Q()
        self.update()

    def update(self):
        self.z_coords = self._calculate_z_coords()

        # Vectorized calculation for performance
        # 1. Calculate Q_bar for all plies at once
        angles = np.array(self.stack)
        Q_bars = self._get_Q_bar(angles) # Returns (3, 3, n_plies)

        # 2. Calculate thickness terms
        zk = self.z_coords[1:]
        zk_1 = self.z_coords[:-1]

        h = zk - zk_1
        h2 = zk**2 - zk_1**2
        h3 = zk**3 - zk_1**3

        # 3. Sum over plies (axis 2)
        # Broadcasting: (3, 3, N) * (N,) -> (3, 3, N)
        self.A = np.sum(Q_bars * h, axis=2)
        self.B = 0.5 * np.sum(Q_bars * h2, axis=2)
        self.D = (1/3) * np.sum(Q_bars * h3, axis=2)

        # ABD Matrix
        self.ABD = np.vstack([
            np.hstack([self.A, self.B]),
            np.hstack([self.B, self.D])
        ])

        # Compliance Matrix (inverse of ABD)
        try:
            self.abd = np.linalg.inv(self.ABD)
        except np.linalg.LinAlgError:
            self.abd = np.zeros_like(self.ABD)

    def _calculate_z_coords(self):
        n_plies = len(self.stack)
        h = self.total_thickness
        z = np.linspace(-h/2, h/2, n_plies + 1)
        return z

    def _get_Q_bar(self, angle_deg):
        theta = np.radians(angle_deg)
        m = np.cos(theta)
        n = np.sin(theta)
        m2 = m**2
        n2 = n**2
        m4 = m**4
        n4 = n**4

        Q11 = self.Q_mat[0, 0]
        Q12 = self.Q_mat[0, 1]
        Q22 = self.Q_mat[1, 1]
        Q66 = self.Q_mat[2, 2]

        Q_bar_11 = Q11*m4 + 2*(Q12 + 2*Q66)*m2*n2 + Q22*n4
        Q_bar_12 = (Q11 + Q22 - 4*Q66)*m2*n2 + Q12*(m4 + n4)
        Q_bar_22 = Q11*n4 + 2*(Q12 + 2*Q66)*m2*n2 + Q22*m4
        Q_bar_16 = (Q11 - Q12 - 2*Q66)*n*m**3 + (Q12 - Q22 + 2*Q66)*n**3*m
        Q_bar_26 = (Q11 - Q12 - 2*Q66)*n**3*m + (Q12 - Q22 + 2*Q66)*n*m**3
        Q_bar_66 = (Q11 + Q22 - 2*Q12 - 2*Q66)*m2*n2 + Q66*(m4 + n4)

        return np.array([
            [Q_bar_11, Q_bar_12, Q_bar_16],
            [Q_bar_12, Q_bar_22, Q_bar_26],
            [Q_bar_16, Q_bar_26, Q_bar_66]
        ])

    def properties(self):
        """Returns equivalent engineering constants."""
        h = self.total_thickness
        a = self.abd[:3, :3]

        # Avoid division by zero
        Ex = 1 / (h * a[0, 0]) if a[0, 0] != 0 else 0
        Ey = 1 / (h * a[1, 1]) if a[1, 1] != 0 else 0
        Gxy = 1 / (h * a[2, 2]) if a[2, 2] != 0 else 0
        vxy = -a[0, 1] / a[0, 0] if a[0, 0] != 0 else 0

        return {
            "Ex": Ex,
            "Ey": Ey,
            "Gxy": Gxy,
            "vxy": vxy
        }

    def polar_stiffness(self, step=10):
        angles = np.arange(0, 360, step)
        results = []

        # Calculate properties by rotating the ABD matrix
        # This is much faster than re-creating Laminate objects
        h = self.total_thickness

        for phi in angles:
            # Rotate A, B, D matrices
            # Rotating coordinate system by phi is equivalent to finding properties in direction phi
            A_prime = _transform_stiffness(self.A, phi)
            B_prime = _transform_stiffness(self.B, phi)
            D_prime = _transform_stiffness(self.D, phi)

            # Assemble rotated ABD
            ABD_prime = np.vstack([
                np.hstack([A_prime, B_prime]),
                np.hstack([B_prime, D_prime])
            ])

            # Invert to get compliance
            try:
                abd_prime = np.linalg.inv(ABD_prime)
            except np.linalg.LinAlgError:
                abd_prime = np.zeros_like(ABD_prime)

            # Calculate engineering constants from compliance
            a = abd_prime[:3, :3]
            Ex = 1 / (h * a[0, 0]) if a[0, 0] != 0 else 0
            Ey = 1 / (h * a[1, 1]) if a[1, 1] != 0 else 0
            Gxy = 1 / (h * a[2, 2]) if a[2, 2] != 0 else 0

            results.append({
                "angle": float(phi),
                "Ex": Ex,
                "Ey": Ey,
                "Gxy": Gxy
            })

        return PolarResult(results)
