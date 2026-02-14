## 2026-02-14 - [Matrix Transformation > Object Re-instantiation]
**Learning:** Re-instantiating `Laminate` objects inside a loop for varying angles is extremely slow (O(Angles * Plies)) due to re-integration of stiffness matrices.
**Action:** Use linear algebra transformations on the aggregated stiffness matrix (`ABD`) instead of re-calculating from plies for geometric rotations (O(Angles)).
