"""
Created on Sun Jul 11 18:55:42 2021
@author: jnguy
"""
from setuptools import find_packages
from setuptools import setup

setup(
      name="checkers_app",
      version ="1.0.0",
      author="ASE",
      packages=["checkers_app"],
      #packages = find_packages(),
      #scripts=[],
      install_requires=[],
      license="MIT",
      description="Checkerboard app for ASE"
      )