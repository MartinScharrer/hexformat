
from multipartbuffer import MultiPartBuffer

# Intel-Hex Record Types
RT_DATA = 0
RT_END_OF_FILE  = 1
RT_EXTENDED_SEGMENT_ADDRESS = 2
RT_START_SEGMENT_ADDRESS = 3
RT_EXTENDED_LINEAR_ADDRESS = 4
RT_START_LINEAR_ADDRESS = 5

class HexformatError(Exception):
    """General hexformat exception. Base class for all other exceptions of this module."""
    pass

class DecodeError(HexformatError):
    """Exception is raised if errors during the decoding of a hex file occur."""
    pass

class EncodeError(HexformatError):
    """Exception is raised if errors during the encoding of a hex file occur."""
    pass

class IntelHex(MultiPartBuffer):
    """Intel-Hex file representation class.

       The IntelHex class is able to parse and generate binary data in the Intel-Hex representation.
    """
    _DATALENGTH = (None, 0, 2, 4, 2, 4)
    _VARIANTS = { 'I08HEX':8, 'I8HEX':8, 'I16HEX':16, 'I32HEX':32, 8:8, 16:16, 32:32 }
    _DEFAULT_BYTES_PER_LINE = 16
    _DEFAULT_VARIANT = 32
    _bytesperline = None
    _cs_ip = None
    _eip = None
    _variant = None

    def __init__(self, **settings):
        super(IntelHex, self).__init__()
        self.settings(**settings)

    def _parseihexline(self, line):
        try:
            line = line.rstrip("\r\n")
            startcode = line[0]
            if startcode != ":":
                raise DecodeError("No valid IntelHex start code found.")
            bytes = bytearray.fromhex(line[1:])
        except:
            raise ValueError
        bytecount = bytes[0]
        if bytecount != len(bytes) - 5:
            raise DecodeError("Data length does not match byte count.")
        checksumcorrect = ( (sum(bytes) & 0xFF) == 0x00 )
        address = (bytes[1] << 8) | bytes[2]
        recordtype = bytes[3]
        try:
            supposed_datalength = self._DATALENGTH[recordtype]
        except IndexError:
            raise DecodeError("Unknown record type.")
        if supposed_datalength is not None and supposed_datalength != bytecount:
            raise DecodeError("Data length does not correspond to record type.")
        data = bytes[4:-1]
        return (recordtype, address, data, bytecount, checksumcorrect)

    def _encodeihexline(self, recordtype, address16bit=0, data=bytearray()):
        linelen = 2*len(data) + 11
        linetempl = ":{:02X}{:04X}{:02X}{:s}{:02X}\n"
        bytecount = len(data)
        try:
            supposed_datalength = self._DATALENGTH[recordtype]
        except IndexError:
            raise DecodeError("Unknown record type.")
        if supposed_datalength is not None and supposed_datalength != bytecount:
            raise DecodeError("Data length does not correspond to record type.")
        address16bit &= 0xFFFF
        datastr = "".join("{:02X}".format(byte) for byte in data)
        checksum = bytecount + sum(data) + (address16bit >> 8) + (address16bit & 0xFF) + recordtype
        checksum = (~checksum + 1) & 0xFF
        return linetempl.format(bytecount, address16bit, recordtype, datastr, checksum)

    @classmethod
    def fromihexfile(cls, frep, ignore_checksum_errors=False):
        self = cls()
        self.loadhexfile(frep, ignore_checksum_errors)
        return self

    def settings(self, **kvargs):
        (self._bytesperline, self._variant, self._cs_ip, self._eip) = self._parsesettings(True, **kvargs)

    def _parsesettings(self, isinit, **kvargs):
        if 'bytesperline' in kvargs:
            bytesperline = int(kvargs['bytesperline'])
        else:
            bytesperline = self._bytesperline
        if 'variant' in kvargs:
            variant = self._VARIANTS[ kvargs['variant'] ]
        else:
            variant = self._variant
        if 'cs_ip' in kvargs:
            cs_ip = int(kvargs['cs_ip'])
            if cs_ip > 0xFFFFFFFF:
                raise ValueError
            cs_ip = bytearray.fromhex("{:08x}".format(cs_ip))
        else:
            cs_ip = self._cs_ip
        if 'eip' in kvargs:
            eip = int(kvargs['eip'])
            if eip > 0xFFFFFFFF:
                raise ValueError
            eip = bytearray.fromhex("{:08x}".format(eip))
        else:
            eip = self._eip
        if not isinit:
            if variant is None:
                variant = self._DEFAULT_VARIANT
            if bytesperline is None:
                bytesperline = self._DEFAULT_BYTES_PER_LINE
        return (bytesperline, variant, cs_ip, eip)

    def loadihexfile(self, frep, ignore_checksum_errors=False):
        if not hasattr(frep, "readline"):
            frep = open(frep, "r")
        highaddr = 0
        line = frep.readline()
        while line != '':
            (recordtype, lowaddress, data, datasize, checksumcorrect) = self._parseihexline(line)
            if not checksumcorrect and not ignore_checksum_errors:
                raise DecodeError("Checksum mismatch.")
            if recordtype == 0:
                self.set( (highaddr + lowaddress), data, datasize)
                if self._bytesperline is None:
                    self._bytesperline = datasize
            elif recordtype == 1:
                break
            elif recordtype == 2:
                highaddr = (data[0] << 12) | (data[1] << 4)
                if self._variant is None:
                    self._variant = 16
            elif recordtype == 3:
                self._cs_ip = data
                if self._variant is None:
                    self._variant = 16
            elif recordtype == 4:
                highaddr = (data[0] << 24) | (data[1] << 16)
                if self._variant is None:
                    self._variant = 32
            elif recordtype == 5:
                self._eip = data
                if self._variant is None:
                    self._variant = 32
            else:
                raise DecodeError("Unsupported record type.")
            line = frep.readline()
        return self

    def toihexfile(self, frep, **settings):
        (bytesperline, variant, cs_ip, eip) = self._parsesettings(False, **settings)
        opened = False
        if not hasattr(frep, "write"):
            opened = True
            frep = open(frep, "w")
        highaddr = 0
        addresshigh = 0
        addresslow = 0
        for address,buffer in self._parts:
            pos = 0
            datalength = len(buffer)
            while pos < datalength:
                if variant == 32:
                    addresslow  = address & 0x0000FFFF
                    addresshigh = address & 0xFFFF0000
                    if address > 0xFFFFFFFF:
                        raise EncodeError("Address to large for format.")
                elif variant == 16:
                    if address > 0xFFFFF:
                        raise EncodeError("Address to large for format.")
                    if address > (addresshigh + 0x0FFFF):
                        addresshigh = address & 0xFFF00
                    addresslow = address - addresshigh
                else:
                    addresslow = address
                    if address > 0xFFFF:
                        raise EncodeError("Address to large for format.")
                if addresshigh != highaddr:
                    highaddr = addresshigh
                    if variant == 32:
                        frep.write(self._encodeihexline(4, 0, [addresshigh>>24, (addresshigh>>16) & 0xFF]))
                    else:
                        frep.write(self._encodeihexline(2, 0, [addresshigh>>12, (addresshigh>>4) & 0xFF]))
                endpos = min( pos + bytesperline, datalength )
                frep.write(self._encodeihexline(0, addresslow, buffer[pos:endpos]))
                address += bytesperline
                pos = endpos
        if variant == 32 and eip is not None:
            frep.write(self._encodeihexline(5, 0, eip))
        elif variant == 16 and cs_ip is not None:
            frep.write(self._encodeihexline(3, 0, cs_ip))
        frep.write(self._encodeihexline(1))
        if opened:
            frep.close()

