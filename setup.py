from setuptools import setup, find_packages

setup(
    name="delta-gmail-ai-autolabel",
    version="0.1.0",
    packages=find_packages(),
    package_data={"": ["py.typed"]},
    install_requires=[
        "google-cloud-aiplatform",
        "Pillow",
        "requests",
        "python-dotenv",
        "matplotlib",
        "numpy",
        "types-setuptools",
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
    ],
    python_requires=">=3.8",
)
