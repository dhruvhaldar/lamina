import numpy as np
K_all = np.random.rand(5, 3, 3)
eps0 = np.random.rand(3, 10)
try:
    res = K_all @ eps0
    print("Success, shape:", res.shape)
except Exception as e:
    print("Error:", e)
