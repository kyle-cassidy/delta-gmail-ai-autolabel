# PaLIGemma Model Deployment

This repository contains scripts for deploying and using Google's PaLIGemma model on Vertex AI.

## Prerequisites

1. Google Cloud Project with billing enabled
2. Google Cloud Storage bucket
3. Python 3.11 or later
4. Required permissions:
   - Vertex AI API enabled
   - Storage Admin role
   - Vertex AI User role

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create and activate a Python virtual environment:
```bash
python3.11 -m venv .venv-3.11
source .venv-3.11/bin/activate  # On Unix/macOS
# OR
.venv-3.11\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"  # or your preferred region
export BUCKET_URI="gs://your-bucket-name"
export MODEL_PATH_PREFIX="gs://your-bucket-name/models/paligemma"
```

## Usage

1. Accept the PaLIGemma model agreement:
   - Open the [PaLIGemma model card](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/363)
   - Review and accept the agreement
   - Copy the provided GCS URI containing the model artifacts

2. Copy model artifacts to your bucket:
```bash
gsutil -m cp -R <provided-gcs-uri>/* $MODEL_PATH_PREFIX
```

3. Run the deployment script:
```bash
python notebooks/predict.py
```

## Model Capabilities

The deployed PaLIGemma model can perform:
- Visual Question Answering (VQA)
- Image Captioning
- Optical Character Recognition (OCR)
- Object Detection

## Cleanup

To avoid unnecessary charges, remember to:
1. Undeploy models from endpoints
2. Delete endpoints
3. Delete model artifacts from your bucket

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details. 