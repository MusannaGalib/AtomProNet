
from setuptools import setup, find_packages

setup(
    name='VASP_Neural_Network_dataset_converter',  # Name of the package
    version='0.1.0',  # Version of the package
    author='Musanna Galib',  # Replace with your name
    author_email='musannagalib@rocketmail.com',  # Replace with your email
    description='A Python package for converting VASP data to extxyz/npz format.',  # Short description of your package
    long_description=open('README.md').read(),  # Long description read from the README.md
    long_description_content_type='text/markdown',  # Type of the long description, markdown is recommended
    url='http://example.com/VASP_Neural_Network_dataset_converter',  # Replace with the URL to your package's repository
    packages=find_packages(),  # Finds all the packages in your project
    install_requires=open('requirements.txt').read().splitlines(),  # List of dependencies, read from requirements.txt
    classifiers=[  # Classifiers give the PyPI users more information about your package
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',  # Minimum version requirement of Python
)
