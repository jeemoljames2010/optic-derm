# OPTIC-DERM Explorer

A lean Streamlit prototype that demonstrates how multimodal optical imaging can be translated into histopathology-relevant tissue descriptors.

## Features

- **Case selection**: Choose a patient and biopsy from the sidebar.
- **Multimodal images**: Side-by-side display of MPM-FLIM, confocal, and RCM placeholder images.
- **Region of interest (ROI)**: Select a region (e.g. epidermis, dermis, lesion center) to generate descriptors.
- **Quantitative descriptors**: Keratin dominance, metabolic state, tissue organization (mock values from interpretable ML).
- **Plain-language explanations** and comparison to normal reference ranges.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown in the terminal (default: http://localhost:8501).

## Project layout

- `app.py` — Streamlit UI and flow.
- `data.py` — Mock patients, biopsies, ROI options, reference ranges, descriptor logic, and placeholder image generation.
