import time
import numpy as np

angles = np.arange(0, 360, 1)
Ex = np.random.rand(360)
Ey = np.random.rand(360)
Gxy = np.random.rand(360)

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
print(f"Original: {t1-t0:.4f}s")

t0 = time.time()
for _ in range(1000):
    angles_l = angles.tolist()
    Ex_l = Ex.tolist()
    Ey_l = Ey.tolist()
    Gxy_l = Gxy.tolist()
    results = [
        {"angle": a, "Ex": ex, "Ey": ey, "Gxy": gxy}
        for a, ex, ey, gxy in zip(angles_l, Ex_l, Ey_l, Gxy_l)
    ]
t1 = time.time()
print(f"List comprehension + zip + tolist: {t1-t0:.4f}s")

t0 = time.time()
for _ in range(1000):
    # What if we create structured array?
    pass
t1 = time.time()
