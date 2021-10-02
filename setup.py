# setup.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)
"""chessresults setup file."""

from setuptools import setup

if __name__ == "__main__":

    long_description = open("README").read()
    install_requires=[
        "solentware-base==4.1.6",
        "chesscalc==1.2.3",
        "emailstore==1.4.4",
        "emailextract==0.7.4",
        "solentware-grid==2.1.4",
        "solentware-misc==1.3.2",
    ]

    setup(
        name="chessresults",
        version="5.0.3",
        description="Results database for chess games",
        author="Roger Marsh",
        author_email="roger.marsh@solentware.co.uk",
        url="http://www.solentware.co.uk",
        packages=[
            "chessresults",
            "chessresults.core",
            "chessresults.help",
            "chessresults.basecore",
            "chessresults.minorbases",
            "chessresults.gui",
            "chessresults.gui.minorbases",
            "chessresults.berkeleydb",
            "chessresults.db",
            "chessresults.dpt",
            "chessresults.sqlite",
            "chessresults.apsw",
            "chessresults.unqlite",
            "chessresults.vedis",
            "chessresults.tools",
        ],
        package_data={
            "chessresults.help": ["*.txt"],
        },
        long_description=long_description,
        license="BSD",
        classifiers=[
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Operating System :: OS Independent",
            "Topic :: Games/Entertainment :: Board Games",
            "Intended Audience :: End Users/Desktop",
            "Development Status :: 3 - Alpha",
        ],
        install_requires=install_requires,
        dependency_links=[
            "-".join(required.split("==")).join(
                ("http://solentware.co.uk/files/", ".tar.gz")
            )
            for required in install_requires
        ],
    )
