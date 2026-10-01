"""
Binance Public Data Downloader - Setup Configuration

Installation package for the refactored Binance public data downloader.
Provides both programmatic API and CLI tools for downloading historical market data.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read version from __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'src', 'binance_data_downloader', '__init__.py')
    if os.path.exists(init_path):
        with open(init_path, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.0'

setup(
    name='binance-data-downloader',
    version=get_version(),
    author='Binance',
    author_email='support@binance.com',
    description='Download historical market data from Binance public data archive',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/binance/binance-public-data',
    project_urls={
        'Bug Reports': 'https://github.com/binance/binance-public-data/issues',
        'Source': 'https://github.com/binance/binance-public-data',
    },
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'pandas>=1.3.0',
        'certifi>=2021.5.30',
    ],
    extras_require={
        'config': ['pyyaml>=5.4.1'],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'pytest-mock>=3.6.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
    },
    entry_points={
        'console_scripts': [
            'binance-download=binance_data_downloader.cli.commands:main',
        ],
    },
    keywords='binance cryptocurrency trading data download klines futures',
    include_package_data=True,
    zip_safe=False,
)
