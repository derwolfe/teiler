import os, sys
from setuptools import find_packages
from cx_Freeze import setup, Executable

if __name__ == "__main__":
    here = os.path.abspath(".")
    README = open(os.path.join(here, 'README.rst')).read()

    install_requires = ["twisted"]

    base = None
    setup(
      name="teiler",
      description="simple LAN filesharing",
      long_description=README,
      version='0.1',
      maintainer="Chris Wolfe",
      maintainer_email="chriswwolfe@gmail.com",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      license="MIT",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        ] + [
            ("Programming Language :: Python :: %s" % x) for x in
                "2.7".split()],
      install_requires=install_requires,
    executables = [Executable("main.py", base=base)]
)

