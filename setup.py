from setuptools import setup, find_packages

setup(
    name='maputils', 
    version='0.1',
    author='Ben Davis',
    author_email='bendavis78@gmail.com',
    url='http://github.com/bendavis78/maputils/',
    description='Utilities for plotting coordinates on a graphical map',
    packages = find_packages(),
    install_requires=['pyproj'],
)

