#!/usr/bin/env python3
import os, shutil
import fsLogger
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

pwd = os.path.abspath(os.path.dirname(__file__))

setup(
	name = "python-fslogger",
	version = fsLogger.__version__,
	description = "Logging utility",
	keywords = "logging utility fusion solutions fusionsolutions",
	author = "Andor `iFA88` Rajci - Fusions Solutions KFT",
	author_email = "ifa@fusionsolutions.io",
	url = "https://github.com/FusionSolutions/python-fslogger",
	license = "GPL-3",
	package_dir={"fsLogger": "fsLogger"},
	packages=["fsLogger"],
	long_description=open(os.path.join(pwd, "README.md")).read(),
	long_description_content_type="text/markdown",
	zip_safe=False,
	python_requires=">=3.5.0",
	classifiers=[ # https://pypi.org/pypi?%3Aaction=list_classifiers
		"Development Status :: 4 - Beta",
		"Topic :: Utilities",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
	],
)