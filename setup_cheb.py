from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

#setup(name="cheb", ext_modules=cythonize('cheb.pyx'),libraries=["gsl", "gslcblas"])

include_gsl_dir = "/usr/include/"
lib_gsl_dir = "/usr/lib/"


ext = Extension("cheb", sources = ["cheb.pyx"],include_dirs=[include_gsl_dir],library_dirs=[lib_gsl_dir],libraries=["gsl", "gslcblas"],extra_compile_args = ["-ffast-math"])

setup(ext_modules=[ext],cmdclass = {'build_ext': build_ext})