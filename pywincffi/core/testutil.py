"""
Test Utility
------------

This module is used by the unittests.
"""

import atexit
import os
import shutil
import sys
from errno import ENOENT
from os.path import isfile, isdir

from cffi import FFI

if sys.version_info[0:2] == (2, 6):
    from unittest2 import TestCase as _TestCase
else:
    from unittest import TestCase as _TestCase

from pywincffi.core.ffi import Library

# Load in our own kernel32 with the function(s) we need
# so we don't have to rely on pywincffi.core
ffi = FFI()
ffi.cdef("void SetLastError(DWORD);")
kernel32 = ffi.dlopen("kernel32")


class TestCase(_TestCase):
    """
    A base class for all test cases.  By default the
    core test case just provides some extra functionality.
    """
    def setUp(self):
        # Always reset the last error to 0 between tests.  This
        # ensures that any error we intentionally throw in one
        # test does not causes an error to be raised in another.
        kernel32.SetLastError(ffi.cast("DWORD", 0))

    def remove(self, path, onexit=True):
        """
        Single function to remove a file or directory.  If there are
        problems while attempting to remove the path we'll try again
        when the tests exit.
        """
        if isfile(path):
            remove = os.remove
        elif isdir(path):
            remove = shutil.rmtree
        else:
            return

        try:
            remove(path)
        except (OSError, IOError, WindowsError) as e:
            if e.errno != ENOENT and onexit:
                atexit.register(self.remove, path, onexit=False)


class HeaderFileDefinitionTestCase(_TestCase):
    """
    Used to test header definitions against our library.
    """
    # The full path to the header file we're testing
    HEADER = None

    def setUp(self):
        if self.HEADER is None:
            self.skipTest("HEADER not set")

        with open(self.HEADER, "r") as header_file:
            self.header = header_file.read()

        self.ffi, self.library = Library.load()

    def get_definitions(self):
        pass

    def test_definitions(self):
        definitions = self.get_definitions()

        if definitions is None:
            self.skipTest("No definitions provided.")

        if not definitions:
            self.fail("No definitions found")

