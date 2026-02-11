# Lamina

**Lamina** is a web-based design and analysis suite for **SD2432 Lightweight Design**. It automates the calculations required for designing anisotropic composite structures, specifically focusing on **Classical Lamination Theory (CLT)** and failure analysis.

This tool acts as the "Digital Twin" for the physical manufacturing phase, allowing the engineering team to optimize stacking sequences () to minimize weight while satisfying strength and buckling constraints.

## 📚 Syllabus Mapping (SD2432)

This project addresses the core theoretical requirements of the 20-credit design course:

| Module | Syllabus Topic | Implemented Features |
| --- | --- | --- |
| **Design** | *Technical design* | Laminate Stacking Sequence definition, Material Library (CFRP, GFRP, Honeycomb cores). |
| **Analysis** | *Analyze technical problems* | Full **ABD Matrix** generation, Equivalent Engineering Constants (). |
| **Verification** | *Assess quality of work* | **First Ply Failure (FPF)** analysis using Tsai-Wu, Tsai-Hill, and Max Stress criteria. |
| **Optimization** | *Constrained by a budget* | Weight minimization algorithms constrained by safety factor and manufacturing cost. |
| **Systems** | *Holistic perspective* | Visualization of coupling effects (Extension-Shear, Bending-Twisting) via the B-Matrix. |

## 🚀 Deployment (Vercel)

Lamina runs as a serverless computational engine.

1. **Fork** this repository.
2. Deploy to **Vercel** (Python runtime is auto-detected).
3. Access the **Laminate Designer** at `https://your-lamina.vercel.app`.

## 📊 Artifacts & Structural Analysis

### 1. Stiffness Polars (Anisotropy Visualization)

*Visualizes how the stiffness of the laminate changes with orientation, critical for understanding "Tailored Composites."*

**Code:**

```python
from lamina.materials import CarbonEpoxy
from lamina.clt import Laminate

# Define a Quasi-Isotropic Layup [0/45/-45/90]s
material = CarbonEpoxy(E1=140e9, E2=10e9, G12=5e9, v12=0.3)
laminate = Laminate(material, stack=[0, 45, -45, 90], symmetry=True)

# Calculate Stiffness vs Angle (0 to 360)
results = laminate.polar_stiffness()
results.plot()

```

**Artifact Output:**


> *Figure 1: Stiffness Polar Plot. The plot shows the Young's Modulus  as a function of angle. A circle indicates a Quasi-Isotropic laminate (equal stiffness in all directions), while a "peanut" shape indicates high directionality, typical of UD (Unidirectional) tape layouts.*

### 2. Failure Envelopes (Tsai-Wu)

*Determines the safe operating limits of the material under biaxial stress states.*

**Code:**

```python
from lamina.failure import FailureCriterion

# Generate envelope for Sigma_1 vs Sigma_2
envelope = FailureCriterion.tsai_wu(laminate, limits={'xt': 1500e6, 'xc': 1200e6})
envelope.plot_2

```