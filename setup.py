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
    description='Syncmedia: data file sincronization for Django'
    long_description='Syncmedia is a django application that let you syncronize data files between multiple machines running the same django site.',
    author='Marco Pattaro, Matteo Atti, Michele Totaro, Dario Pavone',
    author_email='mpattaro@gmail.it'
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
# from setuptools import setup, find_packages

# setup(
#     name='django-syncmedia',
#     version='0.1.3',
#     description="Allow sync of static files for load balanced systems.",
#     long_description=('TODO!!!'),
#     keywords='sync, static',
#     author='Matteo Atti, Marco Pattaro',
#     author_email='matteo@***REMOVED***.com',
#     maintainer='Matteo Atti',
#     maintainer_email='matteo@***REMOVED***.com',
#     license='MIT',
#     package_dir={'syncmedia': 'syncmedia'},
#     include_package_data=True,
#     packages=find_packages(),
#     classifiers=[
#         'Development Status :: 5 - Production/Stable',
#         'Environment :: Web Environment',
#         'Framework :: Django',
#         'Intended Audience :: Developers',
#         'Intended Audience :: System Administrators',
#         'License :: OSI Approved :: MIT License',
#         'Operating System :: OS Independent',
#         'Programming Language :: Python',
#         'Programming Language :: Python :: 2.7',
#         'Topic :: Internet :: Log Analysis',
#         'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
#         'Topic :: Security',
#         'Topic :: System :: Logging',
#     ],
#     zip_safe=False,
# )
