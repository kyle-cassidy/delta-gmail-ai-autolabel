from setuptools import setup, find_packages

setup(
    name="delta-gmail-ai-autolabel",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.9.4",
        "questionary>=2.0.0",
        "pdfminer.six>=20221105",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "doc-labeler=src.cli.cli_doc_labeler2:cli",
        ],
    },
)
