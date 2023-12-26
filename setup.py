from setuptools import setup, find_packages

setup(
    name="esign",
    description="A command-line tool for re-signing iOS IPA files",
    version="1.0.0",
    license="MIT",
    author="Harlans",
    author_email="2461414445@qq.com",
    url="https://github.com/DargonLee/EasySignIpa",
    python_requires=">=3.7",
    packages=find_packages(),
    package_data={"esign": ["config/*", "bin/*"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "esign = esign.cli:main",
        ],
    },
)
