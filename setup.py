#!/usr/bin/python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='',
    description='Library for popular HEX-formats like IntelHex and SRecord',
    long_description=read("README.rst"),
    author='Martin Scharrer',
    author_email='martin@scharrer-online.de',
    license='GPL v3+',
    packages=['hexformat', 'tests'],
    version='0.1',
    url='https://bitbucket.org/martin_scharrer/hexformat',
    download_url='https://bitbucket.org/martin_scharrer/hexformat/downloads/',
    install_requires=[],
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience:: Developers",
        "Intended Audience:: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Utilities",
    ],
)
