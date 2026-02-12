"""
Setup configuration for Banking Transactions API.

This module provides the setup configuration for packaging the Banking
Transactions API application using setuptools.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="banking-transactions-api",
    version="1.0.0",
    author="MBA2 Team",
    author_email="team@esg-mba.fr",
    description="API REST pour l'exposition des données de transactions bancaires",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/banking-transactions-api",
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.12",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "pandas>=2.2.0",
        "numpy>=1.26.3",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.23.3",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "black>=24.1.1",
            "httpx>=0.26.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "banking-api=app.main:run",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["data/*.csv"],
    },
    zip_safe=False,
)