import numpy as np
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate

def test_polar_stiffness_0_90():
    mat = CarbonEpoxy()
    # Simple laminate [0/90]s
    lam = Laminate(mat, [0, 90], symmetry=True)

    # Calculate base properties
    props_base = lam.properties()

    # Calculate polar stiffness
    polar = lam.polar_stiffness(step=90)
    data = polar.data

    # Check at 0 degrees
    d0 = next(d for d in data if d['angle'] == 0)
    assert np.isclose(d0['Ex'], props_base['Ex'])
    assert np.isclose(d0['Ey'], props_base['Ey'])
    assert np.isclose(d0['Gxy'], props_base['Gxy'])

    # Check at 90 degrees
    # Ex at 90 should be Ey at 0
    d90 = next(d for d in data if d['angle'] == 90)
    assert np.isclose(d90['Ex'], props_base['Ey'])
    assert np.isclose(d90['Ey'], props_base['Ex'])
    # Gxy should be same for orthotropic laminate rotated 90 deg?
    # Gxy depends on A66. A66 is invariant under 90 rotation for orthotropic?
    # Q66 is invariant.
    # Yes, A66' = A66.
    assert np.isclose(d90['Gxy'], props_base['Gxy'])

def test_polar_stiffness_UD():
    # Test Unidirectional laminate
    mat = CarbonEpoxy()
    lam = Laminate(mat, [0])

    polar = lam.polar_stiffness(step=10)

    # At 0, Ex should be E1
    d0 = next(d for d in polar.data if d['angle'] == 0)
    # Note: lam.properties() gives equivalent constants.
    # For single ply, Ex = E1 approx (plane stress).
    # Actually Q11 = E1 / (1-v12v21).
    # A11 = h * Q11.
    # abd = inv(ABD).
    # a11 = 1/A11 (if coupling is zero).
    # Ex = 1/(h * a11) = A11 / h = Q11.
    # So Ex = E1 / (1-v12v21).
    # This is "Plane Stress Modulus" vs "Engineering Modulus".
    # But usually we compare consistency.

    props = lam.properties()
    assert np.isclose(d0['Ex'], props['Ex'])

    # At 90, Ex should be E2 / (1-...) ~ E2
    d90 = next(d for d in polar.data if d['angle'] == 90)
    assert np.isclose(d90['Ex'], props['Ey'])
