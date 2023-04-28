import sys
from setuptools import setup
from setuptools.command.install import install
from pip._internal import main as pip


class PostInstallCommand(install):
    """Post-installation command."""
    def run(self):
        # Check if pip is installed
        try:
            __import__("pip")
        except ImportError:
            # Install pip using ensurepip
            import ensurepip
            ensurepip.bootstrap()
            __import__("pip")

        # Install pipenv
        pip(["install", "pipenv"])

        # Install packages from Pipfile.lock
        pipenv_install_cmd = ["pipenv", "install", "--ignore-pipfile"]
        pip(pipenv_install_cmd)

        # Call parent command
        install.run(self)


setup(
    name="shikoni",
    version="1.0",
    description="shikoni base package",
    author="VG Dragon",
    author_email="dragon@vg_dragon.net",
    packages=["shikoni"],
    cmdclass={
        "install": PostInstallCommand,
    }
)
