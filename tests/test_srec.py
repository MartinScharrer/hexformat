from hexformat.srecord import SRecord
from nose.tools import assert_equal, assert_list_equal


class FakeFileHandle(list):
    def write(self, line):
        self.append(line)


# noinspection PyProtectedMember
def test_encode_bytesperline():
    testline = "S11F00007C0802A6900100049421FFF07C6C1B787C8C23783C6000003863000026\n"
    testaddr = 0x0000
    testdata = bytearray.fromhex("7C0802A6900100049421FFF07C6C1B787C8C23783C60000038630000")
    fh = FakeFileHandle()
    SRecord._encodesrecline(fh, testaddr, testdata, offset=0, recordtype=1, bytesperline=32)
    assert_equal(fh[0], testline)


# noinspection PyProtectedMember
def test_encode_bytesperlineminusone():
    testline = "S12200007A2924CCF93992EBA363D902D6A1DFF23FF7640A434C887B9D788E0B499EDFC8\n"
    testaddr = 0x0000
    testdata = bytearray.fromhex("7A2924CCF93992EBA363D902D6A1DFF23FF7640A434C887B9D788E0B499EDF")
    fh = FakeFileHandle()
    SRecord._encodesrecline(fh, testaddr, testdata, offset=0, recordtype=1, bytesperline=32)
    assert_equal(fh[0], testline)


# noinspection PyProtectedMember
def test_encode_bytesperlineplusone():
    testlines = ["S123000092DC615BBFC97CA260C8193A8D9EBA2986A0328851C66834A50058C707CD5AC737\n",
                 "S104002033A8\n"]
    testaddr = 0x0000
    testdata = bytearray.fromhex("92DC615BBFC97CA260C8193A8D9EBA2986A0328851C66834A50058C707CD5AC733")
    fh = FakeFileHandle()
    SRecord._encodesrecline(fh, testaddr, testdata, offset=0, recordtype=1, bytesperline=32)
    assert_list_equal(fh, testlines)




