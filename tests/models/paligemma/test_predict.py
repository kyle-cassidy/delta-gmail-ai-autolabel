import pytest
import base64
from unittest.mock import patch, MagicMock
from PIL import Image
import io
import os
from src.models.paligemma.predict import (
    _resize_image,
    encode_image,
    make_prediction,
)


@pytest.fixture
def sample_image():
    # Create a simple test image
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def mock_endpoint():
    with patch("google.cloud.aiplatform.Endpoint") as mock:
        yield mock


def test_resize_image_under_max_size():
    # Test image under max size remains unchanged
    img = Image.new("RGB", (512, 512), color="red")
    result = _resize_image(img, max_size=1024)
    resized_img = Image.open(io.BytesIO(result))
    assert resized_img.size == (512, 512)


def test_resize_image_over_max_size():
    # Test image over max size is resized properly
    img = Image.new("RGB", (2048, 1024), color="red")
    result = _resize_image(img, max_size=1024)
    resized_img = Image.open(io.BytesIO(result))
    assert max(resized_img.size) == 1024


def test_encode_image_local_file(tmp_path, sample_image):
    # Test encoding local image file
    image_path = tmp_path / "test.jpg"
    with open(image_path, "wb") as f:
        f.write(sample_image)

    encoded = encode_image(str(image_path))
    assert isinstance(encoded, str)
    assert base64.b64decode(encoded)  # Verify it's valid base64


@patch("requests.get")
def test_encode_image_url(mock_get, sample_image):
    # Test encoding image from URL
    mock_response = MagicMock()
    mock_response.content = sample_image
    mock_get.return_value = mock_response

    encoded = encode_image("http://example.com/image.jpg")
    assert isinstance(encoded, str)
    assert base64.b64decode(encoded)  # Verify it's valid base64


@patch("src.models.paligemma.predict.endpoint")
def test_make_prediction_success(mock_endpoint):
    # Test successful prediction
    instances = [{"image": "base64_string", "prompt": "test prompt"}]
    expected_response = {"predictions": ["test prediction"]}

    mock_endpoint.predict.return_value = expected_response
    response = make_prediction(instances)
    assert response == expected_response
    mock_endpoint.predict.assert_called_once_with(instances=instances)


@patch("src.models.paligemma.predict.endpoint")
def test_make_prediction_retry(mock_endpoint):
    # Test prediction with retries
    instances = [{"image": "base64_string", "prompt": "test prompt"}]
    expected_response = {"predictions": ["test prediction"]}

    mock_endpoint.predict.side_effect = [
        Exception("Temporary error"),
        expected_response,
    ]

    response = make_prediction(instances, max_retries=2, delay=0)
    assert response == expected_response
    assert mock_endpoint.predict.call_count == 2


@patch("src.models.paligemma.predict.endpoint")
def test_make_prediction_failure(mock_endpoint):
    # Test prediction failure after max retries
    instances = [{"image": "base64_string", "prompt": "test prompt"}]
    mock_endpoint.predict.side_effect = Exception("Persistent error")

    with pytest.raises(Exception):
        make_prediction(
            instances, max_retries=0, delay=0
        )  # No retries, just initial attempt
    assert mock_endpoint.predict.call_count == 1  # Only initial attempt


def test_environment_variables():
    # Test required environment variables are set
    required_vars = ["PROJECT_ID", "ENDPOINT_ID", "REGION"]
    for var in required_vars:
        assert os.getenv(var) is not None, f"Missing environment variable: {var}"
