import streamlit as st
import requests
from PIL import Image
import io

# ---------------------------------------------------------
# 1. PAGE SETUP & INSTITUTIONAL DISCLAIMERS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Quantum Cancer Finder UI",
    page_icon="🧬",
    layout="centered"
)

# DYNAMIC INFRASTRUCTURE ROUTING (Automates Online & Offline Execution)
# Evaluates the host headers to seamlessly switch API routing contexts
current_url = st.context.headers.get("Host", "")

if "render.com" in current_url:
    # Production Cloud Route: Used when running live on the web
    API_URL = "https://quantum-machine-learning-cancer-finder.onrender.com/predict"
else:
    # Desktop Executable Route: Used when running locally as a standalone application package
    API_URL = "http://127.0.0.1:8000/predict"

# Crucial Regulatory Disclaimer Banner for Medical Networks
st.warning("""
⚠️ **RESEARCH USE ONLY — NOT FOR ACTIVE CLINICAL DIAGNOSIS** This software is an open-source proof of concept utilizing a hybrid quantum-classical Variational Quantum Algorithm (VQA) simulation. It has not been evaluated by the FDA or any regulatory body and must not be used as a primary diagnostic instrument in clinical treatment environments.
""")

st.title("🧬 Hybrid Quantum-Classical VQA Analytics")
st.write("Upload a clinical skin scan or cell matrix image to calculate the 4-dimensional quantum feature state vector via remote simulation.")

# ---------------------------------------------------------
# 2. IMAGE CAPTURE INTERFACE
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Select Image Scan (JPEG/PNG)...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image inside the layout immediately
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image Scan", use_column_width=True)
    
    st.markdown("---")
    
    # ---------------------------------------------------------
    # 3. INFERENCE PIPELINE STREAMING EXECUTION
    # ---------------------------------------------------------
    if st.button("Execute Quantum VQA Inference", type="primary"):
        with st.spinner("Streaming matrix arrays to remote QPU simulator..."):
            try:
                # Convert the file in memory back into bytes for transmission
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format)
                img_byte_arr = img_byte_arr.getvalue()
                
                # Construct the multipart/form-data payload contract matching backend specifications
                files = {"file": (uploaded_file.name, img_byte_arr, uploaded_file.type)}
                
                # Stream request over evaluated network protocol path (Cloud vs Localhost)
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # A. Display the Diagnostic Result Flags
                    if data["is_malignant"]:
                        st.error(f"🚨 {data['prediction']}")
                    else:
                        st.success(f"🟢 {data['prediction']}")
                        
                    # B. Display Performance Telemetry Metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Quantum Confidence Score", value=f"{data['confidence_score']:.2f}%")
                    with col2:
                        st.metric(label="QPU Simulation Execution Time", value=f"{data['quantum_execution_time_ms']} ms")
                    
                    # C. Output the Mathematical Translation Visualization Arrays
                    st.subheader("Extracted Quantum Feature Vector (Angles)")
                    st.json(data["feature_vector"])
                    
                else:
                    st.error(f"Backend API Gateway Error (Status {response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"Failed to connect to the Quantum Inference Endpoint: {str(e)}")
