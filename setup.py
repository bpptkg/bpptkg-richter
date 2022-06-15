#!/usr/bin/env python

import io
import os
import re

from setuptools import find_packages, setup


with io.open("richter/version.py", "rt", encoding="utf-8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)


def read(filename):
    """Read file contents."""
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name="bpptkg-richter",
    version=version,
    description=(
        "Python library for computing Richter local magnitude scales "
        "on BPPTKG seismic network"
    ),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="MIT",
    install_requires=[
        "numpy",
        "python-dateutil",
    ],
    author="BPPTKG",
    author_email="bpptkg@esdm.go.id",
    url="https://github.com/bpptkg/bpptkg-richter",
    zip_safe=False,
    packages=find_packages(exclude=["docs", "tests", "examples"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
