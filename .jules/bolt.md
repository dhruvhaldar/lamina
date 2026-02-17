## 2026-02-14 - [Matrix Transformation > Object Re-instantiation]
**Learning:** Re-instantiating `Laminate` objects inside a loop for varying angles is extremely slow (O(Angles * Plies)) due to re-integration of stiffness matrices.
**Action:** Use linear algebra transformations on the aggregated stiffness matrix (`ABD`) instead of re-calculating from plies for geometric rotations (O(Angles)).

## 2026-02-14 - [Failure Envelope Vectorization]
**Learning:** Calculating failure envelopes by looping over angles and plies in Python is extremely slow (O(Angles * Plies)). Vectorizing the stress transformation and failure criteria evaluation across all angles at once yields massive speedups (~85x).
**Action:** Always vectorize laminate analysis across the sweep parameter (angles, loads) instead of looping.

## 2026-02-16 - [Laminate Creation Vectorization]
**Learning:** `Laminate` creation (specifically the `update` method calculating ABD matrices) using an explicit Python loop over plies is a bottleneck in optimization algorithms that create thousands of laminates. Vectorizing the ply integration reduced creation time by ~54% (0.37ms -> 0.17ms).
**Action:** Vectorize matrix calculations over the ply dimension using numpy broadcasting when integrating stiffness properties.

## 2026-02-27 - [Polar Stiffness Vectorization]
**Learning:** Looping over angles in Python to calculate rotated stiffness properties (`polar_stiffness`) is slow (~30ms for 360 angles). Vectorizing the rotation matrix construction and matrix multiplication using NumPy broadcasting reduces this to ~3ms (~10x speedup).
**Action:** Vectorize geometric transformations of stiffness matrices over the angle dimension using `(N, 3, 3)` stacks.
