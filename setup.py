from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="tiktok-sayer",
    version="1.0.0",
    author="Saudi Linux",
    author_email="SayerLinux@gmail.com",
    keywords=["tiktok", "osint", "security", "social media"],
    description="An OSINT tool for analyzing TikTok accounts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SaudiLinux/TikTok-Sayer",
    py_modules=["tiktok_sayer"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Internet",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tiktok-sayer=tiktok_sayer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "tiktok_sayer": ["assets/*"],
    },
    data_files=[
        ("assets", ["assets/icon.svg"]),
    ],
)