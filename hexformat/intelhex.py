      
from multipartbuffer import MultiPartBuffer


RT_DATA = 0
RT_END_OF_FILE  = 1
RT_EXTENDED_SEGMENT_ADDRESS = 2
RT_START_SEGMENT_ADDRESS = 3
RT_EXTENDED_LINEAR_ADDRESS = 4
RT_START_LINEAR_ADDRESS = 5


class DecodeError(Exception):
    pass

class IntelHex(MultiPartBuffer):
    _DATALENGTH = (None, 0, 2, 4, 2, 4)
    _bytesperline = 0x10
    _cs = None
    _ip = None
    _eip = None

    @classmethod
    def _parseline(cls, line):
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
            supposed_datalength = cls._DATALENGTH[recordtype]
        except IndexError:
            raise DecodeError("Unknown record type.")
        if supposed_datalength is not None and supposed_datalength != bytecount:
            raise DecodeError("Data length does not correspond to record type.")
        data = bytes[4:-1]
        return (recordtype, address, data, bytecount, checksumcorrect)
        
    @classmethod
    def _genline(cls, recordtype, address16bit=0, data=bytearray()):
        linelen = 2*len(data) + 11
        linetempl = ":{:02X}{:04X}{:02X}{:s}{:02X}\n"
        bytecount = len(data)
        try:
            supposed_datalength = cls._DATALENGTH[recordtype]
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
    def fromfile(cls, frep, format='hex'):
        format = format.lower()
        if format == 'hex':
            return cls.fromsrecfile(frep)
        elif format == 'bin':
            return cls.frombinfile(frep)

    @classmethod
    def fromhexfile(cls, frep):
        self = cls()
        self.loadhexfile(frep)
        return self
        
    def loadhexfile(self, frep):
        if not hasattr(frep, "readline"):
            frep = open(frep, "r")
        highaddr = 0
        line = frep.readline()
        while line != '':
            (recordtype, lowaddress, data, datasize, checksumcorrect) = self._parseline(line)
            if recordtype == 0:
                self.set( (highaddr + lowaddress), data, datasize)
            elif recordtype == 1:
                break
            elif recordtype == 2:
                highaddr = (data[0] << 12) | (data[1] << 4)
            elif recordtype == 3:
                self._cs_ip = data
            elif recordtype == 4:
                highaddr = (data[0] << 24) | (data[1] << 16)
            elif recordtype == 5:
                self._eip = data
            line = frep.readline()
        return self

    def tohexfile(self, frep):
        opened = False
        if not hasattr(frep, "write"):
            opened = True
            frep = open(frep, "w")
        highaddr = 0
        for address,buffer in self._parts:
            datalength = len(buffer)
            pos = 0
            while pos < datalength:
                addresslow = address & 0x0000FFFF
                addresshigh  = address & 0xFFFF0000
                endpos = min( pos + self._bytesperline, datalength )
                if addresshigh != highaddr:
                    highaddr = addresshigh
                    frep.write(self._genline(4, 0, [addresshigh>>24, addresshigh>>16]))            
                frep.write(self._genline(0, addresslow, buffer[pos:endpos]))
                pos = endpos
                address += self._bytesperline
        frep.write(self._genline(1))
        if opened:
            frep.close()
        return self        