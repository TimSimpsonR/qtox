import setuptools


setuptools.setup(
    name="qtox",
    version="0.0.1",
    author="Tim Simpson",
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=["typing"],
    classifiers=[],
    entry_points={"console_scripts": ["qtox = qtox.main:main"]},
)
