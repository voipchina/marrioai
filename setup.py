import os
import subprocess

from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import find_packages, setup

cwd = Path(__file__).resolve().parent

package_name = "marrioai"
version = "0.0.1"
git_hash = "unknown"

def write_version_file():
    path = cwd / package_name / "version.py"
    with path.open("w") as f:
        f.write(f'__version__ = "{version}"\n')
        f.write(f'git_version = "{git_hash}"\n')


write_version_file()

def get_extensions():
    ext_dirs = cwd / package_name / "cpp_exts"
    ext_modules = []

    # Add rANS module
    rans_lib_dir = cwd / "third_party/ryg_rans"
    rans_ext_dir = ext_dirs / "rans"

    extra_compile_args = ["-std=c++17"]
    if os.getenv("DEBUG_BUILD", None):
        extra_compile_args += ["-O0", "-g", "-UNDEBUG"]
    else:
        extra_compile_args += ["-O3"]
    ext_modules.append(
        Pybind11Extension(
            name=f"{package_name}.ans",
            sources=[str(s) for s in rans_ext_dir.glob("*.cpp")],
            language="c++",
            include_dirs=[rans_lib_dir, rans_ext_dir],
            extra_compile_args=extra_compile_args,
        )
    )

    # Add ops
    ops_ext_dir = ext_dirs / "ops"
    ext_modules.append(
        Pybind11Extension(
            name=f"{package_name}._CXX",
            sources=[str(s) for s in ops_ext_dir.glob("*.cpp")],
            language="c++",
            extra_compile_args=extra_compile_args,
        )
    )

    return ext_modules

TEST_REQUIRES = ["pytest", "pytest-cov", "plotly"]
DEV_REQUIRES = TEST_REQUIRES + [
    "black",
    "flake8",
    "flake8-bugbear",
    "flake8-comprehensions",
    "isort",
    "mypy",
]
POINTCLOUD_REQUIRES = [
    "pointops-yoda",
    "pyntcloud-yoda",  # Patched version of pyntcloud.
]

def get_extra_requirements():
    extras_require = {
        "test": TEST_REQUIRES,
        "dev": DEV_REQUIRES,
        "doc": ["sphinx", "sphinx-book-theme", "Jinja2<3.1"],
        "tutorials": ["jupyter", "ipywidgets"],
        "pointcloud": POINTCLOUD_REQUIRES,
    }
    extras_require["all"] = {req for reqs in extras_require.values() for req in reqs}
    return extras_require

setup(
    name=package_name,
    version=version,
    description="A Mindspore library and evaluation platform for end-to-end compression research",
    url="https://github.com/voipchina/marrioai",
    author="Steven Wang",
    author_email="geniuswwg@gmail.com",
    packages=find_packages(exclude=("tests",)),
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        # "einops",
        # "numpy>=1.21.0",
        # "pandas",
        # "scipy",
        # "matplotlib",
        # "torch>=1.7.1, <2.3",
        # "torch-geometric>=2.3.0",
        # "typing-extensions>=4.0.0",
        # "torchvision",
        # "pytorch-msssim",
        # "tqdm",
    ],
    extras_require=get_extra_requirements(),
    license="BSD 3-Clause Clear License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    ext_modules=get_extensions(),
    cmdclass={"build_ext": build_ext},
)
