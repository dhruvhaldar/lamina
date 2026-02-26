import numpy as np
import matplotlib.pyplot as plt
from lamina.materials import Material

def _get_transformation_matrices(angle_deg):
    """
    Computes T_sigma and T_epsilon_inv matrices for a given angle (scalar or array).
    """
    theta = np.radians(angle_deg)
    c = np.cos(theta)
    s = np.sin(theta)

    if np.ndim(theta) == 0:
        # T_sigma (stress transformation)
        T_sigma = np.array([
            [c**2, s**2, 2*c*s],
            [s**2, c**2, -2*c*s],
            [-c*s, c*s, c**2-s**2]
        ])

        # T_epsilon_inv (strain transformation inverse)
        T_epsilon_inv = np.array([
            [c**2, s**2, -c*s],
            [s**2, c**2, c*s],
            [2*c*s, -2*c*s, c**2-s**2]
        ])
    else:
        # Vectorized case: theta is (N,)
        c2 = c**2
        s2 = s**2
        cs = c*s

        # Construct T_sigma as (N, 3, 3)
        # We construct (3, 3, N) first then transpose
        T_sigma_T = np.array([
            [c2, s2, 2*cs],
            [s2, c2, -2*cs],
            [-cs, cs, c2-s2]
        ])
        T_sigma = T_sigma_T.transpose(2, 0, 1)

        # Construct T_epsilon_inv as (N, 3, 3)
        T_epsilon_inv_T = np.array([
            [c2, s2, -cs],
            [s2, c2, cs],
            [2*cs, -2*cs, c2-s2]
        ])
        T_epsilon_inv = T_epsilon_inv_T.transpose(2, 0, 1)

    return T_sigma, T_epsilon_inv


def _apply_transformation(Q, T_sigma, T_epsilon_inv):
    """
    Applies transformation: Q' = T_sigma @ Q @ T_epsilon_inv.
    Handles broadcasting if T matrices are stacked.
    """
    if T_sigma.ndim == 3:
        # Vectorized case: (N, 3, 3) @ (3, 3) @ (N, 3, 3) -> (N, 3, 3)
        # Using einsum avoids large intermediate array allocation and is ~3x faster for this shape
        return np.einsum('nij,jk,nkl->nil', T_sigma, Q, T_epsilon_inv)
    return T_sigma @ Q @ T_epsilon_inv


def _transform_stiffness(Q, angle_deg):
    """
    Transforms stiffness matrix Q by rotating coordinate system by angle_deg.
    Q' = T_sigma @ Q @ T_epsilon_inv
    Supports angle_deg as scalar or numpy array.
    """
    T_sigma, T_epsilon_inv = _get_transformation_matrices(angle_deg)
    return _apply_transformation(Q, T_sigma, T_epsilon_inv)

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

        # Precompute and store trig values for reuse in failure analysis and optimization
        self.rads = np.radians(angles)
        self.c = np.cos(self.rads)
        self.s = np.sin(self.rads)

        # Calculate Q_bar using precomputed trig values for performance
        Q_bars = self._get_Q_bar_from_trig(self.c, self.s) # Returns (3, 3, n_plies)

        # 2. Calculate thickness terms
        zk = self.z_coords[1:]
        zk_1 = self.z_coords[:-1]

        h = zk - zk_1
        h2 = zk**2 - zk_1**2
        h3 = zk**3 - zk_1**3

        # 3. Sum over plies (axis 2)
        # Optimization: Use dot product for A, B, and D matrices.
        # This replaces broadcasting which creates large temporary arrays (3, 3, N)
        # and leverages optimized BLAS routines (reshape(9, N) @ (N,)).
        self.A = (Q_bars.reshape(9, -1) @ h).reshape(3, 3)
        self.B = 0.5 * (Q_bars.reshape(9, -1) @ h2).reshape(3, 3)
        self.D = (1/3) * (Q_bars.reshape(9, -1) @ h3).reshape(3, 3)

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
        """
        Calculate transformed stiffness matrix Q_bar for given angles.
        Wrapper around _get_Q_bar_from_trig for backward compatibility.
        """
        theta = np.radians(angle_deg)
        c = np.cos(theta)
        s = np.sin(theta)
        return self._get_Q_bar_from_trig(c, s)

    def _get_Q_bar_from_trig(self, c, s):
        """
        Calculate transformed stiffness matrix Q_bar using precomputed cos(theta) and sin(theta).
        Avoids recomputing trig functions and uses double-angle identities.
        """
        # Use invariants for faster calculation
        U1, U2, U3, U4, U5 = self.material.invariants

        # Calculate double angles from single angles
        # cos(2t) = c^2 - s^2
        # sin(2t) = 2*c*s

        c2 = c*c
        s2 = s*s

        cos2 = c2 - s2
        sin2 = 2 * c * s

        # cos(4t) = cos(2*2t) = cos2^2 - sin2^2
        # sin(4t) = 2*cos2*sin2

        cos2_sq = cos2*cos2
        sin2_sq = sin2*sin2

        cos4 = cos2_sq - sin2_sq
        sin4 = 2 * cos2 * sin2

        Q_bar_11 = U1 + U2*cos2 + U3*cos4
        Q_bar_12 = U4 - U3*cos4
        Q_bar_22 = U1 - U2*cos2 + U3*cos4
        Q_bar_16 = 0.5*U2*sin2 + U3*sin4
        Q_bar_26 = 0.5*U2*sin2 - U3*sin4
        Q_bar_66 = U5 - U3*cos4

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
        h = self.total_thickness

        # Optimization: Directly transform compliance matrix components instead of
        # transforming stiffness (ABD), assembling 6x6, and inverting it N times.
        # This reduces complexity from O(N * 6^3) to O(N * 3^3).

        # We need to transform the compliance matrix 'abd'.
        # The transformation rule for compliance S is S' = T_epsilon @ S @ T_sigma^-1
        # where T_epsilon is the strain transformation matrix and T_sigma is stress transformation.

        # We can obtain T_epsilon and T_sigma^-1 by calling _get_transformation_matrices with -angles.
        # _get_transformation_matrices(theta) returns (T_sigma(theta), T_epsilon_inv(theta)).
        # T_sigma(-theta) = T_sigma(theta)^-1  (Inverse of stress transformation)
        # T_epsilon_inv(-theta) = T_epsilon(theta) (Strain transformation)

        T_sigma_inv, T_epsilon = _get_transformation_matrices(-angles)

        # We only need the top-left 3x3 block of the transformed compliance matrix (a')
        # to calculate in-plane engineering constants (Ex, Ey, Gxy).
        # a' = T_epsilon @ a @ T_sigma_inv
        a = self.abd[:3, :3]
        a_prime = _apply_transformation(a, T_epsilon, T_sigma_inv)

        # Extract elements from transformed 3x3 compliance blocks
        a00 = a_prime[:, 0, 0]
        a11 = a_prime[:, 1, 1]
        a22 = a_prime[:, 2, 2]

        # Initialize arrays
        Ex = np.zeros_like(a00)
        Ey = np.zeros_like(a11)
        Gxy = np.zeros_like(a22)

        # Vectorized division with zero check
        mask00 = a00 != 0
        Ex[mask00] = 1 / (h * a00[mask00])

        mask11 = a11 != 0
        Ey[mask11] = 1 / (h * a11[mask11])

        mask22 = a22 != 0
        Gxy[mask22] = 1 / (h * a22[mask22])

        results = []
        for i, angle in enumerate(angles):
            results.append({
                "angle": float(angle),
                "Ex": float(Ex[i]),
                "Ey": float(Ey[i]),
                "Gxy": float(Gxy[i])
            })

        return PolarResult(results)
