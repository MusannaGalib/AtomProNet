from setuptools import setup, find_packages
from pathlib import Path


here = Path(__file__).parent
requirements_path = here / "requirements.txt"

if requirements_path.exists():
    with open(requirements_path, encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = []  

setup(
    name="AtomProNet",
    version="0.0.1",
    author="Musanna Galib",
    author_email="galibubc@student.ubc.ca",
    description="A Python package for pre and post-process VASP/Quantum ESPRESSO data into machine learning interatomic potential (MLIP) training format (extxyz or npz).",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MusannaGalib/AtomProNet",
    packages=find_packages(),
    install_requires=requirements,  # Load dynamically
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "AtomProNet=AtomProNet.process_and_run_script:main",
        ],
    },
)
