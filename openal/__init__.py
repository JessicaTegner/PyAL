"""OpenAL AL and ALC wrapper using ctypes"""
import os
import sys
import ctypes
import warnings
from ctypes.util import find_library

__all__ = ["get_dll_file", "version_info"]


def _findlib(libnames, path=None):
    """Internal helper function to find the requested DLL(s)."""
    platform = sys.platform
    if platform in ("win32", "cli"):
        suffix = ".dll"
    elif platform == "darwin":
        suffix = ".dylib"
    else:
        suffix = ".so"

    searchfor = libnames
    if type(libnames) is dict:
        # different library names for the platforms
        if platform == "cli" and platform not in libnames:
            # if not explicitly specified, use the Win32 libs for IronPython
            platform = "win32"
        if platform not in libnames:
            platform = "DEFAULT"
        searchfor = libnames[platform]
    results = []
    if path:
        for libname in searchfor:
            dllfile = os.path.join(path, "%s%s" % (libname, suffix))
            if os.path.exists(dllfile):
                results.append(dllfile)
    for libname in searchfor:
        dllfile = find_library(libname)
        if dllfile:
            results.append(dllfile)
    return results


class _DLL(object):
    """Function wrapper around the different DLL functions. Do not use or
    instantiate this one directly from your user code.
    """
    def __init__(self, libinfo, libnames, path=None):
        self._dll = None
        foundlibs = _findlib(libnames, path)
        if len(foundlibs) == 0:
            raise RuntimeError("could not find any library for %s" % libinfo)
        for libfile in foundlibs:
            try:
                self._dll = ctypes.CDLL(libfile)
                self._libfile = libfile
                break
            except Exception as exc:
                # Could not load it, silently ignore that issue and move
                # to the next one.
                warnings.warn(exc, ImportWarning)
        if self._dll is None:
            raise RuntimeError("could not load any library for %s" % libinfo)
        if path is not None and sys.platform in ("win32", "cli") and \
            path in self._libfile:
            os.environ["PATH"] += ";%s" % path

    def bind_function(self, funcname, args=None, returns=None):
        """Binds the passed argument and return value types to the specified
        function."""
        func = getattr(self._dll, funcname)
        func.argtypes = args
        func.restype = returns
        return func

    @property
    def libfile(self):
        """Gets the filename of the loaded library."""
        return self._libfile


dll = _DLL("OpenAL", {"win32": ["OpenAL", "OpenAL32"],
                      "darwin": ["OpenAL"],
                      "DEFAULT": ["openal", "OpenAL"]},
           os.getenv("PYAL_DLL_PATH"))


def get_dll_file():
    """Gets the file name of the loaded OpenAL library."""
    return dll.libfile


__version__ = "0.2.0"
version_info = (0, 2, 0, "")
