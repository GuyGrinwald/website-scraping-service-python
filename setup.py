# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import find_packages, setup

with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="website-scraping-service",
    version="0.1.0",
    description="A website scraper that extracts URLs and links from websites",
    long_description=readme,
    author="Guy Grinwald",
    url="https://github.com/GuyGrinwald/website-scraping-service-python",
    license=license,
    packages=find_packages(exclude=("tests")),
)
