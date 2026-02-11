import numpy as np
import pytest
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate

def test_q_matrix():
    mat = CarbonEpoxy()
    Q = mat.Q()

    denom = 1 - mat.v12 * mat.v21
    assert np.isclose(Q[0,0], mat.E1/denom)
    assert np.isclose(Q[1,1], mat.E2/denom)
    assert np.isclose(Q[0,1], (mat.v12*mat.E2)/denom)
    assert np.isclose(Q[2,2], mat.G12)

def test_symmetric_laminate_abd():
    mat = CarbonEpoxy()
    # [0/90]s -> [0, 90, 90, 0]
    lam = Laminate(mat, [0, 90], symmetry=True)

    # B matrix should be zero for symmetric laminate
    assert np.allclose(lam.B, np.zeros((3,3)))

    # A11 check
    # A = sum(Q_bar * t)
    # Q_bar(0) = Q (since cos(0)=1, sin(0)=0)
    # Q_bar(90): Q11->Q22, Q22->Q11 (roughly, if Q12 small)

    # Detailed check:
    # Q_bar(90):
    # m=0, n=1
    # Q_bar_11 = Q22
    # Q_bar_22 = Q11
    # Q_bar_12 = Q12
    # Q_bar_66 = Q66

    Q = mat.Q()
    t = lam.ply_thickness

    # 2 plies at 0, 2 plies at 90
    expected_A11 = 2*t*Q[0,0] + 2*t*Q[1,1]

    assert np.isclose(lam.A[0,0], expected_A11)

def test_engineering_constants():
    mat = CarbonEpoxy()
    lam = Laminate(mat, [0, 90], symmetry=True)
    props = lam.properties()

    # Check ranges
    assert props['Ex'] > 0
    assert props['Ey'] > 0
    assert props['Gxy'] > 0
    assert 0 < props['vxy'] < 1
