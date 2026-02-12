"""Setup script for banking-transactions-api package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="banking-transactions-api",
    version="1.0.0",
    author="ESG MBA Team",
    author_email="team@esg-mba.com",
    description="API REST pour l'exposition des données de transactions bancaires",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-team/banking-transactions-api",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pandas>=2.1.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "httpx>=0.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "black>=23.11.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "banking-api=banking_api.main:start",
        ],
    },
    include_package_data=True,
    package_data={
        "banking_api": ["py.typed"],
    },
)
