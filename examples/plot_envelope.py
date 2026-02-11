from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate
from lamina.failure import FailureCriterion
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend

# Define a Quasi-Isotropic Layup [0/45/-45/90]s
material = CarbonEpoxy(E1=140e9, E2=10e9, G12=5e9, v12=0.3)
laminate = Laminate(material, stack=[0, 45, -45, 90], symmetry=True)

# Generate envelope for Sigma_1 vs Sigma_2
envelope = FailureCriterion.tsai_wu(laminate, limits={'xt': 1500e6, 'xc': 1200e6, 'yt': 50e6, 'yc': 250e6, 's': 70e6})
envelope.plot("example_envelope.png")
print("Envelope plotted to example_envelope.png")
