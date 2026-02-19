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

## 2026-03-01 - [Failure Criteria Memory Bottleneck]
**Learning:** Fully vectorizing `FailureCriterion` calculations across both plies (200) and angles (3600) simultaneously created massive intermediate arrays (5.7MB each), causing memory bandwidth bottlenecks and cache misses that made the vectorized code slower than a simple Python loop for large laminates.
**Action:** Use a hybrid approach: pre-calculate angle-dependent terms (A, B) for unique ply angles, then use a generator to yield stress components ply-by-ply. This avoids large allocations while keeping computational efficiency high (~40% faster than loop).

## 2026-03-05 - [Redundant Geometric Transformations]
**Learning:** Calculating transformation matrices (T_sigma, T_epsilon_inv) repeatedly for different stiffness matrices (A, B, D) with identical angles wastes ~66% of trigonometric computations in polar plots.
**Action:** Factor out transformation matrix construction from the application step. Compute matrices once for the angle array, then reuse them for transforming all stiffness components.
