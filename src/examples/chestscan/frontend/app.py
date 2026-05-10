# frontend/app.py
# Streamlit radiologist interface for the ChestScan pneumonia detector.
#
# Features:
#   - Chest X-ray file uploader (JPEG/PNG)
#   - POST /predict: diagnosis badge + confidence bar chart for all 3 classes
#   - POST /explain: Grad-CAM three-panel heatmap beside original
#   - Sidebar: real-time backend health check
#   - BACKEND_URL configurable via environment variable

import io
import os

import requests
import streamlit as st
from PIL import Image

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Display labels and badge colours per predicted class
CLASS_DISPLAY = {
    "NORMAL":   ("Normal — No Pneumonia Detected",    "#27ae60"),
    "BACTERIA": ("Bacterial Pneumonia Detected",       "#e74c3c"),
    "VIRUS":    ("Viral Pneumonia Detected",           "#e67e22"),
}

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ChestScan Pneumonia Detector",
    page_icon="🩻",
    layout="wide",
)

st.title("ChestScan Pneumonia Detector")
st.markdown(
    "> **Decision support tool only.** Not a substitute for professional medical diagnosis. "
    "All results must be reviewed by a qualified radiologist before clinical action."
)

# ---------------------------------------------------------------------------
# Sidebar: system status and legend
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("System Status")
    try:
        health_resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            st.success("Backend: Online")
            st.caption(f"Model: `{health_data.get('model_version', 'unknown')}`")
            st.caption(f"Device: `{health_data.get('device', 'unknown')}`")
        else:
            st.error(f"Backend: Unhealthy (HTTP {health_resp.status_code})")
    except requests.exceptions.ConnectionError:
        st.error(f"Backend: Unreachable at {BACKEND_URL}")
        st.stop()

    st.divider()
    st.markdown("**Diagnosis Classes:**")
    for cls, (label, color) in CLASS_DISPLAY.items():
        st.markdown(
            f"<span style='color:{color}; font-size:1.2em;'>■</span> {label}",
            unsafe_allow_html=True,
        )

    st.divider()
    st.caption(
        "Validated on paediatric patients (ages 1–5) from the Kaggle "
        "Chest X-Ray Pneumonia dataset.  Not validated for adult populations."
    )

# ---------------------------------------------------------------------------
# Main: image upload
# ---------------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a chest X-ray image (JPEG or PNG, max 10 MB)",
    type=["jpg", "jpeg", "png"],
    help="Anterior-posterior (AP) chest X-ray from a paediatric patient.",
)

if uploaded_file is not None:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Uploaded Image")
        pil_image = Image.open(uploaded_file)
        st.image(pil_image, caption="Input chest X-ray", use_column_width=True)

    # Read raw bytes for API calls (file pointer must be reset after PIL.open)
    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()

    with col2:
        st.subheader("Analysis Results")
        analyse_btn = st.button("Run Analysis", type="primary", use_container_width=True)

        if analyse_btn:
            with st.spinner("Classifying image..."):
                try:
                    pred_resp = requests.post(
                        f"{BACKEND_URL}/predict",
                        files={"file": (uploaded_file.name, image_bytes, uploaded_file.type)},
                        timeout=30,
                    )
                    pred_resp.raise_for_status()
                    st.session_state["last_prediction"]  = pred_resp.json()
                    st.session_state["image_bytes"]      = image_bytes
                    st.session_state["image_name"]       = uploaded_file.name
                    st.session_state["image_type"]       = uploaded_file.type
                    # Clear stale heatmap when a new image is analysed
                    st.session_state.pop("last_heatmap", None)
                except requests.exceptions.RequestException as exc:
                    st.error(f"Prediction request failed: {exc}")
                    st.stop()

        result = st.session_state.get("last_prediction", {})
        if result:
            pred_class = result.get("diagnosis", "")
            # Extract internal key from display name for colour lookup
            internal_key = pred_class.split()[0].upper()
            if "Bacterial" in pred_class:
                internal_key = "BACTERIA"
            elif "Viral" in pred_class:
                internal_key = "VIRUS"
            elif "Normal" in pred_class:
                internal_key = "NORMAL"

            confidence = result.get("confidence", 0.0)
            probs      = result.get("probabilities", {})
            pred_id    = result.get("prediction_id", result.get("model_version", ""))

            # Diagnosis badge
            label, color = CLASS_DISPLAY.get(internal_key, (pred_class, "#7f8c8d"))
            st.markdown(
                f"<h3 style='color:{color}; margin-top:0;'>{label}</h3>",
                unsafe_allow_html=True,
            )
            st.metric("Confidence", f"{confidence:.1%}")

            # Class probability bars
            st.markdown("**Class Probabilities:**")
            for cls_key in ["NORMAL", "BACTERIA", "VIRUS"]:
                display_label, bar_color = CLASS_DISPLAY[cls_key]
                prob = probs.get(cls_key, 0.0)
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    st.caption(display_label.split("—")[0].strip())
                with col_b:
                    st.progress(float(prob), text=f"{prob:.1%}")

            if pred_id:
                st.caption(f"Model: `{str(pred_id)[:60]}`")

    # -----------------------------------------------------------------------
    # Grad-CAM explainability section
    # -----------------------------------------------------------------------
    st.divider()
    st.subheader("Explainability: Grad-CAM Heatmap")
    st.caption(
        "Grad-CAM highlights the regions of the X-ray that most influenced the "
        "model's prediction.  Clinically meaningful heatmaps should highlight areas "
        "of opacity or consolidation within the lung fields — not image borders or annotations."
    )

    explain_btn = st.button("Generate Explanation", use_container_width=True)

    if explain_btn:
        img_bytes = st.session_state.get("image_bytes", image_bytes)
        img_name  = st.session_state.get("image_name",  uploaded_file.name)
        img_type  = st.session_state.get("image_type",  uploaded_file.type)
        with st.spinner("Generating Grad-CAM heatmap (10–30 seconds)..."):
            try:
                explain_resp = requests.post(
                    f"{BACKEND_URL}/explain",
                    files={"file": (img_name, img_bytes, img_type)},
                    timeout=60,
                )
                explain_resp.raise_for_status()
                st.session_state["last_heatmap"] = explain_resp.content
            except requests.exceptions.RequestException as exc:
                st.error(f"Explanation request failed: {exc}")
                st.stop()

    heatmap_bytes = st.session_state.get("last_heatmap")
    if heatmap_bytes:
        st.image(
            heatmap_bytes,
            caption="Grad-CAM: Original X-Ray | Heatmap | Overlay",
            use_column_width=True,
        )
        st.download_button(
            label="Download Heatmap (PNG)",
            data=heatmap_bytes,
            file_name="gradcam_heatmap.png",
            mime="image/png",
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "ChestScan Pneumonia Detector — trained on the Kaggle Chest X-Ray Pneumonia dataset "
    "(Guangzhou Women and Children's Medical Centre).  "
    "Validated on paediatric patients only.  Not validated for adult populations."
)
