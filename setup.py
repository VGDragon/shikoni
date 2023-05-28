from setuptools import setup, find_packages
from setuptools.command.install import install



class PostInstallCommand(install):
    """Post-installation command."""
    def run(self):
        import pip
        # Check if pip is installed
        try:
            from pip._internal import main as pip
        except ImportError:
            # Install pip using ensurepip
            import ensurepip
            ensurepip.bootstrap()
            from pip._internal import main as pip

        # Install pipenv
        pip(["install", "-r", "requirements.txt"])
        # Call parent command
        install.run(self)

with open("README.md") as f:
    long_description = f.read()

setup(
    name="shikoni",
    version="0.0.2",
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
    packages=find_packages(),
    python_requires='>=3.8',
    cmdclass={
        "install": PostInstallCommand,
    },
    install_requires=["flask", "requests", "websockets"]
)
