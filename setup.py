import os, sys
from setuptools import setup, find_packages

setup(
    name="teiler",
    description="simple LAN filesharing",
    long_description= open(os.path.join('.', 'README.rst')).read(),
    version='0.1',
    maintainer="Chris Wolfe",
    maintainer_email="chriswwolfe@gmail.com",
    packages=['teiler'],
    license="MIT",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ] + [
        ("Programming Language :: Python :: %s" % x) for x in
        "2.7".split()],
    install_requires = ["twisted", "netifaces"],
    extras_require = dict(
        dev=["coverage", "pyflakes", "pep8", "flake8"]
    ),
    test_suite='tests'
)
