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

    c2 = c * c
    s2 = s * s
    cs = c * s
    c2_s2 = c2 - s2

    if np.ndim(theta) == 0:
        # T_sigma (stress transformation)
        T_sigma = np.array([
            [c2, s2, 2*cs],
            [s2, c2, -2*cs],
            [-cs, cs, c2_s2]
        ])

        # T_epsilon_inv (strain transformation inverse)
        T_epsilon_inv = np.array([
            [c2, s2, -cs],
            [s2, c2, cs],
            [2*cs, -2*cs, c2_s2]
        ])
    else:
        # Vectorized case: theta is (N,)
        # Optimization: Pre-allocate target arrays to avoid intermediate (3, 3, N)
        # array construction and .transpose() overhead
        n = theta.size
        T_sigma = np.empty((n, 3, 3))
        T_sigma[:, 0, 0] = c2
        T_sigma[:, 0, 1] = s2
        T_sigma[:, 0, 2] = 2*cs
        T_sigma[:, 1, 0] = s2
        T_sigma[:, 1, 1] = c2
        T_sigma[:, 1, 2] = -2*cs
        T_sigma[:, 2, 0] = -cs
        T_sigma[:, 2, 1] = cs
        T_sigma[:, 2, 2] = c2_s2

        T_epsilon_inv = np.empty((n, 3, 3))
        T_epsilon_inv[:, 0, 0] = c2
        T_epsilon_inv[:, 0, 1] = s2
        T_epsilon_inv[:, 0, 2] = -cs
        T_epsilon_inv[:, 1, 0] = s2
        T_epsilon_inv[:, 1, 1] = c2
        T_epsilon_inv[:, 1, 2] = cs
        T_epsilon_inv[:, 2, 0] = 2*cs
        T_epsilon_inv[:, 2, 1] = -2*cs
        T_epsilon_inv[:, 2, 2] = c2_s2

    return T_sigma, T_epsilon_inv


def _apply_transformation(Q, T_sigma, T_epsilon_inv):
    """
    Applies transformation: Q' = T_sigma @ Q @ T_epsilon_inv.
    Handles broadcasting natively if T matrices are stacked (N, 3, 3).
    """
    # Optimization: Native matmul (@) with broadcasting is significantly faster
    # than np.einsum for these (N, 3, 3) shapes in modern numpy versions.
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
        # Optimization: returns (9, n_plies) array directly
        Q_bars_flat = self._get_Q_bar_from_trig(self.c, self.s)

        # 2. Calculate thickness terms
        zk = self.z_coords[1:]
        zk_1 = self.z_coords[:-1]

        # Optimization: algebraic simplifications are faster than array exponentiation
        h = zk - zk_1
        sum_z = zk + zk_1
        h2 = h * sum_z
        h3 = h * (zk*zk + zk*zk_1 + zk_1*zk_1)

        # 3. Sum over plies (axis 2)
        # Optimization: Use dot product for A, B, and D matrices.
        # This replaces broadcasting which creates large temporary arrays (3, 3, N)
        # and leverages optimized BLAS routines (reshape(9, N) @ (N,)).

        self.A = (Q_bars_flat @ h).reshape(3, 3)
        self.B = 0.5 * (Q_bars_flat @ h2).reshape(3, 3)
        self.D = (1/3) * (Q_bars_flat @ h3).reshape(3, 3)

        # ABD Matrix
        self.ABD = np.empty((6, 6))
        self.ABD[:3, :3] = self.A
        self.ABD[:3, 3:] = self.B
        self.ABD[3:, :3] = self.B
        self.ABD[3:, 3:] = self.D

        # Invalidate cached compliance matrix
        self._abd = None

    @property
    def abd(self):
        """Lazy evaluation of the compliance matrix (inverse of ABD)."""
        if getattr(self, '_abd', None) is None:
            try:
                self._abd = np.linalg.inv(self.ABD)
            except np.linalg.LinAlgError:
                self._abd = np.zeros_like(self.ABD)
        return self._abd

    def _calculate_z_coords(self):
        n_plies = len(self.stack)
        h = self.total_thickness
        # Optimization: np.arange and simple math is significantly faster than np.linspace for small arrays
        z = np.arange(n_plies + 1, dtype=np.float64)
        z *= self.ply_thickness
        z -= h/2
        return z

    def _get_Q_bar(self, angle_deg):
        """
        Calculate transformed stiffness matrix Q_bar for given angles.
        Wrapper around _get_Q_bar_from_trig for backward compatibility.
        """
        theta = np.radians(angle_deg)
        c = np.cos(theta)
        s = np.sin(theta)
        q_bar_flat = self._get_Q_bar_from_trig(c, s)
        if np.ndim(angle_deg) == 0:
            return q_bar_flat.reshape(3, 3)
        return q_bar_flat.reshape(3, 3, -1)

    def _get_Q_bar_from_trig(self, c, s):
        """
        Calculate transformed stiffness matrix Q_bar using precomputed cos(theta) and sin(theta).
        Avoids recomputing trig functions and uses double-angle identities.
        """
        # Use invariants for faster calculation
        U1, U2, U3, U4, U5 = self.material.invariants

        # Calculate double angles from single angles
        # Optimization: Pre-compute repetitive array multiplications to reduce allocation overhead
        cos2 = c*c - s*s
        sin2 = 2 * c * s

        cos4 = cos2*cos2 - sin2*sin2
        sin4 = 2 * cos2 * sin2

        U2_cos2 = U2 * cos2
        U3_cos4 = U3 * cos4
        half_U2_sin2 = 0.5 * U2 * sin2
        U3_sin4 = U3 * sin4

        Q_bar_11 = U1 + U2_cos2 + U3_cos4
        Q_bar_12 = U4 - U3_cos4
        Q_bar_22 = U1 - U2_cos2 + U3_cos4
        Q_bar_16 = half_U2_sin2 + U3_sin4
        Q_bar_26 = half_U2_sin2 - U3_sin4
        Q_bar_66 = U5 - U3_cos4

        # Optimization: Directly populate and return flat array (9, N) to avoid
        # 3x3xN array construction and subsequent .reshape(9, -1) overhead
        n = c.size if np.ndim(c) > 0 else 1
        res = np.empty((9, n))
        res[0] = Q_bar_11
        res[1] = Q_bar_12
        res[2] = Q_bar_16
        res[3] = Q_bar_12
        res[4] = Q_bar_22
        res[5] = Q_bar_26
        res[6] = Q_bar_16
        res[7] = Q_bar_26
        res[8] = Q_bar_66

        return res

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

        # Optimization: Use np.divide instead of manual masking to reduce array loops and boolean array overhead
        h_inv = 1.0 / h

        Ex = np.zeros_like(a00)
        Ey = np.zeros_like(a11)
        Gxy = np.zeros_like(a22)

        np.divide(h_inv, a00, out=Ex, where=a00!=0)
        np.divide(h_inv, a11, out=Ey, where=a11!=0)
        np.divide(h_inv, a22, out=Gxy, where=a22!=0)

        # Optimization: Converting arrays to lists and zipping them in a list comprehension
        # is significantly faster than looping over the arrays and calling float() on each element.
        angles_list = angles.tolist()
        Ex_list = Ex.tolist()
        Ey_list = Ey.tolist()
        Gxy_list = Gxy.tolist()

        results = [
            {"angle": a, "Ex": ex, "Ey": ey, "Gxy": gxy}
            for a, ex, ey, gxy in zip(angles_list, Ex_list, Ey_list, Gxy_list)
        ]

        return PolarResult(results)
