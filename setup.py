import os
import io
import sys
import subprocess
from shutil import rmtree

from setuptools import setup, Command


# Package metadata.

NAME = 'pacumen'
DESCRIPTION = 'Exploring Artificial Intelligence with Pac-Man'
URL = 'http://github.com/jeffnyman/pacumen'
AUTHOR = 'Jeff Nyman'
EMAIL = 'jeffnyman@gmail.com'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = None

here = os.path.abspath(os.path.dirname(__file__))


# Import the README and use it as the long-description. It is critical that
# the MANIFEST.in file lists the README.md file. Otherwise, this will not
# work.

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# This load the package's __version__.py module as a dictionary. Part of the
# strategy here is that the __version__ attribute is part of __init__.py,
# which makes it an attribute of the module, as recommended in PEP 396. This
# does require the version string being reassembled here as part of the about
# dictionary. This enables the following behavior:
#    >>> import quendor
#    >>> print(quendor.__version__)

about = {}

if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
        about['__version__'] = '.'.join(map(str, about['VERSION']))
else:
    about['__version__'] = VERSION


# This class is used to support an upload command. This allows you to do this:
#     $ python3 setup.py upload
# This command will create a universal wheel (and sdist) and upload the package
# to PyPi using Twine. This avoids the need to have a setup.cfg file in place.
# This will also create/upload a new git tag automatically. Do note: that to
# use the 'upload' functionality of this file, you must do the following:
#     $ pip install twine

# One thing to note here is the upload command is apparently going to be
# deprecated by setuptools. See:
# https://github.com/pypa/setuptools/pull/1410

class UploadCommand(Command):
    """ Support setup.py upload. """
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(message):
        """ Custom method to print status updates in bold. """
        print('\033[1m{0}\033[0m'.format(message))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (pure Python) distribution...')

        subprocess.check_call(
            [sys.executable, 'setup.py', 'sdist', 'bdist_wheel']
        )

        self.status('Uploading the package to PyPI via Twine...')
        subprocess.check_call(['twine', 'upload', 'dist/*'])

        self.status('Pushing git tags...')

        subprocess.check_call(
            ['git', 'tag', 'v{0}'.format(about['__version__'])]
        )
        subprocess.check_call(['git', 'push', '--tags'])

        sys.exit()


# This is the standard setup for a Python project.

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='artificial intelligence machine learning'.split(),
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    license='MIT',
    packages=['pacumen'],
    zip_safe=False,
    include_package_data=True,
    python_requires=REQUIRES_PYTHON,
    classifiers=[
        # Reference: <URL:https://pypi.org/pypi?:action=list_classifiers>
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    entry_points={
        'console_scripts': [
            'pacumen=pacumen.__main__:main'
        ],
    },
    cmdclass={
        'upload': UploadCommand
    }
)
