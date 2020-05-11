"""This file is used to deploy the plugin"""
import io
import os
from setuptools import setup

install_requires = ["coverage>=5.1", "pytest>=4.4.0", "pytest-cov"]


def read(filename):
    """This function takes in a filepath and reads the file"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with io.open(filepath, mode="r", encoding="utf-8") as f:
        return f.read()


setup(
    name="pytest-pinpoint",
    version="0.2.2",
    description="A pytest plugin which runs SBFL algorithms to detect faults.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Lancaster Wu",
    author_email="wuj@allegheny.edu",
    url="https://github.com/Generalized-SBFL/pytest-pinpoint",
    license="GNU",
    platforms="any",
    install_requires=install_requires,
    py_modules=["pytest_pinpoint"],
    entry_points={"pytest11": ["pinpoint = pytest_pinpoint"]},
)
