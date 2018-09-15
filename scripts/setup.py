import setuptools


setuptools.setup(
    name='qtox-self-tests',
    entry_points={
        'console_scripts': [
            "qtox-tests = runner:main",
        ],
    }
)
