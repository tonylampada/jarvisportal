from setuptools import setup, find_packages

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().split("\n")

setup(
    name='jarvisportal',
    version='1.0.6',
    description='Give Chat GPT access to your terminal',
    author='Tony Lampada',
    packages=find_packages(exclude=("tests",)),
    url="https://github.com/tonylampada/jarvisportal",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "jarvisportal=jarvisportal.jarvisportal:main",
            "gptexec=jarvisportal.gptexec:main",
        ],
    },
    python_requires=">=3.8",
)
