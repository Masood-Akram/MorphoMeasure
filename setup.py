from setuptools import setup, find_packages

setup(
    name="morphomeasure",
    version="0.1.0",
    description="Python wrapper and CLI for L-Measure morphometric feature extraction",
    author="Masood Akram",
    packages=find_packages(),
    install_requires=[
        "pandas"
    ],
    python_requires=">=3.7",
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'morphomeasure=morphomeasure.cli:main'
        ]
    },
)
