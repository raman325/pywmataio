import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywmataio",
    version="0.0.8",
    author="Raman",
    author_email="7243222+raman325@users.noreply.github.com",
    description="A simple async interface to the WMATA (Washington, DC Public Transit) API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raman325/pywmataio",
    packages=setuptools.find_packages(),
    install_requires=["aiohttp"],
    tests_require=[
        "aioresponses",
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-timeout",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
)
