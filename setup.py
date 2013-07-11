#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup
from syncmedia import __version__

setup(
    name='Syncmedia',
    version=__version__,
    description='Syncmedia: data file sincronization for Django',
    long_description="Syncmedia is a django application that let you syncronize data files between multiple machines running the same django site.",
    author='Marco Pattaro, Matteo Atti, Michele Totaro, Dario Pavone',
    author_email='mpattaro@gmail.it',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
    packages=[
        'syncmedia',
        'syncmedia.management',
        'syncmedia.migrations',
        'syncmedia.commands',
    ],
)
