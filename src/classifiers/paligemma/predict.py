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


def _resize_image(img: Image.Image, max_size: int = 1024) -> bytes:  # type: ignore
    """Resize image if it exceeds max dimensions while maintaining aspect ratio."""
    buffer = io.BytesIO()
    if max(img.size) <= max_size:
        img.save(buffer, format="JPEG")
        return buffer.getvalue()

    ratio = max_size / max(img.size)
    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)  # type: ignore
    resized_img.save(buffer, format="JPEG")
    return buffer.getvalue()


def encode_image(image_path: str) -> str:
    """Encode image to base64 string."""
    if image_path.startswith(("http://", "https://")):
        response = requests.get(image_path)
        img_data = response.content
    else:
        with open(image_path, "rb") as f:
            img_data = f.read()

    img = Image.open(io.BytesIO(img_data))  # type: ignore
    processed_img_data = _resize_image(img)
    return base64.b64encode(processed_img_data).decode("utf-8")


def make_prediction(
    instances: List[Dict[str, Any]], max_retries: int = 3, delay: int = 1
) -> Any:
    """Make a prediction using the PaLIGemma endpoint with retry logic.

    Args:
        instances: List of instances to predict on
        max_retries: Maximum number of retries (not including initial attempt)
        delay: Delay between retries in seconds

    Returns:
        Prediction response from the endpoint

    Raises:
        Exception: If all attempts fail
    """
    last_error = None
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            return endpoint.predict(instances=instances)
        except Exception as e:
            last_error = e
            logging.error(f"Attempt {attempt + 1} failed: {e}")  # noqa: RUF100
            if attempt < max_retries:  # Only sleep if we're going to retry
                time.sleep(delay)
                continue
            raise last_error  # Directly raise the last error instead of creating a new one


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
