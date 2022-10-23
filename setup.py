from setuptools import setup, find_packages

setup(
    name="camfwd",
    version="0.1.0",
    author="Douglas Button",
    author_email="doug@paratrix.net",
    description="A tool to control cameras supported by `libgphoto2` from the"
    "command line",
    packages=find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux"),
    install_requires=("gphoto2~=2.3",),
    python_requires="~=3.9"
)
