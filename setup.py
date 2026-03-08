from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "cpp_core",
        ["cpp_core/bindings.cpp"],  
        include_dirs=[pybind11.get_include()],
        language="c++",
    ),
]

setup(
    ext_modules=ext_modules,
)
