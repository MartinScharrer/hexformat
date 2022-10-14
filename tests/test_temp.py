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
