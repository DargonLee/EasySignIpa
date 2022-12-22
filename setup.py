from setuptools import setup, find_packages

setup(
    name="vss_cli",
    version="2.0.0",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "frida",
    ],
    scripts=['bin/vss_cli'],
    package_data={
        '':['js/*.js']
    },
    # entry_points={
    #     "console_scripts": [
    #         "vss-cli = vss_cli:main",
    #     ],
    # },
)
