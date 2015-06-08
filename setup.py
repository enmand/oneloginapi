import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="onelogin",
    version="0.0.1",
    author="Daniel Enman",
    author_email="enmand@gmail.com",
    description=("An API for interacting with OneLogin"),
    license="BSD",
    packages=['onelogin'],
    long_description=read('README.md'),
)
