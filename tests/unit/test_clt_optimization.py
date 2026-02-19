
import numpy as np
import pytest
from lamina.clt import _get_transformation_matrices, _apply_transformation, _transform_stiffness, Laminate
from lamina.materials import Material

def test_transformation_matrices_consistency():
    """Verify _get_transformation_matrices and _apply_transformation match _transform_stiffness"""
    angle = 30
    Q = np.eye(3)

    # Old way via _transform_stiffness
    res_old = _transform_stiffness(Q, angle)

    # New way
    T_sigma, T_epsilon_inv = _get_transformation_matrices(angle)
    res_new = _apply_transformation(Q, T_sigma, T_epsilon_inv)

    np.testing.assert_allclose(res_old, res_new, err_msg="Scalar transformation mismatch")

def test_vectorized_transformation_consistency():
    """Verify vectorized transformation matches"""
    angles = np.array([0, 30, 45, 90])
    Q = np.eye(3)

    # Old way via _transform_stiffness
    res_old = _transform_stiffness(Q, angles)

    # New way
    T_sigma, T_epsilon_inv = _get_transformation_matrices(angles)
    res_new = _apply_transformation(Q, T_sigma, T_epsilon_inv)

    np.testing.assert_allclose(res_old, res_new, err_msg="Vectorized transformation mismatch")

def test_polar_stiffness_calls():
    """Ensure polar_stiffness runs without error and returns valid data"""
    mat = Material(E1=140e9, E2=10e9, G12=5e9, v12=0.3)
    lam = Laminate(mat, stack=[0, 45, -45, 90], symmetry=True)

    res = lam.polar_stiffness(step=45)
    assert len(res.data) > 0
    assert 'Ex' in res.data[0]
