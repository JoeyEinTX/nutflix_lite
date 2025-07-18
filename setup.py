#!/usr/bin/env python3
"""
Setup script for Nutflix Common Package
Shared utilities and modules for Nutflix projects
"""

from setuptools import setup, find_packages
import os

# Read README if it exists
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='nutflix_common',
    version='0.1.0',
    author='Nutflix Team',
    author_email='nutflix@example.com',
    description='Shared utilities and modules for Nutflix and Nutflix Lite projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JoeyEinTX/nutflix_lite',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    install_requires=[
        'pyyaml>=6.0',
        'opencv-python>=4.5.0',
        'numpy>=1.21.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'flake8',
        ],
    },
    entry_points={
        'console_scripts': [
            # Add CLI scripts here if needed
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
