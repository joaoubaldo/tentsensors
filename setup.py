import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'requirements.txt')) as f:
    requires = f.read().splitlines()
with open(os.path.join(here, 'version')) as f:
    version = f.read().splitlines()[0]

tests_require = requires + [
    'pylint'
]

version = os.getenv('BUILD_VERSION', version)

setup(name='tentsensord',
    version=version,
    description='Tent sensors control service',
    long_description=README + '\n',
    classifiers=[
        "Programming Language :: Python"
    ],
    author='Joao Coutinho',
    author_email='me at joaoubaldo.com',
    url='https://b.joaoubaldo.com',
    keywords='mysensors tent automation',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="tests",
    entry_points={
        'console_scripts':
            ['tentsensord = tentsensord.cli:main']
    }
)
