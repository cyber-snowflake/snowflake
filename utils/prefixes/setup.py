from distutils.core import setup
from distutils.extension import Extension

from Cython.Distutils import build_ext

prefix_manager = Extension("prefixes", ["prefixes.pyx"], language="c++")

setup(name="Prefixes Manager", ext_modules=[prefix_manager], cmdclass={"build_ext": build_ext})
