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

## 2026-03-08 - [Safety Factor Calculation Vectorization]
**Learning:** The `calculate_safety_factor` function in optimization loops was iterating over plies in Python, causing significant overhead (36.8ms per call). Fully vectorizing the strain transformation and Tsai-Wu failure criterion evaluation using NumPy broadcasting reduced execution time to ~0.3ms (100x speedup).
**Action:** When evaluating failure criteria across many plies (e.g., in optimization), vectorize operations over the ply dimension to leverage NumPy's efficiency.

## 2026-03-12 - [Invariant-based Stiffness Calculation]
**Learning:** Repeated calculation of ply stiffness matrix `Q_bar` using explicit trigonometric powers (`cos**4`, `sin**4`) is computationally expensive during laminate instantiation (~0.26ms).
**Action:** Use Tsai-Pagano invariants (U1-U5) cached in the `Material` object to compute `Q_bar` components via linear combinations of `cos(2t)` and `cos(4t)`. This reduces operations and speeds up laminate creation by ~2x.

## 2026-03-15 - [ABD Matrix Summation Optimization]
**Learning:** Calculating laminate stiffness matrices (A, B, D) using `np.sum(Q_bars * h, axis=2)` involves broadcasting `(3, 3, N)` * `(N,)` -> `(3, 3, N)`, creating large intermediate arrays. Using a reshaped dot product `(Q_bars.reshape(9, -1) @ h).reshape(3, 3)` avoids this allocation and leverages optimized BLAS routines, providing a ~3.6x speedup for this operation.
**Action:** Prefer matrix multiplication (`@`) over broadcasting and summation for weighted sums of matrices (tensor contraction), especially when the summation axis is large.

## 2026-03-20 - [Precomputed Trigonometric Values]
**Learning:** Redundant calls to `np.cos` and `np.sin` for the same ply angles in different parts of the pipeline (Laminate creation vs. Failure Analysis) add measurable overhead (~12% in safety factor loops). Additionally, using double-angle identities ((2\theta) = c^2 - s^2$) is faster than calling `np.cos(2\theta)`.
**Action:** Compute `cos(theta)` and `sin(theta)` once during Laminate update, store them, and reuse them for both stiffness matrix calculation (via identities) and downstream failure analysis.

## 2026-03-24 - [Direct Compliance Transformation]
**Learning:** Inverting the 6x6 ABD matrix for every angle in a polar plot (O(N * 6^3)) is computationally expensive and unnecessary when only in-plane properties are needed. Transforming the compliance matrix components directly (O(N * 3^3)) using the appropriate transformation rules ($S' = T_{\epsilon} S T_{\sigma}^{-1}$) yields a ~9x speedup.
**Action:** When calculating direction-dependent properties, transform the compliance matrix directly instead of transforming stiffness and inverting, especially if full coupling is not required or can be handled block-wise.

## 2026-03-26 - [Genetic Algorithm Evaluation Cache]
**Learning:** In the Genetic Algorithm implementation for laminate optimization, elitism and crossover/mutation mechanisms cause identical laminate stacks to be evaluated frequently. Calculating the laminate properties, buckling load, and safety factors is computationally expensive, leading to >90% redundant work during standard runs.
**Action:** Use a memoization approach (dictionary with a tuple of the ply stack as the key) to cache stack evaluation results across generations. This directly avoids re-calculating the expensive steps for previously seen stacks.

## 2026-04-03 - [Material Property Q Matrix Cache]
**Learning:** Recalculating the Material Q Matrix continuously inside tight loops caused an observable performance drop.
**Action:** Cache the invariant NumPy matrix using a lazy evaluation property and protect it from mutation with `.setflags(write=False)`.

## 2026-04-03 - [Numpy Array Concatenation Overhead]
**Learning:** Array concatenations inside tight loops like `calculate_safety_factor` add an unnecessary overhead.
**Action:** Prefer instantiating an array with elements already passed in the desired final dimensions (`np.array([a, b, c, 0.0, 0.0, 0.0])`) over concatenating arrays.