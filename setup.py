import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="Cards",
    version="0.0.1",
    author="Luke Keating Hughes",
    author_email="luke.keating-hughes@capgemini.com",
    description="A package to simulate playing cards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lukekh/...",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
