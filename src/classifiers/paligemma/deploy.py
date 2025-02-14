#!/usr/bin/env python3

"""Deploy PaLIGemma model to Vertex AI."""

import datetime
import os
import subprocess
from typing import Tuple

from google.cloud import aiplatform

# Initialize variables
PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
REGION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
BUCKET_URI = os.environ.get("BUCKET_URI", "gs://gmail-ai-bucket")
MODEL_PATH_PREFIX = os.environ.get(
    "MODEL_PATH_PREFIX", "gs://gmail-ai-bucket/models/paligemma"
)

# Initialize empty dictionaries for models and endpoints
models, endpoints = {}, {}


def deploy_model(
    model_name: str,
    checkpoint_path: str,
    machine_type: str = "g2-standard-32",
    accelerator_type: str = "NVIDIA_L4",
    accelerator_count: int = 1,
    resolution: int = 224,
) -> Tuple[aiplatform.Model, aiplatform.Endpoint]:
    """Create a Vertex AI Endpoint and deploy the specified model to the endpoint."""
    model_name_with_time = (
        f"{model_name}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    endpoint = aiplatform.Endpoint.create(
        display_name=f"{model_name_with_time}-endpoint"
    )

    SERVE_DOCKER_URI = "us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/jax-paligemma-serve-gpu:20240807_0916_RC00"

    model = aiplatform.Model.upload(
        display_name=model_name_with_time,
        serving_container_image_uri=SERVE_DOCKER_URI,
        serving_container_ports=[8080],
        serving_container_predict_route="/predict",
        serving_container_health_route="/health",
        serving_container_environment_variables={
            "CKPT_PATH": checkpoint_path,
            "RESOLUTION": resolution,
            "MODEL_ID": f"google/{model_name}",
        },
    )
    print(
        f"Deploying {model_name_with_time} on {machine_type} with {accelerator_count} {accelerator_type} GPU(s)."
    )

    # Get the default SERVICE_ACCOUNT
    result = subprocess.run(
        ["gcloud", "projects", "describe", PROJECT_ID], capture_output=True, text=True
    )
    project_number = (
        [line for line in result.stdout.split("\n") if "projectNumber" in line][0]
        .split(":")[1]
        .strip()
        .replace("'", "")
    )
    SERVICE_ACCOUNT = f"{project_number}-compute@developer.gserviceaccount.com"

    model.deploy(
        endpoint=endpoint,
        machine_type=machine_type,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        deploy_request_timeout=1800,
        service_account=SERVICE_ACCOUNT,
        enable_access_logging=True,
        min_replica_count=1,
        sync=True,
        system_labels={"NOTEBOOK_NAME": "model_garden_jax_paligemma_deployment.ipynb"},
    )
    return model, endpoint


def main() -> None:
    """Deploy PaLIGemma model to Vertex AI."""
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)

    # Deploy model
    model_name = "paligemma-224-bfloat16"
    checkpoint_path = os.path.join(MODEL_PATH_PREFIX, "pt_224.bf16.npz")

    models["model"], endpoints["endpoint"] = deploy_model(
        model_name=model_name,
        checkpoint_path=checkpoint_path,
        machine_type="g2-standard-16",
        accelerator_type="NVIDIA_L4",
        accelerator_count=1,
        resolution=224,
    )


if __name__ == "__main__":
    main()
