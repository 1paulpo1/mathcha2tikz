from __future__ import annotations

from pathlib import Path
from setuptools import find_packages, setup


ROOT = Path(__file__).parent
ABOUT: dict[str, str] = {}
with (ROOT / "mathcha2tikz" / "__version__.py").open(encoding="utf-8") as fh:
    exec(fh.read(), ABOUT)


setup(
    name="mathcha2tikz",
    version=ABOUT["__version__"],
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21",
    ],
    extras_require={
        "clipboard": ["pyperclip>=1.8"],
        "dev": ["pytest>=7", "pytest-cov>=4", "mypy>=1.8", "ruff>=0.5"],
    },
    entry_points={
        "console_scripts": [
            "mathcha2tikz=mathcha2tikz.CLI:main",
        ],
    },
    author="Paul",
    author_email="ptvkzybrf@icloud.com",
    description="Convert Mathcha-exported TikZ into optimized, human-readable TikZ.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/1paulpo1/mathcha2tikz",
    project_urls={
        "Homepage": "https://github.com/1paulpo1/mathcha2tikz",
        "Repository": "https://github.com/1paulpo1/mathcha2tikz",
        "Issues": "https://github.com/1paulpo1/mathcha2tikz/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
