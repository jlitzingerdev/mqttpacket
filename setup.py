
"""
Copyright 2018 Jason Litzinger.
See LICENSE for details
"""
from setuptools import setup, find_packages

EXTRAS = {
    "tests": [
        "coverage",
        "pytest",
    ]
}

setup(
    name='mqttpacket',
    version='0.0.0',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        'attrs',
    ],
    package_dir={"": "src"},
    packages=find_packages("src"),
    license='MIT',
    extras_require=EXTRAS,
)
