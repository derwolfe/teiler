import os
from setuptools import setup

setup(
    name="teiler",
    description="simple LAN filesharing",
    long_description=open(os.path.join('.', 'README.rst')).read(),
    version='0.1',
    maintainer="Chris Wolfe",
    maintainer_email="chriswwolfe@gmail.com",
    packages=['teiler', 'teiler.tests'],
    license="MIT",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=["twisted", "netifaces", "klein"],
    extras_require=dict(
        dev=["coverage", "flake8", "mock"]
    ),
    test_suite='teiler.tests'
)
