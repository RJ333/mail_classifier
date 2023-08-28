#!/usr/bin/env python

from setuptools import setup

setup(
    name="mail_classifier",
    author="Rene Janssen",
    author_email="rjanssen@barracuda.com",
    maintainer="Rene Janssen",  # Add at least a second maintainer (comma separated string)
    maintainer_email="rjanssen@barracuda.com",
    cudasetup=dict(
        repo="folsom/~rjanssen",
    ),
    setup_requires=["cudasetuptools>=0.4"],
    install_requires=[],  # add your dependencies here
    extras_require=dict(
        test=["tox", "tox-wheel"],  # "pytest-mock","pytest-sugar","pytest-cov","hypothesis",
        dev=["pylint", "black", "pre_commit"],  # flake8
    ),
)
