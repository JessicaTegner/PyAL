#!/usr/bin/env python
import os
import sys
from distutils.core import setup

VERSION = "0.4.0"

if __name__ == "__main__":

    if "--format=msi" in sys.argv or "bdist_msi" in sys.argv:
        # hack the version name to a format msi doesn't have trouble with
        VERSION = VERSION.replace("-alpha", "a")
        VERSION = VERSION.replace("-beta", "b")
        VERSION = VERSION.replace("-rc", "r")

    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    readme = open(fname, "r")
    long_desc = readme.read()
    readme.close()

    setupdata = {
        "name":  "python-openal",
        "version": VERSION,
        "description": "Python OpenAL bindings",
        "long_description": long_desc,
        "author": "Marcus von Appen",
        "author_email": "marcus@sysfault.org",
        "license": "Public Domain / zlib",
        "url": "http://bitbucket.org/marcusva/py-al",
        "packages": ["openal",
                     "openal.loaders",
                     "openal.test",
                     "openal.test.util"
                     ],
        "package_data": {"openal.test": ["resources/*.*"]},
        "classifiers": [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: Public Domain",
            "License :: OSI Approved :: zlib/libpng License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: IronPython",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Topic :: Multimedia :: Sound/Audio",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        }
    setup(**setupdata)
