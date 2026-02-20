import numpy as np
import pytest
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate
from lamina.optimization import calculate_safety_factor

def test_optimization_correctness():
    """
    Verifies that the vectorized implementation of calculate_safety_factor
    produces the expected result matching the original scalar implementation.
    """
    material = CarbonEpoxy()
    # Use a stack with multiple angles to test all logic paths
    stack = [0, 45, -45, 90] * 5
    laminate = Laminate(material, stack)

    load = {'Nx': 100000, 'Ny': 50000, 'Nxy': 10000}
    limits = {
        'xt': 1500e6, 'xc': 1200e6,
        'yt': 50e6, 'yc': 250e6,
        's': 70e6
    }

    # Baseline value obtained from original implementation
    expected_sf = 5.998767264911595

    sf_calculated = calculate_safety_factor(laminate, load, limits)

    # Check for equality within floating point tolerance
    np.testing.assert_allclose(sf_calculated, expected_sf, rtol=1e-6, err_msg="Vectorized safety factor mismatch")

def test_optimization_linear_case_positive_B():
    """
    Tests the linear case where A_coeff is close to zero and B > 0.
    Ensures that we get a finite safety factor (1/B).
    """
    material = CarbonEpoxy()
    stack = [0]
    laminate = Laminate(material, stack)

    # Very small load to produce small stresses -> small A
    load = {'Nx': 1, 'Ny': 0, 'Nxy': 0}

    # Set limits such that F1 > 0 (Xt < Xc)
    # F1 = 1/Xt - 1/Xc
    limits = {
        'xt': 1000e6, 'xc': 2000e6,
        'yt': 50e6, 'yc': 250e6,
        's': 70e6
    }

    sf = calculate_safety_factor(laminate, load, limits)

    # Should be finite and around 250,000 based on manual calc
    assert sf > 2e5
    assert not np.isinf(sf)
