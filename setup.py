from setuptools import setup, find_packages

setup(
    name="delta-gmail-ai-autolabel",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-cloud-aiplatform",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "pillow",
        "matplotlib",
        "numpy",
        "requests",
        "python-dotenv",
    ],
    python_requires=">=3.10",
)
