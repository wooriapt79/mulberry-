"""
Setup script for Mulberry Spirit Score System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mulberry-spirit-score",
    version="1.0.0",
    author="CTO Koda",
    author_email="koda@mulberry.team",
    description="장승배기 정신을 코드로 구현한 자동화 시스템",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mulberry-project/spirit-score",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "spirit-score-api=src.api:main",
        ],
    },
)
