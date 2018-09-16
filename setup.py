import setuptools


setuptools.setup(
    name="qtox",
    version="0.0.4",
    author="Tim Simpson",
    description="Lets you re-run Tox commands faster and in parallel.",
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=["typing"],
    license='MIT',
    entry_points={"console_scripts": ["qtox = qtox.main:main"]},
)
