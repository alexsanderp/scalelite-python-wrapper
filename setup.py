import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scalelite",
    version="0.0.1",
    author='Alexsander Pereira',
    author_email='alexsander.pereira@icloud.com',
    description=u'A Python wrapper around the Scalelite',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexsanderp/scalelite-python-wrapper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7',
)
