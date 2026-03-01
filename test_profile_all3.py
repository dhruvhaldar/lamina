import time
import numpy as np

Ex = np.random.rand(360)
Ey = np.random.rand(360)
Gxy = np.random.rand(360)
angles = np.arange(360)

t0 = time.time()
for _ in range(1000):
    results = []
    for i, angle in enumerate(angles):
        results.append({
            "angle": float(angle),
            "Ex": float(Ex[i]),
            "Ey": float(Ey[i]),
            "Gxy": float(Gxy[i])
        })
t1 = time.time()
print(f"Orig list: {t1-t0:.4f}")

t0 = time.time()
for _ in range(1000):
    results = [
        {"angle": float(a), "Ex": float(x), "Ey": float(y), "Gxy": float(g)}
        for a, x, y, g in zip(angles, Ex, Ey, Gxy)
    ]
t1 = time.time()
print(f"New list comp: {t1-t0:.4f}")
