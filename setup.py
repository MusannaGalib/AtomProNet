
from setuptools import setup, find_packages

setup(
    name='AtomProNet',  
    version='0.0.1',  
    author='Musanna Galib',  
    author_email='galibubc@student.ubc.ca', 
    description='A Python package for converting VASP data to extxyz/npz format.',  
    long_description=open('README.md').read(),  # Long description read from the README.md
    long_description_content_type='text/markdown',  
    url='https://github.com/MusannaGalib/AtomProNet',  
    packages=find_packages(),  
    install_requires=open('requirements.txt').read().splitlines(),  
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
    python_requires='>=3.6',  
)
