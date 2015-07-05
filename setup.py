import os

try:
    from setuptools import setup
except ImportError:
    from distutiparse_requirementsls.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="oneloginapi",
    version="0.2.0",
    author="Daniel Enman",
    author_email="enmand@gmail.com",
    description=("An API for interacting with OneLogin"),
    license="BSD",
    install_requires=["requests", "lxml==3.4.3"],
    packages=['oneloginapi'],
    package_dir={'oneloginapi': "oneloginapi"},
    long_description=read('README.md'),
)
