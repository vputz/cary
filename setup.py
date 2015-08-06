from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

long_description = """
A simple email bot for installing plugins which do various useful
tasks.  Comes with a simple example command which echoes an email back
to the sender.
"""

setup(
    name='cary',
    version='1.0.0',
    description='a simple "email-bot" framework',
    long_description=long_description,
    url='https://github.com/vputz/cary',
    author='Victor Putz',
    author_email='vputz@nyx.net',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        ],

    keywords='email',

    packages=['cary'],

    install_requires=[],

    extras_require={},

    package_data={},

    data_files=[],

    entry_points={
        'console_scripts': [
            'cary = cary.__main__:main'
            ]
            },
)
