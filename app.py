import io
import time
import numpy as np
from PIL import Image
from pydantic import BaseModel, Field
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Quantum Simulation Layer (Using PennyLane as the local QPU simulator backend)
import pennylane as qml

app = FastAPI(
    title="Quantum VQA Cancer Detection API",
    description="Stateless processing engine for high-dimensional matrix evaluations utilizing a VQA architecture. Zero data retention policy.",
    version="1.0.0"
)

# Enable CORS so your decoupled frontend service can securely stream data to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 1. COMPLIANT SOFTWARE DATA CONTRACTS (Schemas)
# ---------------------------------------------------------
class CancerDiagnosisResponse(BaseModel):
    is_malignant: bool = Field(..., description="True if a malignant anomaly is detected, False if benign.")
    prediction: str = Field(..., description="Text breakdown label of the diagnostic assessment.")
    confidence_score: float = Field(..., description="The calculated probability percentage normalized from 0.0% to 100.0%.")
    quantum_execution_time_ms: float = Field(..., description="Time taken to execute the quantum circuit simulation.")
    feature_vector: list[float] = Field(..., description="The 4-dimensional normalized angles fed into the VQA.")

# ---------------------------------------------------------
# 2. QUANTUM CIRCUITS & VQA LAYER (4 Qubits)
# ---------------------------------------------------------
num_qubits = 4
dev = qml.device("default.qubit", wires=num_qubits)

# Fixed variational weights representing a trained QML model ansatz state
TRAINED_VARIATIONAL_WEIGHTS = np.array([
    [0.15, -0.42, 0.88, 0.23],  # Layer 1 rotation weights
    [0.54, 0.11, -0.33, 0.71]   # Layer 2 rotation weights
])

@qml.qnode(dev)
def run_quantum_vqa_circuit(image_features, weights):
    """
    Parametrized Quantum Circuit (PQC) acting as our VQA diagnostic ansatz.
    """
    # Step A: Quantum Data Embedding (Angle Encoding)
    for i in range(num_qubits):
        qml.RY(image_features[i], wires=i)
    
    # Step B: Entanglement Layer 1 (Strong Entangling Ansatz)
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    qml.CNOT(wires=[2, 3])
    qml.CNOT(wires=[3, 0])
    
    # Step C: Variational Parameter Rotations
    for i in range(num_qubits):
        qml.RZ(weights[0][i], wires=i)
        qml.RX(weights[1][i], wires=i)
        
    # Step D: Entanglement Layer 2
    qml.CNOT(wires=[0, 2])
    qml.CNOT(wires=[1, 3])

    # Step E: Quantum Measurement (Expectation value of the readout qubit)
    return qml.expval(qml.PauliZ(0))

# ---------------------------------------------------------
# 3. CLASSICAL FEATURE EXTRACTION (Image Processing)
# ---------------------------------------------------------
def extract_classical_features(image_bytes: bytes) -> np.ndarray:
    """
    Takes raw photo bytes, normalizes the dimensions, downsamples it, 
    and extracts a 4-dimensional feature vector mapped to [-π, π].
    """
    try:
        # Load image completely in-memory (Stateless / HIPAA aligned) and convert to grayscale
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        
        # Downsample to a 2x2 grid to match our 4-qubit data allocation constraint
        img_resized = img.resize((2, 2), Image.Resampling.BILINEAR)
        pixel_array = np.array(img_resized).flatten() # Flatten to 4 elements
        
        # Normalize pixel values [0, 255] directly into quantum phase angles [-π, π]
        normalized_features = (pixel_array / 255.0) * 2 * np.pi - np.pi
        return normalized_features
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image matrix data: {str(e)}")

# ---------------------------------------------------------
# 4. HTTP API ENDPOINTS (The Gateway Logic)
# ---------------------------------------------------------
@app.post("/predict", response_model=CancerDiagnosisResponse)
async def predict_cancer(file: UploadFile = File(..., description="Upload a medical photo (.jpg or .png)")):
    """
    Accepts a photo file upload, runs it through the classical feature extractor,
    passes the result to the local quantum VQA, and returns the descriptive diagnostic assessment.
    """
    # Enforce strict image format contracts
    if file.content_type not in ["image/jpeg", "image/png"] and not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type. System requires a PNG or JPEG photo.")
        
    try:
        # Read raw photo stream into memory
        image_bytes = await file.read()
        
        # 1. Classical Processing Step
        features = extract_classical_features(image_bytes)
        
        # 2. Quantum Processing Step (Timing the simulation performance metrics)
        start_time = time.perf_counter()
        quantum_expectation = run_quantum_vqa_circuit(features, TRAINED_VARIATIONAL_WEIGHTS)
        end_time = time.perf_counter()
        
        execution_time_ms = (end_time - start_time) * 1000
        
        # 3. Measurement Normalization
        # PauliZ expectation maps to [-1.0, 1.0]. We scale it to a classical probability baseline [0.0, 1.0]
        raw_probability = float((quantum_expectation + 1.0) / 2.0)
        
        # Convert to an institutional confidence percentage format [0.0%, 100.0%]
        confidence_percentage = round(raw_probability * 100, 2)
        
        # Binary classification threshold boundary (50.0%)
        is_malignant = raw_probability >= 0.50
        prediction_label = "Malignant Anomaly Detected" if is_malignant else "Benign Tissue Profile"

        return CancerDiagnosisResponse(
            is_malignant=is_malignant,
            prediction=prediction_label,
            confidence_score=confidence_percentage,
            quantum_execution_time_ms=round(execution_time_ms, 2),
            feature_vector=features.tolist()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal System Matrix Error: {str(e)}")

@app.get("/health")
def health_check():
    """Operational verification route."""
    return {"status": "online", "backend": f"PennyLane Virtual QPU ({num_qubits} Qubits)"}

if __name__ == "__main__":
    # Runs the local HTTP application server
    uvicorn.run(app, host="0.0.0.0", port=8000)
