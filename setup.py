from setuptools import setup, find_packages
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
        pip(["install", "-r", "requirements.txt"])
        # Call parent command
        install.run(self)


setup(
    name="shikoni",
    version="0.1.0",
    description="shikoni base package",
    url="https://github.com/VGDragon/shikoni",
    author="VG Dragon",
    author_email="vg_dragon@hotmail.com",
    packages=find_packages(),
    cmdclass={
        "install": PostInstallCommand,
    }
)
