from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="AtomProNet",
    version="0.0.1",
    author="Musanna Galib",
    author_email="galibubc@student.ubc.ca",
    description="A Python package for pre and post-process VASP/Quantum ESPRESSO data into machine learning interatomic potential (MLIP) format.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MusannaGalib/AtomProNet",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "ase",
        "mp-api",
        "scipy",
        "pymatgen",
        "statsmodels",
        "seaborn",
        "scikit-learn",
    ],  # Manually listing dependencies here
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "AtomProNet=AtomProNet.process_and_run_script:main",
        ],
    },
)
