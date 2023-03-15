from setuptools import setup, find_packages

setup(
    name="esign",
    version="2.0.0",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "frida",
    ],
    scripts=['bin/esign'],
    package_data={
        '':['js/*.js']
    },
    # entry_points={
    #     "console_scripts": [
    #         "vss-cli = esign:main",
    #     ],
    # },
)
