from mypyc.build import mypycify
from setuptools import setup

setup(ext_modules=mypycify(["exert/__init__.py"]))
