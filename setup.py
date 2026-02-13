"""Configuration setup pour le package banking-transactions-api."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="banking-transactions-api",
    version="1.0.0",
    author="Seynabou, Mame Diarra, Mathis",
    description="API REST pour transactions bancaires",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pandas>=2.2.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "httpx>=0.26.0",
            "black>=24.0.0",
            "isort>=5.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "banking-api=banking_api.main:run",
        ],
    },
)
