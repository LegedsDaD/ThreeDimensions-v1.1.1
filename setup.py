from setuptools import setup, Extension
import pybind11
import sys

extra_compile_args = []

if sys.platform == "win32":
    extra_compile_args = ["/std:c++17"]
else:
    extra_compile_args = ["-std=c++17"]

ext_modules = [
    Extension(
        "_threedimensions_core",
        ["cpp_core/bindings.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=extra_compile_args,
    )
]

setup(ext_modules=ext_modules)
