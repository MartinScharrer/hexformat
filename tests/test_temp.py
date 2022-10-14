""" Further unit tests for IntelHex and SRecord.

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
import os
import shutil
import tempfile
from time import time
from tests import TestCase, randbytes, randint

from hexformat.intelhex import IntelHex
from hexformat.multipartbuffer import MultiPartBuffer
from hexformat.srecord import SRecord


class TestTemp(TestCase):

    def createrandom(self, randomsize, randomaddr, filebase):
        binfilename = filebase + '.bin'
        ihexfilename = filebase + '.hex'
        srecfilename = filebase + '.srec'

        # create random bin file
        # noinspection PyUnusedLocal
        randomdata = randbytes(randomsize)
        self.assertEqual(len(randomdata), randomsize)
        with open(binfilename, "wb") as fh:
            fh.write(randomdata)

        # read back and compare
        mpb = MultiPartBuffer.frombinfile(binfilename, address=randomaddr)
        self.assertEqual(mpb[:], randomdata)
        srec = SRecord.frombinfile(binfilename, address=randomaddr)
        self.assertEqual(srec[:], randomdata)
        ihex = IntelHex.frombinfile(binfilename, address=randomaddr)
        self.assertEqual(ihex[:], randomdata)

        # generate hexfiles and read back
        srec.tosrecfile(srecfilename)
        srec2 = SRecord.fromsrecfile(srecfilename)
        self.assertEqual(srec[:], srec2[:])
        self.assertEqual(srec, srec2)
        ihex.toihexfile(ihexfilename)
        ihex2 = IntelHex.fromihexfile(ihexfilename)
        self.assertEqual(ihex[:], ihex2[:])
        self.assertEqual(ihex, ihex2)
        self.assertEqual(ihex2[:], srec2[:])

    def test_createrandom(self):
        dirname = tempfile.mkdtemp(prefix="test_createrandom_")
        timelimit = time() + 20
        try:
            for n in range(0, 10):
                randomsize = randint(0, (1 << 16) - 1)
                randomaddr = randint(0, (1 << 21) - 1)
                filebase = os.path.join(dirname, "testrun" + str(n))
                with self.subTest(n):
                    self.createrandom(randomsize, randomaddr, filebase)
                if time() >= timelimit:
                    break
        finally:
            try:
                shutil.rmtree(dirname)
            except OSError:
                pass
