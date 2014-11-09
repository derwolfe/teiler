import os
from setuptools import setup


INSTALL_REQUIRES = [
    "twisted",
    "netifaces",
    "klein",
    "mock"
]

setup(
    name="teiler",
    description="simple LAN filesharing",
    long_description=open(os.path.join('.', 'README.rst')).read(),
    version='0.1',
    maintainer="Chris Wolfe",
    maintainer_email="chriswwolfe@gmail.com",
    packages=['teiler'],
    license="MIT",
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=INSTALL_REQUIRES,
    extras_require=dict(
        dev=["coverage", "flake8"]
    ),
    test_suite='tests',
    # py2app
    app=['main.py'],
    setup_requires=['py2app'] + INSTALL_REQUIRES
)
