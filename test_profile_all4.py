import time
import numpy as np

Ex = np.random.rand(360)
Ey = np.random.rand(360)
Gxy = np.random.rand(360)
angles = np.arange(360)

t0 = time.time()
for _ in range(1000):
    al = angles.tolist()
    xl = Ex.tolist()
    yl = Ey.tolist()
    gl = Gxy.tolist()
    results = [
        {"angle": a, "Ex": x, "Ey": y, "Gxy": g}
        for a, x, y, g in zip(al, xl, yl, gl)
    ]
t1 = time.time()
print(f"New tolist list comp: {t1-t0:.4f}")
