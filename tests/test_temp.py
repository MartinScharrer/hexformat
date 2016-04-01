import tempfile
import random
from hexformat.multipartbuffer import MultiPartBuffer
from hexformat.intelhex import IntelHex
from hexformat.srecord import SRecord
from time import time
import os
import shutil


def createrandom(randomsize, randomaddr, filebase):
    binfilename = filebase + '.bin'
    ihexfilename = filebase + '.hex'
    srecfilename = filebase + '.srec'

    # create random bin file
    randomdata = bytearray((random.randint(0, 255) for n in range(0, randomsize)))
    assert len(randomdata) == randomsize
    with open(binfilename, "wb") as fh:
        fh.write(randomdata)

    # read back and compare
    mpb = MultiPartBuffer.frombinfile(binfilename, address=randomaddr)
    assert mpb[:] == randomdata
    srec = SRecord.frombinfile(binfilename, address=randomaddr)
    assert srec[:] == randomdata
    ihex = IntelHex.frombinfile(binfilename, address=randomaddr)
    assert ihex[:] == randomdata

    # generate hexfiles and read back
    srec.tosrecfile(srecfilename)
    srec2 = SRecord.fromsrecfile(srecfilename)
    assert srec[:] == srec2[:]
    assert srec == srec2
    ihex.toihexfile(ihexfilename)
    ihex2 = IntelHex.fromihexfile(ihexfilename)
    assert ihex[:] == ihex2[:]
    assert ihex == ihex2
    assert ihex2[:] == srec2[:]


def test_createrandom():
    dirname = tempfile.mkdtemp(prefix="test_createrandom_")
    timelimit = time() + 20
    try:
        for n in range(0, 10):
            randomsize = random.randint(0, (1 << 16) - 1)
            randomaddr = random.randint(0, (1 << 21) - 1)
            filebase = os.path.join(dirname, "testrun"+str(n))
            yield createrandom, randomsize, randomaddr, filebase
            if time() >= timelimit:
                break
    finally:
        try:
            shutil.rmtree(dirname)
        except:
            pass


