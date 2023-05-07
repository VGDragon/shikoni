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

with open("README.md") as f:
    long_description = f.read()

setup(
    name="shikoni-test",
    version="0.0.1a1",
    description="Message system for connecting tools on a single or multiple Computer.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/VGDragon/shikoni",
    author="VG Dragon",
    author_email="vg_dragon@hotmail.com",
    license='MIT',
    keywords='message connection connector AI tools',
    project_urls={
        'Github': "https://github.com/VGDragon/shikoni",
    },
    packages=find_packages(include=['shikoni', 'shikoni.*']),
    python_requires='>=3.8',
    cmdclass={
        "install": PostInstallCommand,
    }
)
