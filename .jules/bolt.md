## 2026-02-14 - [Matrix Transformation > Object Re-instantiation]
**Learning:** Re-instantiating `Laminate` objects inside a loop for varying angles is extremely slow (O(Angles * Plies)) due to re-integration of stiffness matrices.
**Action:** Use linear algebra transformations on the aggregated stiffness matrix (`ABD`) instead of re-calculating from plies for geometric rotations (O(Angles)).

## 2026-02-14 - [Failure Envelope Vectorization]
**Learning:** Calculating failure envelopes by looping over angles and plies in Python is extremely slow (O(Angles * Plies)). Vectorizing the stress transformation and failure criteria evaluation across all angles at once yields massive speedups (~85x).
**Action:** Always vectorize laminate analysis across the sweep parameter (angles, loads) instead of looping.
