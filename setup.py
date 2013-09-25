#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='simplemail',
    version='0.1.3',
    description='Simple library for sending e-mails with python',
    author='Cristian Consonni',
    author_email='kikkocristian@gmail.com',
    scripts = ['scripts/simplemail'],
    packages=['simplemail'],
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
