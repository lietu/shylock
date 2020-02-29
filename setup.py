# -*- coding: utf-8 -*-
from setuptools import setup
from io import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="shylock",
    version="1.0.0",
    description="Distributed async locks in Python, similar to https://github.com/vaidik/sherlock",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/lietu/shylock",
    author="Janne Enberg",
    author_email="janne.enberg@lietu.net",
    packages=["shylock", "shylock.backends"],
    keywords="distributed locking lock",
    python_requires=">=3.6,<4",
    extras_require={"motor": ["motor~=2.0.0"]},
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    project_urls={
        "Bug Reports": "https://github.com/lietu/shylock/issues",
        "Source": "https://github.com/lietu/shylock/",
    },
)
