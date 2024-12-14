from setuptools import setup, find_packages

setup(
    name="htb-operator",
    version="1.0.0",
    packages=find_packages(),
    py_modules=["htb_operator"],
    install_requires=[
        "requests",
        "colorama",
        "pyjwt",
        "tabulate",
        "psutil",
        "pexpect",
        "pyreadline3",
        "python-dateutil",
        "rich",
        "pillow",
        "python-hosts",
        "psutil",
        "beautifulsoup4",
        "tqdm",
        "paramiko"],
    entry_points={
        "console_scripts": [
            "htb-operator=htb_operator:main",
        ],
    },
    description="Command line interface for managing hack the box profile, machines and challenges",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/",
    author="user0x1337",
    author_email="user0x1337@protonmail.com",
    license="MIT",
)