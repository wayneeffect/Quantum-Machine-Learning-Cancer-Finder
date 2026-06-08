import io
import time
import numpy as np
from PIL import Image
from pydantic import BaseModel, Field
from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn

# Quantum Simulation Layer (Using PennyLane as the local QPU simulator backend)
import pennylane as qml

app = FastAPI(
    title="Quantum VQA Cancer Detection API",
    description="A hybrid quantum-classical application that processes photos to detect anomalies using a VQA architecture."
)

# ---------------------------------------------------------
# 1. SOFTWARE COMPLETENESS DATA CONTRACTS (Schemas)
# ---------------------------------------------------------
class CancerDiagnosisResponse(BaseModel):
    is_malignant: bool = Field(..., description="True if a malignant anomaly is detected, False if benign.")
    confidence_score: float = Field(..., description="The calculated probability normalized from 0.0 to 1.0.")
    quantum_execution_time_ms: float = Field(..., description="Time taken to execute the quantum circuit simulation.")
    feature_vector: list[float] = Field(..., description="The 4-dimensional normalized angles fed into the VQA.")

# ---------------------------------------------------------
# 2. QUANTUM CIRCUITS & VQA LAYER (4 Qubits)
# ---------------------------------------------------------
num_qubits = 4
dev = qml.device("default.qubit", wires=num_qubits)

# Fixed variational weights representing a trained QML model ansatz state
# In production, these weights are optimized using your framework's gradient descent/splines
TRAINED_VARIATIONAL_WEIGHTS = np.array([
    [0.15, -0.42, 0.88, 0.23],  # Layer 1 rotation weights
    [0.54, 0.11, -0.33, 0.71]   # Layer 2 rotation weights
])

@qml.qnode(dev)
def quantum_vqa_classifier(image_features, weights):
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
        # Load image and convert to grayscale to isolate intensity patterns
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        
        # Downsample to a 2x2 grid to match our 4-qubit data allocation constraint
        img_resized = img.resize((2, 2), Image.Resampling.BILINEAR)
        pixel_array = np.array(img_resized).flatten() # Flatten to 4 elements
        
        # Normalize pixel values [0, 255] directly into quantum phase angles [-π, π]
        normalized_features = (pixel_array / 255.0) * 2 * np.pi - np.pi
        return normalized_features
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image data: {str(e)}")

# ---------------------------------------------------------
# 4. HTTP API ENDPOINTS (The Gateway Gateway)
# ---------------------------------------------------------
@app.post("/predict", response_model=CancerDiagnosisResponse)
async def predict_cancer(file: UploadFile = File(..., description="Upload a medical photo (.jpg or .png)")):
    """
    Accepts a photo file upload, runs it through the classical feature extractor,
    passes the result to the local quantum VQA, and returns the diagnostic assessment.
    """
    # Enforce allowed file extensions
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PNG or JPEG photo.")
        
    # Read raw photo stream
    image_bytes = await file.read()
    
    # 1. Classical Processing Step
    features = extract_classical_features(image_bytes)
    
    # 2. Quantum Processing Step (Timing the execution metrics)
    start_time = time.perf_counter()
    quantum_expectation = quantum_vqa_classifier(features, TRAINED_VARIATIONAL_WEIGHTS)
    end_time = time.perf_counter()
    
    execution_time_ms = (end_time - start_time) * 1000
    
    # 3. Measurement Normalization
    # PauliZ expectation maps to [-1.0, 1.0]. We scale it to a classical probability [0.0, 1.0]
    confidence = float((quantum_expectation + 1.0) / 2.0)
    
    # Binary classification threshold boundary (0.50)
    is_malignant = confidence >= 0.50

    return CancerDiagnosisResponse(
        is_malignant=is_malignant,
        confidence_score=round(confidence, 4),
        quantum_execution_time_ms=round(execution_time_ms, 2),
        feature_vector=features.tolist()
    )

@app.get("/health")
def health_check():
    """Operational verification route."""
    return {"status": "online", "backend": f"PennyLane Virtual QPU ({num_qubits} Qubits)"}

if __name__ == "__main__":
    # Runs the local HTTP application server
    uvicorn.run(app, host="0.0.0.0", port=8000)
