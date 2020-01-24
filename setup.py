from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# See https://github.com/pypa/sampleproject/blob/master/setup.py for details
setup(
    name="buildingblocks",
    version="0.1.0",
    description="A collection of MyHDL blocks that can be used to model and build bigger projects",
    long_description=long_description,
    long_description_content_type='text/markdown',
    #url='https://github.com/pypa/sampleproject',  # Optional
    author="Alexander Wranovsky",
    author_email="alex@wranovsky.org",
    packages=['buildingblocks'],
    python_requires=">=3.5",
    install_requires=["myhdl", "colorama"]
)
