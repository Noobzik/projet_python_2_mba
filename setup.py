"""Configuration du package banking_api."""
from setuptools import setup, find_packages


# Lire le fichier README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


# Lire les dépendances
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]


setup(
    name='banking-transactions-api',
    version='1.0.0',
    author='Camille Thauvin',
    author_email='camille.thauvin@example.com',
    description='API REST pour la gestion et l\'analyse de transactions bancaires',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CamilleThauvin/projet_python_2_mba',
    packages=find_packages(exclude=['tests', 'tests_unittest', 'venv', 'data']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Framework :: FastAPI',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'flake8>=7.0.0',
            'autopep8>=2.0.0',
            'pytest>=9.0.0',
            'pytest-cov>=7.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'banking-api=banking_api.main:app',
        ],
    },
    include_package_data=True,
    package_data={
        'banking_api': ['py.typed'],
    },
    zip_safe=False,
    keywords='banking transactions api fastapi fraud-detection analytics',
    project_urls={
        'Bug Reports': 'https://github.com/CamilleThauvin/projet_python_2_mba/issues',
        'Source': 'https://github.com/CamilleThauvin/projet_python_2_mba',
    },
)
