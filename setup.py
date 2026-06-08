
from setuptools import find_packages
from setuptools import setup

setup (
	name="MultiEdit",
	version="v0.1.2",
	description="",
	author="Jonathon Chew",
	author_email="jonchew626@hotmail.com",
	url="",
    package_dir={"": "src"},
	packages=find_packages(exclude=("tests*")),
)
	
