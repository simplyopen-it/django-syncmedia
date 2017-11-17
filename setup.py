from setuptools import setup, find_packages
from syncmedia import __version__

setup(
    name='Syncmedia',
    version=__version__,
    description='Syncmedia: data file sincronization for Django',
    long_description="Syncmedia is a django application that let you syncronize data files between multiple machines running the same django site.",
    author='SimplyOpen',
    author_email='info@simplyopen.org',
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
    packages=find_packages(),
    package_dir={'syncmedia': 'syncmedia'},
    install_requires=[
        'Django>=1.4',
        'psutil'
    ],
)
