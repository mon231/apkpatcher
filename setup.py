import setuptools
from pathlib import Path


CURRENT_FOLDER = Path(__file__).parent
README_PATH = CURRENT_FOLDER / 'README.md'


setuptools.setup(
    name = "apkmod",
    version = "1.3.0",
    author = "Ariel Tubul",
    packages = setuptools.find_packages(),
    long_description=README_PATH.read_text(),
    install_requires = ['requests', 'buildapp'],
    long_description_content_type='text/markdown',
    url = "https://github.com/mon231/apkpatcher/",
    description = "Apk frida-gadget injector script",
    entry_points = {'console_scripts': ['apkmod=apkmod.main:main']}
)
