from distutils.cmd import Command
from os import getcwd
from setuptools import setup, find_packages


class InstallCommand(Command):
    description = "make root dir"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import getpass, os, shutil

        user_name = getpass.getuser()
        esign_dir_path = "/Users/" + user_name + "/.esign/"
        if not os.path.exists(esign_dir_path):
            os.makedirs(esign_dir_path)
            shutil.copytree(
                os.path.join(getcwd(), "config"), os.path.join(esign_dir_path, "config")
            )
            shutil.copytree(
                os.path.join(getcwd(), "bin"), os.path.join(esign_dir_path, "bin")
            )
            provisions_path = os.path.join(esign_dir_path, "provisions")
            if not os.path.exists(provisions_path):
                os.makedirs(provisions_path)



setup(
    name="esign",
    description="A command-line tool for re-signing iOS IPA files",
    version="0.9.3",
    license="MIT",
    author="Harlans",
    author_email="2461414445@qq.com",
    url="https://github.com/DargonLee/EasySignIpa",
    python_requires=">=3.7",
    packages=find_packages(),
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
    cmdclass={"install_command": InstallCommand},
)
