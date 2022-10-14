"""Test modules for hexformat package.

  License::
  
    Copyright (C) 2015-2022  Martin Scharrer <martin.scharrer@web.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

"""

from random import randint
import os
import shutil
import tempfile
import unittest
from unittest import TestCase
from unittest.mock import patch

patch = patch

try:
    from random import randbytes
except ImportError:
    def randbytes(length):
        return [randint(0, 255) for _ in range(0, length)]


# Decorator for slow tests to be skipped under normal test runs
skipunlessslow = unittest.skipUnless(os.environ.get('SLOW_TESTS', False), "slow tests")


def randstr(length):
    return bytearray((randint(ord('a'), ord('z')) for _ in range(0, length))).decode()


def randdict(number=None):
    if number is None:
        number = randint(1, 16)
    return {randstr(randint(1, 16)): randbytes(randint(1, 16)) for _ in range(0, number)}


class TestCaseWithTempfile(TestCase):
    """Test case with a temporary testfile."""
    dirname = ""
    testfilename = ""

    def setUp(self):
        """Set-up temporary directory with test file."""
        self.dirname = tempfile.mkdtemp(prefix="test_srecord_")
        # sys.stderr.write("Tempdir: {:s}\n".format(self.dirname))
        self.testfilename = os.path.join(self.dirname, "testdata.srec")

    def tearDown(self):
        """Remove temporary directory after test run."""
        try:
            shutil.rmtree(self.dirname)
        except OSError:
            pass
