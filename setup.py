from setuptools import setup, find_packages

setup(
    name="pytree",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'pytree=pytree:cli.main',
        ],
    },
    author="Brendan Martin",
    author_email="contact@brmartin.com",
    description="A command-line tool to print directory trees",
    long_description="This tool prints a directory tree structure and allows excluding specific directory contents.",
    license="MIT",
    keywords="tree directory structure",
)