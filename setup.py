#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages

with io.open("simplepay/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = '(.*?)'", f.read()).group(1)


setup(
    name='SimplePay',
    version=version,
    packages=find_packages(),
    author='Chris Stranex',
    author_email='chris@stranex.com',
    description='Python API bindings for Simple Pay',
    install_requires=['requests'],
    python_requires='>=3.6',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License'
    ]
)
