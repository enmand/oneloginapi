import os

try:
    from setuptools import setup
except ImportError:
    from distutiparse_requirementsls.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="onelogin",
    version="0.1.2",
    author="Daniel Enman",
    author_email="enmand@gmail.com",
    description=("An API for interacting with OneLogin"),
    license="BSD",
    install_requires=["requests", "lxml==3.4.3"],
    packages=['onelogin'],
    package_dir={'onelogin': "onelogin"},
    long_description=read('README.md'),
)
