import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timeguard-supplymaster",
    version="0.0.14",
    author="Richard Pearce",
    author_email="rjpearce23@gmail.com",
    description="Implementation of the API used by the Timeguard's Supplymaster application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rjpearce/timeguard-supplymaster-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Home Automation",
    ],
    python_requires='>=3.6',
)