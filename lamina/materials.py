import numpy as np

class Material:
    """
    Represents an Orthotropic Material.
    """
    def __init__(self, E1, E2, G12, v12, rho=0, name="Material"):
        """
        Initialize the material.

        Args:
            E1 (float): Longitudinal Young's Modulus (Pa)
            E2 (float): Transverse Young's Modulus (Pa)
            G12 (float): In-plane Shear Modulus (Pa)
            v12 (float): Major Poisson's Ratio
            rho (float): Density (kg/m^3)
            name (str): Name of the material
        """
        self.E1 = E1
        self.E2 = E2
        self.G12 = G12
        self.v12 = v12
        # Calculate minor Poisson's ratio v21
        self.v21 = v12 * E2 / E1
        self.rho = rho
        self.name = name
        self._invariants = None

    @property
    def invariants(self):
        """
        Calculate and cache the Tsai-Pagano invariants.

        Returns:
            tuple: (U1, U2, U3, U4, U5)
        """
        if self._invariants is None:
            Q = self.Q()
            Q11 = Q[0, 0]
            Q12 = Q[0, 1]
            Q22 = Q[1, 1]
            Q66 = Q[2, 2]

            U1 = (3*Q11 + 3*Q22 + 2*Q12 + 4*Q66) / 8
            U2 = (Q11 - Q22) / 2
            U3 = (Q11 + Q22 - 2*Q12 - 4*Q66) / 8
            U4 = (Q11 + Q22 + 6*Q12 - 4*Q66) / 8
            U5 = (Q11 + Q22 - 2*Q12 + 4*Q66) / 8
            self._invariants = (U1, U2, U3, U4, U5)

        return self._invariants

    def Q(self):
        """
        Calculate the reduced stiffness matrix Q.

        Returns:
            np.ndarray: 3x3 reduced stiffness matrix.
        """
        denom = 1 - self.v12 * self.v21
        Q11 = self.E1 / denom
        Q22 = self.E2 / denom
        Q12 = (self.v12 * self.E2) / denom
        Q66 = self.G12
        return np.array([
            [Q11, Q12, 0],
            [Q12, Q22, 0],
            [0, 0, Q66]
        ])

class CarbonEpoxy(Material):
    """
    Standard Carbon/Epoxy material properties.
    """
    def __init__(self, E1=140e9, E2=10e9, G12=5e9, v12=0.3, rho=1600):
        super().__init__(E1, E2, G12, v12, rho, "Carbon/Epoxy")

class GlassEpoxy(Material):
    """
    Standard Glass/Epoxy material properties.
    """
    def __init__(self, E1=43e9, E2=10e9, G12=4.5e9, v12=0.29, rho=2000):
        super().__init__(E1, E2, G12, v12, rho, "Glass/Epoxy")
