#!/usr/bin/env python

import os

from distutils.core import setup
from richter.version import get_version


def read(filename):
    """Read file contents."""
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='richter',
    version=get_version(),
    description=('Python library for computing Richter local magnitude scales '
                 'on BPPTKG seismic network'),
    long_description=read('README.md'),
    license='BPPTKG',
    author='Indra Rudianto',
    author_email='indrarudianto.official@gmail.com',
    url='https://gitlab.com/bpptkg/bpptkg-richter',
    zip_safe=True,
    packages=['richter'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Science/Research',
        'Natural Language :: Indonesian',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
