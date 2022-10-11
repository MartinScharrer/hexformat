from hexformat.srecord import SRecord
import random
import unittest


class FakeFileHandle(list):
    def write(self, line):
        self.append(line)


class TestSRecEncode(unittest.TestCase):

    # noinspection PyProtectedMember
    def test_encode_bytesperline(self):
        testlines = ["S11F00007C0802A6900100049421FFF07C6C1B787C8C23783C6000003863000026\n", ]
        testaddr = 0x0000
        testdata = bytearray.fromhex("7C0802A6900100049421FFF07C6C1B787C8C23783C60000038630000")
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 1, testaddr, testdata, bytesperline=32)
        self.assertEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_bytesperlineminusone(self):
        testlines = ["S12200007A2924CCF93992EBA363D902D6A1DFF23FF7640A434C887B9D788E0B499EDFC8\n", ]
        testaddr = 0x0000
        testdata = bytearray.fromhex("7A2924CCF93992EBA363D902D6A1DFF23FF7640A434C887B9D788E0B499EDF")
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 1, testaddr, testdata, bytesperline=32)
        self.assertEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_bytesperlineplusone(self):
        testlines = ["S123000092DC615BBFC97CA260C8193A8D9EBA2986A0328851C66834A50058C707CD5AC737\n",
                     "S104002033A8\n"]
        testaddr = 0x0000
        testdata = bytearray.fromhex("92DC615BBFC97CA260C8193A8D9EBA2986A0328851C66834A50058C707CD5AC733")
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 1, testaddr, testdata, bytesperline=32)
        self.assertListEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_s0_1(self):
        testlines = ["S011000000486578766965772056312E3038D1\n", ]
        testaddr = 0x0000
        testdata = bytearray.fromhex("00486578766965772056312E3038")
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 0, testaddr, testdata, bytesperline=32)
        self.assertListEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_s0_2(self):
        testlines = ["S00F000068656C6C6F202020202000003C\n", ]
        testaddr = 0x0000
        testdata = bytearray.fromhex("68656C6C6F20202020200000")
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 0, testaddr, testdata, bytesperline=32)
        self.assertListEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_s5(self):
        testlines = ["S5030003F9\n", ]
        testaddr = 0x0003
        testdata = bytearray()
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 5, testaddr, testdata, bytesperline=32)
        self.assertListEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_s9_1(self):
        testlines = ["S9030000FC\n", ]
        testaddr = 0x0000
        testdata = bytearray()
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 9, testaddr, testdata, bytesperline=32)
        self.assertListEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_s9_2(self):
        testlines = ["S903FFFFFE\n", ]
        testaddr = 0xFFFF
        testdata = bytearray()
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 9, testaddr, testdata, bytesperline=32)
        self.assertListEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_s3(self):
        testlines = [
            "S325000000008A2787EF8DE62E8C416810F616EDB69F898B355AEEDB0EB56CF2538949920BCF61\n",
            "S3250000002067A2D8B50FDCD7F2EEC6C8565DE36FA5E62A39A503B7237628C1D82204CC1975C8\n",
            "S32500000040051F620F1A79CBB7BC002CF22F7A84D405BF9C17E56EE76A8AE0AD0B0E5A689870\n",
            "S3090000006069876F2314\n",
        ]
        testaddr = 0x0000
        testdata = bytearray.fromhex("8A2787EF8DE62E8C416810F616EDB69F898B355AEEDB0EB56CF2538949920BCF"
                                     "67A2D8B50FDCD7F2EEC6C8565DE36FA5E62A39A503B7237628C1D82204CC1975"
                                     "051F620F1A79CBB7BC002CF22F7A84D405BF9C17E56EE76A8AE0AD0B0E5A6898"
                                     "69876F23")
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 3, testaddr, testdata, 32)
        self.assertListEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_s2(self):
        testlines = [
            "S2240000008A2787EF8DE62E8C416810F616EDB69F898B355AEEDB0EB56CF2538949920BCF62\n",
            "S22400002067A2D8B50FDCD7F2EEC6C8565DE36FA5E62A39A503B7237628C1D82204CC1975C9\n",
            "S224000040051F620F1A79CBB7BC002CF22F7A84D405BF9C17E56EE76A8AE0AD0B0E5A689871\n",
            "S20800006069876F2315\n",
        ]
        testaddr = 0x0000
        testdata = bytearray.fromhex("8A2787EF8DE62E8C416810F616EDB69F898B355AEEDB0EB56CF2538949920BCF"
                                     "67A2D8B50FDCD7F2EEC6C8565DE36FA5E62A39A503B7237628C1D82204CC1975"
                                     "051F620F1A79CBB7BC002CF22F7A84D405BF9C17E56EE76A8AE0AD0B0E5A6898"
                                     "69876F23")
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 2, testaddr, testdata, 32)
        self.assertListEqual(testlines, fh)

    # noinspection PyProtectedMember
    def test_encode_s1(self):
        testlines = [
            "S12300003501C3BFF01EC6E629ADADB85F40907B1859B8E2808061CC5494BE2FFE5F3E4E8F\n",
            "S1230020026C0E33981DDF599AF8E9A9A14230A76CCF06EE8118D1DA168E0E84312E96F3B1\n",
            "S12300400F562090C3D708DB1F4B4F5DD7A9E2DDE4161FD727FE952A4F640B11FC76C45488\n",
            "S1070060246502C04D\n",
        ]
        testaddr = 0x0000
        testdata = bytearray.fromhex("3501C3BFF01EC6E629ADADB85F40907B1859B8E2808061CC5494BE2FFE5F3E4E"
                                     "026C0E33981DDF599AF8E9A9A14230A76CCF06EE8118D1DA168E0E84312E96F3"
                                     "0F562090C3D708DB1F4B4F5DD7A9E2DDE4161FD727FE952A4F640B11FC76C454"
                                     "246502C0")
        fh = FakeFileHandle()
        SRecord._encodesrecline(fh, 1, testaddr, testdata, 32)
        self.assertListEqual(testlines, fh)

    def test_encode_all_byteperline(self):
        """ Test all valid bytesperline settings [0..254-addresslength] """

        # noinspection PyProtectedMember
        def do(recordtype, bytesperline):
            addresslen = recordtype + 1
            # noinspection PyUnusedLocal
            testdata = bytearray((random.randint(0, 0xFF) for m in range(0, bytesperline)))
            fh = FakeFileHandle()
            SRecord._encodesrecline(fh, recordtype, 0, testdata, bytesperline)
            self.assertEqual(len(fh), 1)
            self.assertEqual(bytearray.fromhex(fh[0][4 + 2 * addresslen:-3]), testdata)

        for r in (1, 2, 3):
            addresslength = r + 1
            for bpl in range(1, 254 - addresslength):
                yield do, r, bpl
