from setuptools import setup, find_packages

setup(
    name="morphomeasure",
    version="0.1.0",
    description="Python package and CLI for L-Measure-based morphometric extraction",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Masood Akram",
    author_email="masood.ahmed.akram@gmail.com",
    url="https://github.com/Masood-Akram/MorphoMeasure",
    packages=find_packages(),
    install_requires=[
        "pandas",
    ],
    include_package_data=True,
    package_data={
        # No need for this if using MANIFEST.in, but doesn't hurt
    },
    entry_points={
        'console_scripts': [
            'morphomeasure=morphomeasure.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"#,
        # "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
