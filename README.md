# Quantum VQA Cancer Detection API 🧬🎛️

A hybrid quantum-classical machine learning application built with FastAPI and PennyLane that processes uploaded photos to detect structural anomalies and cancer probabilities.

A hybrid quantum-classical machine learning (QML) application that processes uploaded photos to detect structural anomalies and cancer probabilities. The core architecture uses a classical computer to compress high-dimensional image data, which is then fed into a Variational Quantum Algorithm (VQA) classifier ansatz running on a 4-qubit register.

A NISQ-optimized hybrid QML diagnostic API. Uses a classical CNN feature extractor to map image tensors into 4-qubit angle-encoded states, executing a Variational Quantum Algorithm (VQA) classifier ansatz.

Designed to run locally as a microservice or scale seamlessly to cloud environments like **Render**.

---

## 🏗️ System Architecture

Because raw photos contain too much data for NISQ-era quantum processors to ingest directly, this application splits the computational workload using a hybrid pipeline:

[ User Uploads Photo (.jpg/.png) ]
│
▼
┌────────────────────────────────────────┐
│ 1. CLASSICAL PREPROCESSING LAYER       │
│ - Normalizes & resizes image tensor    │
│ - Downsamples image to 2x2 grid        │
│ - Extracts 4-element intensity vector  │
└────────────────────────────────────────┘
│
▼  (Mapped to Range [-π, π])
┌────────────────────────────────────────┐
│ 2. QUANTUM VQA ANSATZ (PennyLane)      │
│ - Data Embedding: Angle encoding (Ry)  │
│ - Entanglement: CNOT Ring Topology     │
│ - Variational Rotations: Rx/Rz gates   │
└────────────────────────────────────────┘
│
▼
[ PauliZ Readout Measurement ──> Sigmoid Scaling ]
│
▼
[ JSON Output: Malignant vs. Benign Prediction ]


---

## 🛠️ Features (MoSCoW Matrix Complete)
* **Data Contract Validation:** Powered by `Pydantic` to ensure clean incoming parameters and reliable execution logging.
* **Angle Encoding Feature Map:** Dynamically translates classical pixel intensity arrays straight into quantum state phase rotations ($|\psi\rangle$).
* **Strong Entangling Ansatz:** Applies parametric quantum gate layers to map complex, non-local features that classical vision models can struggle to surface.
* **Zero-Latency Simulation:** Configured natively to use the `pennylane` virtual QPU environment for rapid, low-overhead inference processing.

---

## 🚀 Quick Start (Local Installation)

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/quantum-cancer-detection-app.git](https://github.com/YOUR_GITHUB_USERNAME/quantum-cancer-detection-app.git)
cd quantum-cancer-detection-app
