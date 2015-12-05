"""
Distribution
============

Module responsible for building the pywincffi distribution
in ``setup.py``.
"""

from os.path import join, isfile
from pkg_resources import resource_filename

from cffi import FFI

from pywincffi.core.logger import get_logger
from pywincffi.exceptions import ResourceNotFoundError


logger = get_logger("core.dist")


def get_filepath(root, filename):
    """
    Returns the filepath to the requested header or source
    file.

    :param str root:
        The root directory under ``pywincffi/core/cdefs``. 'headers'
        for example would be a valid entry here.

    :param str filename:
        The name of the file you want to retrieve under ``root``.

    :raises ResourceNotFoundError:
        Raised if the function could not find the requested file.
    """
    logger.debug("get_filepath(%r, %r)", root, filename)
    path = resource_filename(
        "pywincffi", join("core", "cdefs", root, filename))

    if not isfile(path):
        raise ResourceNotFoundError(
            "Failed to locate %s/%s" % (root, filename))

    return path


class Distribution(object):
    """
    A class responsible for building, caching and returning
    the built artifacts for :mod:`pywincffi`

    :ivar str MODULE_NAME:
        The name of the module to pass to :meth:`FFI.set_source`. This
        will eventually end up becoming the name of the underlying C-module
        that is built.

    :ivar tuple HEADERS:
        A tuple containing all the headers used to build pywincffi.

    :ivar tuple SOURCES:
        A tuple containing all the C source files to build pywincffi.

    :ivar tuple LIBRARIES:
        A tuple of Windows library names that :meth:`FFI.verify` should
        use.
    """
    MODULE_NAME = "_pywincffi"
    HEADERS = (
        get_filepath("headers", "constants.h"),
        get_filepath("headers", "structs.h"),
        get_filepath("headers", "functions.h")
    )
    SOURCES = (get_filepath("sources", "main.c"), )
    LIBRARIES = ("kernel32", )

    _ffi = None

    @classmethod
    def load_definitions(cls):
        """
        Reads in the headers and source files and produces
        a tuple of strings with the results
        """
        header = ""
        source = ""

        for path in cls.HEADERS:
            logger.debug("Reading %s", path)
            with open(path, "r") as file_:
                header += file_.read()

        for path in cls.SOURCES:
            logger.debug("Reading %s", path)
            with open(path, "r") as file_:
                source += file_.read()

        return header, source

    @classmethod
    def inline(cls):
        """
        Compiles pywincffi in inline mode.  This is mainly used when
        doing development and is conditionally called by :meth:`load`
        below.
        """
        logger.debug("Compiling inline")
        header, source = cls.load_definitions()

        ffi = FFI()
        ffi.set_unicode(True)
        ffi.cdef(header)

        return ffi, ffi.verify(source, libraries=cls.LIBRARIES)

    @classmethod
    def out_of_line(cls, compile_=False):
        """
        Compiles pywincffi in out of line mode.  This is used to create a
        distribution of pywcinffi and more specifically is used by
        ``setup.py``

        :param bool compile_:
            If True then perform the compile step as well.  By default calling
            this method will not call :func:`FFI.compile`.
        """
        logger.debug("Compiling out of line")
        header, source = cls.load_definitions()
        ffi = FFI()
        ffi.set_unicode(True)
        ffi.set_source(cls.MODULE_NAME, source)
        ffi.cdef(header)

        if compile_:
            ffi.compile()

        return ffi

# Entrypoint for setup.py
compile_ = Distribution.out_of_line
