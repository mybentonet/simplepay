#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages

with io.open("simplepay/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = '(.*?)'", f.read()).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='SimplePay',
    version=version,
    packages=find_packages(exclude=['docs']),
    author='Chris Stranex',
    author_email='chris@stranex.com',
    description='Python API bindings for Simple Pay',
    long_description=long_description,
    url="https://github.com/cstranex/simplepay/",
    project_urls={
        'Documentation': 'https://cstranex.github.io/simplepay/'
    },
    install_requires=['requests'],
    python_requires='>=3.6',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License'
    ]
)
