import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zju_hitcarder",
    version="0.1.1",
    author="Tishacy",
    author_email="Tishacy@gmail.com",
    description="ZJU health hitcarder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.25.1',
        'loguru>=0.5.3',
        'APScheduler>=3.7.0'
    ],
    entry_points={
        'console_scripts': [
            'hitcarder=hitcarder.run:main'
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    )
)