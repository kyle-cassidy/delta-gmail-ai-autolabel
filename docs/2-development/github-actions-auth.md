# GitHub Actions GCP Authentication Guide

## Overview
This guide documents our setup for authenticating GitHub Actions with Google Cloud Platform (GCP) services, specifically for Vertex AI integration.

## Service Account Setup
- **Account**: `github-actions@gmail-ai-autolabel.iam.gserviceaccount.com`
- **Required Roles**:
  - `roles/aiplatform.user`
  - `roles/viewer`

## Authentication Method
We use [google-github-actions/auth@v2](https://github.com/google-github-actions/auth) (v2.1.7) for GCP authentication, which is the official, verified GitHub action from Google.

### Key Features
- Automatic credential file management
- Environment variable export
- Proper cleanup after job completion
- Support for Workload Identity Federation

## Implementation

### 1. Service Account Key
```bash
# Generate service account key
gcloud iam service-accounts keys create "key.json" \
  --iam-account "github-actions@gmail-ai-autolabel.iam.gserviceaccount.com"
```

### 2. GitHub Secrets Setup
1. Add the service account key JSON content to GitHub Secrets as `GOOGLE_CREDENTIALS`
2. Ensure the JSON is properly formatted and complete

### 3. Workflow Configuration
```yaml
- name: Google Auth
  uses: google-github-actions/auth@v2
  with:
    credentials_json: '${{ secrets.GOOGLE_CREDENTIALS }}'
    create_credentials_file: true
    export_environment_variables: true
    cleanup_credentials: true
    service_account: 'github-actions@gmail-ai-autolabel.iam.gserviceaccount.com'
```

### 4. Environment Variables
Required environment variables for GCP services:
```yaml
env:
  PROJECT_ID: gmail-ai-autolabel
  REGION: us-central1
  GOOGLE_CLOUD_PROJECT: gmail-ai-autolabel
```

## Best Practices

### Security
1. Never commit service account keys to the repository
2. Use GitHub Secrets for credential storage
3. Enable automatic credential cleanup
4. Consider implementing Workload Identity Federation for keyless authentication

### Maintenance
1. Regularly rotate service account keys
2. Monitor GitHub Actions logs for authentication issues
3. Keep the auth action version updated
4. Review service account permissions periodically

## Troubleshooting

### Common Issues
1. **Invalid Credentials Format**
   - Ensure JSON is properly formatted
   - Verify complete key content in GitHub Secrets

2. **Permission Issues**
   - Check service account roles
   - Verify project and resource access

3. **Environment Variables**
   - Confirm all required variables are set
   - Check variable inheritance in job steps

## References
- [Google Auth Action Documentation](https://github.com/google-github-actions/auth)
- [GitHub Actions Security Guide](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-google-cloud-platform)
- [GCP Service Accounts](https://cloud.google.com/iam/docs/service-accounts) 