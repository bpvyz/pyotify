import setuptools
import re


def read_file(filename):
    with open(filename) as file:
        return file.read()


version = re.search(r"__version__ = '([0-9.]*)'", read_file('pyotify/__init__.py')).group(1)


setuptools.setup(
    name='pyotify',
    version=version,
    author='Marko Paunovic',
    author_email='paunovic@gmail.com',
    description='Fully-featured library to interact with Spotify Web API',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/paunovic/pyotify',
    packages=setuptools.find_packages(exclude=['tests*']),
    install_requires=read_file('requirements.in'),
    extras_require={
        'tests': {
            'pytest',
        },
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: API Libraries',
    ],
)
