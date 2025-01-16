import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "PROJECT_ID": "test-project",
            "ENDPOINT_ID": "test-endpoint",
            "REGION": "us-central1",
        },
    ):
        yield


@pytest.fixture
def sample_prediction_request():
    """Sample prediction request data."""
    return {
        "image": "base64_encoded_image",
        "prompt": "What is in this image?",
        "task": "vqa",
        "max_tokens": 100,
        "temperature": 0.7,
    }


@pytest.fixture
def sample_prediction_response():
    """Sample prediction response data."""
    return {
        "predictions": [
            "This image shows a person sitting at a desk working on a computer."
        ]
    }
