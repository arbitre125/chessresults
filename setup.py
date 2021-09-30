# setup.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)
"""chessresults setup file."""

from setuptools import setup

if __name__ == "__main__":

    long_description = open("README").read()

    setup(
        name="chessresults",
        version="5.0.2",
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
        install_requires=[
            "solentware-base==4.1.5",
            "chesscalc==1.2.2",
            "emailstore==1.4.3",
            "emailextract==0.7.3",
            "solentware-grid==2.1.3",
            "solentware-misc==1.3.1",
        ],
        dependency_links=[
            "http://solentware.co.uk/files/solentware-base-4.1.5.tar.gz",
            "http://solentware.co.uk/files/chesscalc-1.2.2.tar.gz",
            "http://solentware.co.uk/files/emailstore-1.4.3.tar.gz",
            "http://solentware.co.uk/files/emailextract-0.7.3.tar.gz",
            "http://solentware.co.uk/files/solentware-grid-2.1.3.tar.gz",
            "http://solentware.co.uk/files/solentware-misc-1.3.1.tar.gz",
        ],
    )
