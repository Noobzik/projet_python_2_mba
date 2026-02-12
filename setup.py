from setuptools import setup, find_packages

setup(
    name="banking_transactions_api",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "pandas",
        "pydantic",
    ],
    python_requires=">=3.12",
)