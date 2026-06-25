## 2025-02-23 - Avoid np.square and chained arithmetic for large vectorized numpy calculations
**Learning:** Replaced `np.square()` and chained operations in Tsai-Wu and Tsai-Hill failure criteria with explicit multiplication (`*`) and in-place assignment operators (`*=`, `+=`). This prevents intermediary NumPy array allocations.
**Action:** Always favor chained in-place operations combined with explicit variable-by-variable multiplication over generic NumPy functions like `np.square()` inside heavy array math loops to boost speed.
