#!/usr/bin/env python3

"""PaLIGemma prediction utilities."""

import base64
import io
import re
from typing import Dict, List, Sequence, Tuple, Union, Any, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import requests  # type: ignore
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from PIL import Image
from google.api_core import retry, exceptions
import grpc  # type: ignore
import logging
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get endpoint details from environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")
REGION = os.getenv("REGION")

# Initialize endpoint
ENDPOINT_PATH = f"projects/{PROJECT_ID}/locations/{REGION}/endpoints/{ENDPOINT_ID}"
logger.info(f"Using endpoint: {ENDPOINT_PATH}")

endpoint = aiplatform.Endpoint(ENDPOINT_PATH)


def encode_image(image_path: str) -> str:
    """Encode image to base64 string."""
    if image_path.startswith(("http://", "https://")):
        response = requests.get(image_path)
        img_data = response.content
    else:
        with open(image_path, "rb") as f:
            img_data = f.read()

    # Resize image if needed (Vertex AI has request size limits)
    img = Image.open(io.BytesIO(img_data))  # type: ignore
    if max(img.size) > 1024:
        ratio = 1024.0 / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)  # type: ignore
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_data = buffer.getvalue()

    return base64.b64encode(img_data).decode("utf-8")


def make_prediction(
    instances: List[Dict[str, Any]], max_retries: int = 3, delay: int = 1
) -> Any:
    for attempt in range(max_retries):
        try:
            return endpoint.predict(instances=instances)
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            raise


if __name__ == "__main__":
    # Example usage
    project = "gmail-ai-autolabel"  # Project ID
    endpoint_id = "3233752757731065856"  # Endpoint ID

    # Example image URL
    image_url = "https://storage.googleapis.com/cloud-samples-data/vision/face_detection/celebrity_recognition/sergey.jpg"

    # Example input for PaLIGemma-224-bfloat16
    instances = [
        {
            "image": encode_image(image_url),
            "prompt": "What is in this image?",
            "task": "vqa",
            "max_tokens": 100,
            "temperature": 0.7,
        }
    ]

    try:
        response = make_prediction(instances)
        logging.info(f"Prediction response: {response}")
    except Exception as e:
        logging.error(f"All prediction attempts failed: {e}")
