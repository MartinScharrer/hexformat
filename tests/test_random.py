from hexformat.multipartbuffer import MultiPartBuffer
from hexformat.intelhex import IntelHex
from hexformat.srecord import SRecord

RANDOM1_ADDR = 0x0
RANDOM1_SIZE = 1023


def test_random1_bin():
    mpb1 = MultiPartBuffer.fromfile("tests/random1.bin", address=RANDOM1_ADDR)
    mpb2 = MultiPartBuffer.frombinfile("tests/random1.bin", address=RANDOM1_ADDR)
    assert mpb1 == mpb2
    assert mpb2.start() == RANDOM1_ADDR
    assert mpb2.usedsize() == RANDOM1_SIZE


def test_random1_hex():
    ih1 = IntelHex.fromfile("tests/random1.hex")
    ih2 = IntelHex.fromihexfile("tests/random1.hex")
    assert ih1 == ih2
    assert ih2.start() == RANDOM1_ADDR
    assert ih2.usedsize() == RANDOM1_SIZE


def test_random1_s19():
    srec1 = SRecord.fromfile("tests/random1.s19")
    srec2 = SRecord.fromsrecfile("tests/random1.s19")
    assert srec1 == srec2
    assert srec2.start() == RANDOM1_ADDR
    assert srec2.usedsize() == RANDOM1_SIZE


def test_random1_s28():
    srec1 = SRecord.fromfile("tests/random1.s28")
    srec2 = SRecord.fromsrecfile("tests/random1.s28")
    assert srec1 == srec2
    assert srec2.start() == RANDOM1_ADDR
    assert srec2.usedsize() == RANDOM1_SIZE


def test_random1_s37():
    srec1 = SRecord.fromfile("tests/random1.s37")
    srec2 = SRecord.fromsrecfile("tests/random1.s37")
    assert srec1 == srec2
    assert srec2.start() == RANDOM1_ADDR
    assert srec2.usedsize() == RANDOM1_SIZE


def test_random1_srec():
    srec37 = SRecord.fromsrecfile("tests/random1.s37")
    srec28 = SRecord.fromsrecfile("tests/random1.s28")
    srec19 = SRecord.fromsrecfile("tests/random1.s19")
    assert srec37 == srec28
    assert srec19 == srec28
    assert srec37 == srec19


# noinspection PyProtectedMember
def test_random1_srecihex():
    srec = SRecord.fromsrecfile("tests/random1.s37")
    ih = IntelHex.fromihexfile("tests/random1.hex")
    assert ih._parts == srec._parts
