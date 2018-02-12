"""

vpl setup file

"""

import glob
from os import path

# always prefer setuptools over distutils
from setuptools import setup


# the location of the setup file
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()


setup(
    name='vpl',
    version='0.0.1',

    description='Video Pipe Line',
    long_description=long_description,

    url='https://github.com/chemicaldevelopment/vpl',

    author='Cade Brown',
    author_email='cade@chemicaldevelopment.us',

    license='GPLv3',

    classifiers=[
        'Topic :: Multimedia :: Video :: Conversion',
    ],

    keywords='video processing',

    packages = ["vpl"],

    test_suite="vpl.tests",

    install_requires=['numpy', 'scipy'],
    extras_require={
        'test': ['coverage'],
        'play': ['simpleaudio']
    },

    #data_files=[('chaudio/samples', glob.glob('chaudio/samples/*')), ('examples', glob.glob("examples/*"))],
    data_files=[],
    
    include_package_data=True,

)
