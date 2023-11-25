from setuptools import setup

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().split("\n")

setup(
    name='jarvisportal',
    version='1.0.0',
    description='Give Chat GPT access to your terminal',
    author='Tony Lampada',
    py_modules=['jarvisportal'],
    url="https://github.com/tonylampada/jarvisportal",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "jarvisportal=jarvisportal:main",
            "gptexec=gptexec:main",
        ],
    },
    python_requires=">=3.8",
)



# setuptools.setup(
#     name="roboflow",
#     version=version,
#     author="Roboflow",
#     author_email="support@roboflow.com",
#     description="Official Python package for working with the Roboflow API",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/roboflow-ai/roboflow-python",
#     install_requires=install_requires,
#     packages=find_packages(exclude=("tests",)),
#     # create optional [desktop]
#     extras_require={
#         "desktop": ["opencv-python==4.8.0.74"],
#         "dev": ["flake8", "black==22.3.0", "isort", "responses", "twine", "wheel"],
#     },
#     entry_points={
#         "console_scripts": [
#             "roboflowpy=roboflow.roboflowpy:main",
#         ],
#     },
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: Apache Software License",
#         "Operating System :: OS Independent",
#     ],
#     python_requires=">=3.8",
# )
