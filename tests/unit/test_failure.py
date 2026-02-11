import numpy as np
import pytest
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate
from lamina.failure import FailureCriterion

def test_tsai_wu_envelope_structure():
    mat = CarbonEpoxy()
    lam = Laminate(mat, [0, 45, -45, 90], symmetry=True)
    limits = {'xt': 1500e6, 'xc': 1200e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6}

    envelope = FailureCriterion.tsai_wu(lam, limits, num_points=10)
    data = envelope.data

    assert len(data) > 0
    # Should contain tuples of (sx, sy)
    assert isinstance(data[0], tuple)
    assert len(data[0]) == 2
    assert isinstance(data[0][0], float)

def test_max_stress_envelope():
    mat = CarbonEpoxy()
    lam = Laminate(mat, [0, 90], symmetry=True)
    limits = {'xt': 1000e6, 'xc': 1000e6, 'yt': 50e6, 'yc': 50e6, 's': 50e6}

    envelope = FailureCriterion.max_stress(lam, limits, num_points=10)
    data = envelope.data

    assert len(data) > 0

    # For [0/90]s, failure in x direction (angle=0) should be dominated by 0 ply fiber failure
    # Stress concentration factor is roughly 1/2 in each ply if E1>>E2?
    # No, strain is constant.
    # eps = sigma_x / Ex.
    # sigma_1_ply0 = Q11 * eps = Q11 * sigma_x / Ex.
    # Ex approx (E1+E2)/2.
    # Q11 approx E1.
    # sigma_1_ply0 approx E1 * sigma_x / ((E1+E2)/2) approx 2 * sigma_x.
    # So sigma_x failure approx Xt / 2.

    # Let's just check it returns reasonable values (not inf)
    sx = [d[0] for d in data]
    assert max(sx) < 1000e6 # It should be less than material strength because of laminate factor
    assert max(sx) > 100e6 # Should be substantial
