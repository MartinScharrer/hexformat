from hexformat.intelhex import IntelHex
from hexformat.multipartbuffer import MultiPartBuffer
from hexformat.srecord import SRecord
import unittest


class TestRandom(unittest.TestCase):
    RANDOM1_ADDR = 0x0
    RANDOM1_SIZE = 1023
    DIR = ""

    def test_random1_bin(self):
        mpb1 = MultiPartBuffer.fromfile(self.DIR + "random1.bin", address=self.RANDOM1_ADDR)
        mpb2 = MultiPartBuffer.frombinfile(self.DIR + "random1.bin", address=self.RANDOM1_ADDR)
        self.assertEqual(mpb1, mpb2)
        self.assertEqual(mpb2.start(), self.RANDOM1_ADDR)
        self.assertEqual(mpb2.usedsize(), self.RANDOM1_SIZE)
    
    
    def test_random1_hex(self):
        ih1 = IntelHex.fromfile(self.DIR + "random1.hex")
        ih2 = IntelHex.fromihexfile(self.DIR + "random1.hex")
        self.assertEqual(ih1, ih2)
        self.assertEqual(ih2.start(), self.RANDOM1_ADDR)
        self.assertEqual(ih2.usedsize(), self.RANDOM1_SIZE)
    
    
    def test_random1_s19(self):
        srec1 = SRecord.fromfile(self.DIR + "random1.s19")
        srec2 = SRecord.fromsrecfile(self.DIR + "random1.s19")
        self.assertEqual(srec1, srec2)
        self.assertEqual(srec2.start(), self.RANDOM1_ADDR)
        self.assertEqual(srec2.usedsize(), self.RANDOM1_SIZE)
    
    
    def test_random1_s28(self):
        srec1 = SRecord.fromfile(self.DIR + "random1.s28")
        srec2 = SRecord.fromsrecfile(self.DIR + "random1.s28")
        self.assertEqual(srec1, srec2)
        self.assertEqual(srec2.start(), self.RANDOM1_ADDR)
        self.assertEqual(srec2.usedsize(), self.RANDOM1_SIZE)
    
    
    def test_random1_s37(self):
        srec1 = SRecord.fromfile(self.DIR + "random1.s37")
        srec2 = SRecord.fromsrecfile(self.DIR + "random1.s37")
        self.assertEqual(srec1, srec2)
        self.assertEqual(srec2.start(), self.RANDOM1_ADDR)
        self.assertEqual(srec2.usedsize(), self.RANDOM1_SIZE)
    
    
    def test_random1_srec(self):
        srec37 = SRecord.fromsrecfile(self.DIR + "random1.s37")
        srec28 = SRecord.fromsrecfile(self.DIR + "random1.s28")
        srec19 = SRecord.fromsrecfile(self.DIR + "random1.s19")
        self.assertEqual(srec37, srec28)
        self.assertEqual(srec19, srec28)
        self.assertEqual(srec37, srec19)
    
    
    # noinspection PyProtectedMember
    def test_random1_srecihex(self):
        srec = SRecord.fromsrecfile(self.DIR + "random1.s37")
        ih = IntelHex.fromihexfile(self.DIR + "random1.hex")
        self.assertEqual(ih._parts, srec._parts)
