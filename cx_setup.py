import os
from cx_Freeze import setup, Executable

options = {
    'build_dmg': {
        'namespace_packages': ['zope'],
        'includes': ['pkg_resources']
    }
}

executables = [
    Executable('main.py')
]

setup(
    name="teiler",
    description="simple LAN filesharing",
    long_description=open(os.path.join('.', 'README.rst')).read(),
    version='0.1',
    packages=['teiler'],
    license="MIT",
    options=options,
    executables=executables
)
