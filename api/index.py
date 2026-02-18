from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator, model_validator
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

    @field_validator('E1', 'E2', 'G12')
    @classmethod
    def check_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Must be positive')
        return v

    @model_validator(mode='after')
    def check_poisson(self) -> 'MaterialModel':
        # Check thermodynamic stability condition: v12*v21 < 1
        # v21 = v12 * E2 / E1
        # so v12^2 * E2 / E1 < 1
        # Also catch potential division by zero if E1 is somehow 0 (caught by check_positive, but good to be safe)
        if self.E1 > 0:
            v21 = self.v12 * self.E2 / self.E1
            if self.v12 * v21 >= 1.0:
                raise ValueError('Invalid Poisson ratio: leads to unstable material (v12*v21 >= 1)')
        return self

class LaminateModel(BaseModel):
    material: MaterialModel
    stack: List[float]
    symmetry: bool = False
    thickness: float = 0.125e-3

    @field_validator('stack')
    @classmethod
    def check_stack_size(cls, v: List[float]) -> List[float]:
        if len(v) > 200:
             raise ValueError('Stack too large (max 200 plies)')
        if len(v) == 0:
             raise ValueError('Stack cannot be empty')
        return v

    @field_validator('thickness')
    @classmethod
    def check_thickness(cls, v: float) -> float:
        if v <= 0:
             raise ValueError('Thickness must be positive')
        return v

class LimitsModel(BaseModel):
    xt: float
    xc: float
    yt: float
    yc: float
    s: float

    @field_validator('xt', 'xc', 'yt', 'yc', 's')
    @classmethod
    def check_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Must be positive')
        return v

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
    envelope = FailureCriterion.tsai_wu(lam, req.limits.model_dump())
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
    base_dir = os.path.realpath("public")
    requested_path = os.path.realpath(os.path.join(base_dir, filename))

    # Verify the path is within the public directory
    # os.path.commonpath correctly resolves symlinks and ..
    if os.path.commonpath([base_dir, requested_path]) != base_dir:
        raise HTTPException(status_code=403, detail="Access denied")

    if not (os.path.exists(requested_path) and os.path.isfile(requested_path)):
        raise HTTPException(status_code=404, detail="File not found")

    response = FileResponse(requested_path)
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Allow scripts from self and d3js (CDN), allow unsafe-inline for now as frontend relies on it
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://d3js.org; style-src 'self' 'unsafe-inline'; img-src 'self' data:"

    return response
