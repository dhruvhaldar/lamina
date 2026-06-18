## 2026-06-09 - [NumPy Matrix Operations Optimization]
**Learning:** In NumPy, direct array instantiation `np.array([a, b])` is noticeably faster than initializing with `np.empty()` and manually assigning rows, due to internal optimizations and reduced overhead. Furthermore, when computing sums of matrix products (`A @ x + B @ y`), using in-place addition (`result = A @ x; result += B @ y`) prevents the allocation of an intermediate array for the final sum, saving memory and improving execution time in tight loops.
**Action:** When constructing arrays from vectors, prefer direct `np.array()` or `np.vstack()` instantiation over manual initialization and assignment. For sequential matrix operations, use in-place operators (`+=`, `*=`) where possible to minimize intermediate array allocations.

## 2026-06-09 - [Strain Invariant Math Optimization]
**Learning:** When computing 2D strain or stress transformations inside tight loops (like in genetic algorithm evaluations), evaluating equations algebraically is heavily impacted by the number of operations. Computing both principal strains independently using trigonometric functions (e.g. `s^2*ex + c^2*ey - c*s*gxy`) requires redundant multiplications.
**Action:** Exploit continuum mechanics invariants. The first strain invariant states that the trace of the strain tensor is constant under rotation (`e1 + e2 = ex + ey`). Thus, once `e1` is computed, `e2` can be derived using a simple subtraction and addition (`e2 = ex + ey - e1`), eliminating multiple floating-point multiplications and generating significant speedup.

## 2026-06-11 - [Buckling Hot Loop Optimization]
**Learning:** In performance-critical tight Python loops, explicitly unpacking arrays/tuples before the loop (e.g. `D11, D12, D22, D66 = D[0,0], D[0,1], D[1,1], D[2,2]`) and completely factoring out mathematical operations like divisions and exponentiations (e.g., using `b_a = b/a; b_a * b_a` instead of `(b/a)**2`) provides substantial cumulative speedups. Additionally, for loops with small bounded execution counts (e.g. `1` to `5`), iterating over a constant tuple `(2, 3, 4, 5)` avoids the overhead of instantiating `range()`.
**Action:** Always pre-calculate and factor out mathematical operations from hot loops. For tight loops with small predefined bounds, replace `range()` calls with explicit tuples.

## $(date +%Y-%m-%d) - [In-place array operations vs Scalar assignments]
**Learning:** Using `np.sqrt(delta, out=delta)` works securely for mutating arrays to avoid allocations, however, it crashes completely if `delta` is a NumPy scalar because scalars are immutable. Functions built to accept arrays and scalars interchangeably cannot freely use the `out=` argument without risking crashes on scalar types.
**Action:** Always verify if a variable could be a scalar or an array in hybrid functions before applying strictly mutating Numpy functions like `np.sqrt(out=)`. For variables that might be scalar, fallback to variable reassignment (`delta = np.sqrt(delta)`), which safely handles both arrays and scalars at minimal overhead.

## 2026-06-18 - [Optimization of Laminate updates]
**Learning:** During the review, I left temporary experimental scripts inside my commits which is unacceptable. In addition, I replaced the arguments given to `_get_Q_bar_from_trig` but forgot to define them during class instantiation or within the class state at all causing a runtime AttributeError.
**Action:** Always delete scratchpad files. Ensure all attributes (`self.c2` etc.) used in an optimization are declared correctly prior to its usage.

## 2026-06-18 - [Optimization of array algebraic difference calculations]
**Learning:** When calculating the difference of cubes or squares for sequential adjacent points in an array (like thickness integrations `zk**3 - zk_1**3`), direct algebraic evaluation `np.square(zk)*zk - np.square(zk_1)*zk_1` creates excessive intermediate temporary arrays and forces multiple redundant passes.
**Action:** Always fully factor the difference formulas using simple arithmetic. For example, `zk^3 - zk_1^3` translates to `h * (sum_z * sum_z - zk * zk_1)` where `h = zk - zk_1` and `sum_z = zk + zk_1`. This simple mathematical substitution yields over 10% speedup by drastically decreasing array operator overhead and avoiding `np.square()`.
