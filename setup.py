from setuptools import setup, find_packages

setup(
    name="mathcha2tikz",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add your project's dependencies here
    ],
    entry_points={
        'console_scripts': [
            'mathcha2tikz=mathcha2tikz.cli:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to convert Mathcha TikZ code to processed TikZ output",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mathcha2tikz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
