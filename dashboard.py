import streamlit as str
import requests
from PIL import Image
import io

# Configure the page style
st.set_page_config(page_title="Quantum Cancer Finder", page_icon="🧬", layout="centered")

st.title("🧬 Quantum VQA Cancer Detection Dashboard")
st.write("Upload a clinical or dermatological photo to analyze structural features using a remote hybrid Variational Quantum Algorithm.")

# The URL pointing directly to your live Render backend
API_URL = "https://quantum-machine-learning-cancer-finder.onrender.com/predict"

# File Uploader Widget
uploaded_file = st.file_uploader("Choose a medical image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image to the user
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image Scan", use_column_width=True)
    
    st.write("---")
    
    # Trigger analysis on button click
    if st.button("Execute Quantum VQA Inference", type="primary"):
        with st.spinner("Processing classical features and executing quantum ansatz layers..."):
            try:
                # Convert the PIL image back to raw bytes to send over HTTP
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format)
                img_byte_arr = img_byte_arr.getvalue()
                
                # Format payload as multipart/form-data
                files = {"file": (uploaded_file.name, img_byte_arr, uploaded_file.type)}
                
                # Fire the HTTP request to your live Render app
                response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 1. Display Diagnostic Results
                    if data["is_malignant"]:
                        st.error("🚨 Diagnostic Assessment: Malignant Anomaly Detected")
                    else:
                        st.success("✅ Diagnostic Assessment: Benign / No Anomaly Found")
                        
                    # 2. Display Quantum Performance Metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Quantum Confidence Score", value=f"{data['confidence_score'] * 100:.2f}%")
                    with col2:
                        st.metric(label="QPU Simulation Execution Time", value=f"{data['quantum_execution_time_ms']} ms")
                        
                    # 3. Plot the Extracted Features
                    st.write("### Extracted Quantum Feature Vector (Angles)")
                    st.json(data["feature_vector"])
                    
                else:
                    st.error(f"Backend API returned an error: {response.status_code}")
            except Exception as e:
                st.error(f"Could not connect to the quantum service: {str(e)}")
