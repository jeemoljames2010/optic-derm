"""
OPTIC-DERM Explorer — Interactive dashboard for multimodal optical imaging
translated into histopathology-relevant tissue descriptors.
"""

import streamlit as st
from PIL import Image
import io
from data import (
    PATIENTS,
    ROI_OPTIONS,
    REFERENCE,
    get_descriptors,
    get_explanation,
    create_placeholder_image,
)

# Persist uploaded images per (biopsy_id, modality)
if "uploaded_images" not in st.session_state:
    st.session_state["uploaded_images"] = {}

st.set_page_config(
    page_title="OPTIC-DERM Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a clean, clinical feel
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: 600; color: #1a365d; margin-bottom: 0.5rem; }
    .sub-header { color: #4a5568; font-size: 0.95rem; margin-bottom: 1.5rem; }
    .metric-card { background: #f7fafc; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #3182ce; }
    .ref-range { font-size: 0.85rem; color: #718096; }
    .explanation { font-size: 0.9rem; color: #2d3748; line-height: 1.5; padding: 0.5rem 0; }
    div[data-testid="stSidebar"] { background: #edf2f7; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🔬 OPTIC-DERM Explorer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Translate multimodal optical imaging into histopathology-relevant '
    'tissue descriptors. Select a case and region of interest to view quantitative descriptors '
    'and plain-language explanations with normal reference comparison.</p>',
    unsafe_allow_html=True,
)

# ——— Sidebar: patient & biopsy selection ———
with st.sidebar:
    st.header("Case selection")
    patient_options = [p["label"] for p in PATIENTS]
    patient_choice = st.selectbox("Patient", patient_options, key="patient")
    patient = next(p for p in PATIENTS if p["label"] == patient_choice)
    biopsy_options = patient["biopsies"]
    biopsy_choice = st.selectbox("Biopsy", biopsy_options, key="biopsy")
    st.divider()
    st.header("Region of interest")
    roi_choice = st.radio(
        "Select ROI",
        options=[r["id"] for r in ROI_OPTIONS],
        format_func=lambda x: next(r["label"] for r in ROI_OPTIONS if r["id"] == x),
        key="roi",
    )
    roi_label = next(r["label"] for r in ROI_OPTIONS if r["id"] == roi_choice)
    st.caption(next(r["description"] for r in ROI_OPTIONS if r["id"] == roi_choice))
    st.divider()
    st.header("Upload your data")
    st.caption("Upload images for the selected biopsy. They will replace placeholders below.")
    mod_labels = {"MPM-FLIM": "MPM-FLIM", "confocal": "Confocal", "RCM": "RCM"}
    for mod_key, mod_name in mod_labels.items():
        key = (biopsy_choice, mod_key)
        f = st.file_uploader(mod_name, type=["png", "jpg", "jpeg", "tif", "tiff"], key=f"up_{biopsy_choice}_{mod_key}")
        if f is not None:
            try:
                img = Image.open(io.BytesIO(f.read())).convert("RGB")
                st.session_state["uploaded_images"][key] = img
            except Exception as e:
                st.error(f"Could not load {mod_name}: {e}")
    if st.button("Clear uploaded images for this biopsy", use_container_width=True):
        for k in list(st.session_state["uploaded_images"].keys()):
            if k[0] == biopsy_choice:
                del st.session_state["uploaded_images"][k]
        st.rerun()
    st.divider()
    st.caption("Descriptors update when you change case or ROI.")

# ——— Multimodal images side-by-side ———
st.subheader("Multimodal imaging")
modalities = [
    ("MPM-FLIM", "Multiphoton FLIM (fluorescence lifetime)"),
    ("confocal", "Confocal reflectance"),
    ("RCM", "Reflectance confocal microscopy"),
]
cols = st.columns(3)
for col, (mod, desc) in zip(cols, modalities):
    with col:
        key = (biopsy_choice, mod)
        if key in st.session_state.get("uploaded_images", {}):
            img = st.session_state["uploaded_images"][key]
            st.image(img, use_container_width=True, caption=f"{desc} (your upload)")
        else:
            img = create_placeholder_image(mod, biopsy_id=biopsy_choice)
            st.image(img, use_container_width=True, caption=desc)

# ——— Descriptors: quantitative values, explanations, reference comparison ———
descriptors = get_descriptors(biopsy_choice, roi_choice)
st.divider()
st.subheader(f"Tissue descriptors — ROI: {roi_label}")

for key, value in descriptors.items():
    ref = REFERENCE[key]
    explanation = get_explanation(key, value, ref)
    low, high = ref["min"], ref["max"]
    pct = (value - low) / (high - low) if high > low else 0.5
    pct = max(0, min(1, pct))

    st.markdown(f"**{ref['label']}**")
    st.progress(pct)
    st.caption(f"Value: **{value:.2f}** {ref['unit']} — Reference range: {low:.2f}–{high:.2f}")
    st.markdown(f'<p class="explanation">{explanation}</p>', unsafe_allow_html=True)
    st.markdown("---")

st.info(
    "These descriptors are derived from interpretable machine-learning models applied to "
    "optical signals in the selected region, supporting transparent, clinically meaningful "
    "skin diagnostics."
)
