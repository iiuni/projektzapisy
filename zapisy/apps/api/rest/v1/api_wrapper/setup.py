import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sz_api",
    version="0.0.1",
    author="Mariusz Bielecki",
    author_email="maniekb12@gmail.com",
    description="API wrapper for https://zapisy.ii.uni.wroc.pl/api/v1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iiuni/sz_api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests"],
    python_requires='>=3.7',
)
