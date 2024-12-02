from setuptools import setup, find_packages

from osintkit.__version__ import __version__

import os
scriptpath = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(scriptpath, 'requirements-kit.txt')) as f:
    install_requires = f.read().splitlines()

setup(
    name='osintkit',
    version=__version__,
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "osintkit = osintkit.main:main"
        ]
    },
    author='bitdruid',
    author_email='bitdruid@outlook.com',
    description='A Python library for my OSINT-related projects.',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)