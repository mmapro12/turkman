from setuptools import setup, find_packages
from pathlib import Path
import os
import re

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "src", "turkman", "version.py")
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*["\'](.+?)["\']', content)
    if match:
        return match.group(1)
    raise RuntimeError("Sürüm bilgisi bulunamadı!")


readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="turkman",
    version=get_version(),
    author="mmapro12",
    author_email="asia172007@gmail.com",
    description="Türkçe Unix/Linux man sayfaları için CLI aracı",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmapro12/turkman",
    license="GPLv3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: System :: Systems Administration",
        "Topic :: Terminals",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.9.0",
        "requests>=2.25.0",
        "rich>=12.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "turkman=turkman.turkman:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

