from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "threedimensions._core",
        ["cpp/core.cpp"],  # change to your real C++ file path
        include_dirs=[pybind11.get_include()],
        language="c++",
    ),
]

setup(
    ext_modules=ext_modules,
)
