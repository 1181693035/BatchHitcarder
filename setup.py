import setuptools

setuptools.setup(
    name="zju_hitcarder",
    version="0.1.0",
    author="Tishacy",
    author_email="Tishacy@gmail.com",
    description="ZJU health hitcarder",
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