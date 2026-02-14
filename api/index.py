from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os

from lamina.materials import Material
from lamina.clt import Laminate
from lamina.failure import FailureCriterion

app = FastAPI()

# Pydantic models
class MaterialModel(BaseModel):
    E1: float
    E2: float
    G12: float
    v12: float
    name: str = "Custom"

class LaminateModel(BaseModel):
    material: MaterialModel
    stack: List[float]
    symmetry: bool = False
    thickness: float = 0.125e-3

class LimitsModel(BaseModel):
    xt: float
    xc: float
    yt: float
    yc: float
    s: float

class FailureRequest(BaseModel):
    laminate: LaminateModel
    limits: LimitsModel

# Helper to create Laminate object
def create_laminate(data: LaminateModel):
    mat = Material(
        E1=data.material.E1,
        E2=data.material.E2,
        G12=data.material.G12,
        v12=data.material.v12,
        name=data.material.name
    )
    return Laminate(mat, data.stack, data.thickness, data.symmetry)

@app.post("/api/calculate")
def calculate(data: LaminateModel):
    lam = create_laminate(data)
    props = lam.properties()
    return {
        "ABD": lam.ABD.tolist(),
        "properties": props
    }

@app.post("/api/polar")
def polar(data: LaminateModel):
    lam = create_laminate(data)
    polar_res = lam.polar_stiffness()
    return polar_res.data

@app.post("/api/failure")
def failure(req: FailureRequest):
    lam = create_laminate(req.laminate)
    # Using Tsai-Wu
    envelope = FailureCriterion.tsai_wu(lam, req.limits.dict())
    return envelope.data

# Serve static files
# In Vercel, static files are usually handled by the platform or placed in public/
# But for local testing, we mount it.
if os.path.exists("public"):
    app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/")
def read_root():
    if os.path.exists("public/index.html"):
        return FileResponse('public/index.html')
    return {"message": "Welcome to Lamina API. Frontend not found."}

@app.get("/{filename}")
def read_file(filename: str):
    base_dir = os.path.abspath("public")
    requested_path = os.path.abspath(os.path.join(base_dir, filename))

    # Verify the path is within the public directory
    if not requested_path.startswith(os.path.join(base_dir, "")):
        return {"error": "Access denied"}

    if os.path.exists(requested_path) and os.path.isfile(requested_path):
        return FileResponse(requested_path)
    return {"error": "File not found"}
