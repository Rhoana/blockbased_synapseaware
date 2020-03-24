from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy as np



extensions = [
    Extension(
        name = 'anchors',
        include_dirs = [np.get_include()],
        sources = ['anchors.pyx', 'cpp-anchors.cpp', 'cpp-skeletonize.cpp', 'PGMImage/PGMImage.cpp'],
        extra_compile_args = ['-O4', '-std=c++0x'],
        language = 'c++'
    )
]

setup(
    name = 'skeletonize',
    ext_modules = cythonize(extensions)
)
