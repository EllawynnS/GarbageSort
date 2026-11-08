"""Image classification using the Hugging Face garbage classification model."""

from pathlib import Path
from typing import NamedTuple

import torch
from PIL import Image, UnidentifiedImageError
from transformers import AutoImageProcessor, AutoModelForImageClassification


MODEL_NAME = "yangy50/garbage-classification"


class Classification(NamedTuple):
    """Predicted class label and confidence as a probability from 0 to 1."""

    label: str
    confidence: float


_processor = None
_model = None


def classify_image(jpeg_path: str | Path) -> Classification:
    """Classify a JPEG and return its most likely label and confidence.

    The Hugging Face model is downloaded the first time this function is called
    and reused for subsequent images. Confidence is the softmax probability of
    the predicted class, not a guarantee of correctness.

    Raises:
        FileNotFoundError: If ``jpeg_path`` does not exist.
        ValueError: If the file is not a readable JPEG image.
    """
    global _processor, _model

    image_path = Path(jpeg_path)
    if not image_path.is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        with Image.open(image_path) as image:
            if image.format != "JPEG":
                raise ValueError(f"Expected a JPEG image: {image_path}")
            rgb_image = image.convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError(f"Could not read JPEG image: {image_path}") from error

    if _model is None or _processor is None:
        _processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
        _model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
        _model.eval()

    inputs = _processor(images=rgb_image, return_tensors="pt")
    with torch.inference_mode():
        logits = _model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1)[0]

    class_index = int(probabilities.argmax().item())
    label = _model.config.id2label[class_index]
    confidence = float(probabilities[class_index].item())
    return Classification(label=label, confidence=confidence)
