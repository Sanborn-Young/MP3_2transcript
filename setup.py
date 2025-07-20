import setuptools

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the contents of your requirements file
with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="mp3-2transcript",
    version="0.1.0",
    author="Sanborn-Young",
    description="A GUI tool to transcribe audio from MP3 files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sanborn-Young/MP3_2transcript",
    project_urls={
        "Bug Tracker": "https://github.com/Sanborn-Young/MP3_2transcript/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    py_modules=["GUIMP3_2transcript"],
    python_requires=">=3.7",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "mp3-2transcript=GUIMP3_2transcript:main",
        ],
    },
)
