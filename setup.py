#!/usr/bin/python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='hexformat',
    description='Library for popular HEX-formats like IntelHex and SRecord',
    long_description_content_type='text/x-rst',
    long_description=read("README.rst"),
    author='Martin Scharrer',
    author_email='martin.scharrer@web.de',
    license='MIT',
    license_files=['LICENSE.txt'],
    packages=['hexformat'],
    test_suite='tests',
    version='0.4.0',
    url='https://github.com/MartinScharrer/hexformat',
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Utilities",
    ],
)
