"""Mock data for OPTIC-DERM Explorer prototype."""

import io
import numpy as np
from PIL import Image

# Patient/biopsy catalog
PATIENTS = [
    {"id": "P001", "label": "Patient 001", "biopsies": ["B001-A", "B001-B"]},
    {"id": "P002", "label": "Patient 002", "biopsies": ["B002-A"]},
    {"id": "P003", "label": "Patient 003", "biopsies": ["B003-A", "B003-B", "B003-C"]},
]

# ROI options (user "selects" a region)
ROI_OPTIONS = [
    {"id": "epidermis", "label": "Epidermis", "description": "Outer layer"},
    {"id": "dermis", "label": "Dermis", "description": "Middle layer"},
    {"id": "lesion_center", "label": "Lesion center", "description": "Center of imaged lesion"},
]

# Normal reference ranges for descriptors (for comparison)
REFERENCE = {
    "keratin_dominance": {"min": 0.15, "max": 0.45, "unit": "ratio", "label": "Keratin dominance"},
    "metabolic_state": {"min": 0.35, "max": 0.75, "unit": "NADH/FAD ratio", "label": "Metabolic state"},
    "tissue_organization": {"min": 0.50, "max": 0.90, "unit": "score", "label": "Tissue organization"},
}

# Mock descriptors per biopsy and ROI (interpretable ML outputs)
def get_descriptors(biopsy_id: str, roi_id: str) -> dict:
    """Return quantitative descriptors for a biopsy and ROI (mock)."""
    # Vary slightly by biopsy and ROI for demo
    rng = np.random.RandomState(hash(biopsy_id + roi_id) % 2**32)
    return {
        "keratin_dominance": float(rng.uniform(0.12, 0.62)),
        "metabolic_state": float(rng.uniform(0.28, 0.82)),
        "tissue_organization": float(rng.uniform(0.40, 0.95)),
    }


def get_explanation(descriptor_key: str, value: float, ref: dict) -> str:
    """Plain-language explanation and comparison to normal."""
    low, high = ref["min"], ref["max"]
    if value < low:
        comp = "below normal range"
        meaning = "May indicate altered differentiation or reduced barrier function."
    elif value > high:
        comp = "above normal range"
        meaning = "May indicate hyperkeratosis or altered metabolic activity."
    else:
        comp = "within normal range"
        meaning = "Consistent with healthy reference tissue."
    return f"{ref['label']}: {value:.2f} ({comp}). {meaning}"


def create_placeholder_image(
    modality: str, width: int = 320, height: int = 240, biopsy_id: str = ""
) -> Image.Image:
    """Generate a placeholder image for a given modality (MPM-FLIM, confocal, RCM)."""
    rng = np.random.RandomState(hash(biopsy_id + modality) % 2**32)
    # Different color schemes per modality
    if modality == "MPM-FLIM":
        # Fluorescence lifetime style: green/teal
        r = (rng.random((height, width)) * 40).astype(np.uint8)
        g = (150 + rng.random((height, width)) * 80).astype(np.uint8)
        b = (120 + rng.random((height, width)) * 60).astype(np.uint8)
    elif modality == "confocal":
        # Reflectance style: grayscale
        g = (80 + rng.random((height, width)) * 120).astype(np.uint8)
        r = b = g
    else:  # RCM
        # Confocal reflectance style: warm gray
        g = (100 + rng.random((height, width)) * 100).astype(np.uint8)
        r = (g + 20).clip(0, 255).astype(np.uint8)
        b = (g - 10).clip(0, 255).astype(np.uint8)
    arr = np.stack([r, g, b], axis=-1)
    # Add simple "tissue-like" gradient; shape (H, W, 1) so it broadcasts with (H, W, 3)
    y = np.linspace(0, 1, height).reshape(-1, 1)
    y = np.broadcast_to(y, (height, width))
    factor = (0.7 + 0.3 * y)[..., np.newaxis]
    arr = (arr * factor).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr)
