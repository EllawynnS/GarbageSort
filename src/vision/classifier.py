"""Waste image classification with a pinned Hugging Face ViT model."""

from __future__ import annotations

import os

# Let PyTorch fall back to CPU for any operator MPS doesn't support.
# Must be set before torch is imported.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

from pathlib import Path
from typing import Any

import torch
from huggingface_hub import snapshot_download
from PIL import Image, UnidentifiedImageError

MODEL_ID = "watersplash/waste-classification"
MODEL_REVISION = "4f35b7f56ddc109934b53a79280233fb4fdb9009"
SUPPORTED_FORMATS = {"JPEG", "PNG"}

_processor: Any = None
_model: Any = None
_device: torch.device | None = None


def _load_model() -> tuple[Any, Any, torch.device]:
    """Load the pinned model and official processor once, using local cache."""
    global _processor, _model, _device

    if _model is not None and _processor is not None and _device is not None:
        return _processor, _model, _device

    try:
        from transformers import AutoImageProcessor, AutoModelForImageClassification
    except ImportError as error:
        raise RuntimeError(
            "Model dependencies are missing. Install torch, transformers, "
            "safetensors, and Pillow to use the waste classifier."
        ) from error

    try:
        model_path = snapshot_download(
            repo_id=MODEL_ID,
            revision=MODEL_REVISION,
            allow_patterns=[
                "config.json",
                "preprocessor_config.json",
                "model.safetensors",
            ],
        )
        _processor = AutoImageProcessor.from_pretrained(
            model_path, local_files_only=True
        )
        _model = AutoModelForImageClassification.from_pretrained(
            model_path,
            use_safetensors=True,
            local_files_only=True,
        )
        _device = torch.device(
            "mps" if torch.backends.mps.is_available() else "cpu"
        )
        _model.to(_device)
        _model.eval()
    except Exception as error:
        _processor = None
        _model = None
        _device = None
        raise RuntimeError(
            f"Could not load {MODEL_ID} at revision {MODEL_REVISION}: {error}"
        ) from error

    return _processor, _model, _device


def preprocess_image(image: Image.Image, processor: Any) -> dict[str, torch.Tensor]:
    """Convert an image to RGB and apply the model's official processor."""
    return processor(images=image.convert("RGB"), return_tensors="pt")


def classify_waste(image_path: str) -> dict[str, Any]:
    """Classify a JPEG or PNG and print its top prediction and sorted probabilities.

    Percentages are returned at full precision and rounded to one decimal place
    only when printed. The model and processor are cached after first load.
    """
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image file not found: {path}")

    try:
        with Image.open(path) as opened_image:
            if opened_image.format not in SUPPORTED_FORMATS:
                raise ValueError(
                    f"Expected a JPEG or PNG image (got {opened_image.format}): {path}"
                )
            image = opened_image.convert("RGB")
            image.load()
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError(f"Invalid or corrupted image: {path}") from error

    processor, model, device = _load_model()
    inputs = preprocess_image(image, processor)
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}

    with torch.inference_mode():
        logits = model(**inputs).logits
        percentages = torch.softmax(logits, dim=-1)[0] * 100

    labels = model.config.id2label
    sorted_indices = torch.argsort(percentages, descending=True).tolist()
    probabilities = {
        labels[index]: float(percentages[index].item())
        for index in sorted_indices
    }
    predicted_index = sorted_indices[0]
    result = {
        "class": labels[predicted_index],
        "confidence": float(percentages[predicted_index].item()),
        "probabilities": probabilities,
    }

    print(f"Image: {image_path}")
    print(f"\nPredicted class: {result['class']}")
    print(f"Confidence: {result['confidence']:.1f}%")
    print("\nAll class probabilities:")
    for label, probability in probabilities.items():
        print(f"{label}: {probability:.1f}%")
    print("\n========================================")

    return result


# """Waste image classification with a pinned Hugging Face ViT model."""
#
# import torch
# from PIL import Image, UnidentifiedImageError
# from huggingface_hub import snapshot_download
#
# _device: torch.device | None = None
#
# from pathlib import Path
# from typing import Any
#
#
# MODEL_ID = "watersplash/waste-classification"
# MODEL_REVISION = "4f35b7f56ddc109934b53a79280233fb4fdb9009"
#
# _processor: Any = None
# _model: Any = None
# _device: torch.device | None = None
#
#
# def _load_model() -> tuple[Any, Any, torch.device]:
#     """Load the pinned model and official processor once, using local cache."""
#     global _processor, _model, _device
#
#     if _model is not None and _processor is not None and _device is not None:
#         return _processor, _model, _device
#
#     try:
#         from transformers import AutoImageProcessor, AutoModelForImageClassification
#     except ImportError as error:
#         raise RuntimeError(
#             "Model dependencies are missing. Install torch, transformers, "
#             "safetensors, and Pillow to use the waste classifier."
#         ) from error
#
#     try:
#         model_path = snapshot_download(
#             repo_id=MODEL_ID,
#             revision=MODEL_REVISION,
#             allow_patterns=[
#                 "config.json",
#                 "preprocessor_config.json",
#                 "model.safetensors",
#             ],
#         )
#         _processor = AutoImageProcessor.from_pretrained(
#             model_path, local_files_only=True
#         )
#         _model = AutoModelForImageClassification.from_pretrained(
#             model_path,
#             use_safetensors=True,
#             local_files_only=True,
#         )
#         _device = torch.device(
#             "mps" if torch.backends.mps.is_available() else "cpu"
#         )
#         _model.to(_device)
#         _model.eval()
#     except Exception as error:
#         _processor = None
#         _model = None
#         _device = None
#         raise RuntimeError(
#             f"Could not load {MODEL_ID} at revision {MODEL_REVISION}: {error}"
#         ) from error
#
#     return _processor, _model, _device
#
#
# def preprocess_image(image: Image.Image, processor: Any) -> dict[str, torch.Tensor]:
#     """Convert an image to RGB and apply the model's official processor."""
#     return processor(images=image.convert("RGB"), return_tensors="pt")
#
#
# def classify_waste(image_path: str) -> dict[str, Any]:
#     """Classify a JPEG and print its top prediction and sorted probabilities.
#
#     Percentages are returned at full precision and rounded to one decimal place
#     only when printed. The model and processor are cached after first load.
#     """
#     path = Path(image_path)
#     if not path.is_file():
#         raise FileNotFoundError(f"Image file not found: {path}")
#
#     try:
#         with Image.open(path) as opened_image:
#             if opened_image.format != "JPEG":
#                 raise ValueError(f"Expected a JPEG image: {path}")
#             image = opened_image.convert("RGB")
#             image.load()
#     except (UnidentifiedImageError, OSError) as error:
#         raise ValueError(f"Invalid or corrupted JPEG image: {path}") from error
#
#     processor, model, device = _load_model()
#     inputs = preprocess_image(image, processor)
#     inputs = {name: tensor.to(device) for name, tensor in inputs.items()}
#
#     with torch.inference_mode():
#         logits = model(**inputs).logits
#         percentages = torch.softmax(logits, dim=-1)[0] * 100
#
#     labels = model.config.id2label
#     sorted_indices = torch.argsort(percentages, descending=True).tolist()
#     probabilities = {
#         labels[index]: float(percentages[index].item())
#         for index in sorted_indices
#     }
#     predicted_index = sorted_indices[0]
#     result = {
#         "class": labels[predicted_index],
#         "confidence": float(percentages[predicted_index].item()),
#         "probabilities": probabilities,
#     }
#
#     print(f"Image: {image_path}")
#     print(f"\nPredicted class: {result['class']}")
#     print(f"Confidence: {result['confidence']:.1f}%")
#     print("\nAll class probabilities:")
#     for label, probability in probabilities.items():
#         print(f"{label}: {probability:.1f}%")
#     print("\n========================================")
#
#     return result
