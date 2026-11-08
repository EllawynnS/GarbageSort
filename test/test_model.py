# to run:  python test/test_model.py

from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image

# 1. Load the processor and model from Hugging Face
model_name = "yangy50/garbage-classification"
processor = ViTImageProcessor.from_pretrained(model_name)
model = ViTForImageClassification.from_pretrained(model_name)

# 2. Load a test image (replace with the path to an image of plastic, paper, metal, etc.)
image_path = "test/images/trashcan.jpg"
image = Image.open(image_path)

# 3. Preprocess and run inference
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits

# 4. Get the predicted class index
predicted_class_idx = logits.argmax(-1).item()

# 5. Print the output label
print(f"Predicted Garbage Class: {model.config.id2label[predicted_class_idx]}")
