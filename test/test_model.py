import sys
from pathlib import Path

# make the project root importable, since this file lives in test/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.vision.classifier import classify_waste

# resolve relative to the project root so it works from any working directory
IMAGES = str(ROOT / "test" / "images" / "can.jpeg")

if __name__ == "__main__":
    result = classify_waste(IMAGES)
    print(result)

