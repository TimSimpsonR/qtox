import pathlib
import setuptools


simple_description = "Lets you re-run Tox commands faster and in parallel."
try:
    with open(pathlib.Path(__file__).parent / "README.rst") as file:
        long_description = file.read()
except BaseException:
    long_description = simple_description


setuptools.setup(
    name="qtox",
    version="0.0.6",
    author="Tim Simpson",
    description="Lets you re-run Tox commands faster and in parallel.",
    long_description=long_description,
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=["typing"],
    license="MIT",
    entry_points={"console_scripts": ["qtox = qtox.main:main"]},
)
