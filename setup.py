from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discordwave",
    version="0.1.0",
    author="o4pixel",
    description="A modern Python library for Discord bot development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/discordwave",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.7.4",
        "websockets>=10.0",
    ],
    keywords="discord, bot, api, async",
)
