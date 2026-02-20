from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crabswarm",
    version="0.1.0",
    author="CrabSwarm Team",
    author_email="crabswarm@example.com",
    description="A 'soulful' multi-agent collaboration framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crabswarm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crabswarm=crabswarm.cli:main",
        ],
    },
)