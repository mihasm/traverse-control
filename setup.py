#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# Get the long description from README.md
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='traverse-control',
    version='1.0.0',
    description='Python control system for ISEL IMC-S8 motorized traverse in wind tunnel measurements',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Miha Smrekar',
    author_email='',  # Removed for privacy
    url='https://github.com/mihasm/traverse-control-',
    packages=find_packages(),
    py_modules=['commands', 'procesiranje', 'wind_interpolation'],
    include_package_data=True,
    install_requires=[
        'pyserial>=3.0',
        'numpy>=1.19.0',
        'scipy>=1.5.0',
        'matplotlib>=3.3.0',
        'mpldatacursor>=0.7',
        'sympy>=1.6.0',
        'tqdm>=4.50.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
    keywords='wind-tunnel measurement motor-control serial isel traverse',
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'traverse-init=commands:initialize_system',
        ],
    },
)