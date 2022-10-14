"""Test modules for hexformat package.

  License::

    MIT License

    Copyright (c) 2015-2022 by Martin Scharrer <martin.scharrer@web.de>

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software
    and associated documentation files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
    BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
