from multipartbuffer import MultiPartBuffer
import binascii

class SRecord(MultiPartBuffer):
    """Motorola S-Record hex file representation class.

       The SRecord class is able to parse and generate binary data in the S-Record representation.
    """

    _SRECORD_ADDRESSLENGTH = (2,2,3,4,None,2,None,4,3,2)
    _STANDARD_FORMAT = 'srec'

    @classmethod
    def _parsesrecline(cls, line):
        """Parse S-Record line and return decoded parts as tuple."""
        try:
            line = line.rstrip("\r\n")
            startcode = line[0]
            if startcode != "S":
                raise ValueError
            recordtype = int(line[1])
            bytes = bytearray.fromhex(line[2:])
        except:
            raise ValueError
        bytecount = bytes[0]
        if bytecount != len(bytes)-1:
            raise ValueError
        crccorrect = ( (sum(bytes) & 0xFF) == 0xFF)
        al = cls._SRECORD_ADDRESSLENGTH[recordtype]
        address = int(line[4:4+2*al], 16)
        datasize = bytecount - al - 1
        data = bytes[1+al:-1]
        return (recordtype, address, data, datasize, crccorrect)

    @staticmethod
    def _s123addr(addresslength, address):
        """Returns a tuple with the address bytes with the given length for encoding."""
        if addresslength == 2:
            return ( ((address >> 8) & 0xFF), (address & 0xFF) )
        elif addresslength == 3:
            return ( ((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF) )
        elif addresslength == 4:
            return ( ((address >> 24) & 0xFF), ((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF) )
        else:
            raise ValueError

    @staticmethod
    def _addresslength(address):
        """Returns minimum length in bytes from given address."""
        addresslength = 0
        if address <= 0xFFFF:
            addresslength = 2
        elif address <= 0xFFFFFF:
            addresslength = 3
        else:
            addresslength = 4
        return addresslength

    @classmethod
    def _encodesrecline(cls, fh, address, buffer, offset=0, recordtype=123, bytesperline=32):
        """Encode given data to a S-Record line."""
        lastaddress = address + len(buffer) - 1
        if recordtype == 123:
            recordtype = cls._addresslength(lastaddress) - 1
        try:
            recordtype = int(recordtype)
            addresslength = int(cls._SRECORD_ADDRESSLENGTH[recordtype])
        except IndexError, TypeError:
            raise ValueError

        bytesperline = max(addresslength+2, min(bytesperline, 254-addresslength))
        bytecount = bytesperline + addresslength + 1
        numrecords = 0
        while address < lastaddress or numrecords == 0:
            numrecords += 1
            if address + bytesperline > lastaddress:
                bytesperline = lastaddress - address + 1
                bytecount = bytesperline + addresslength + 1
            linebuffer = bytearray([0,] * (bytecount+1))
            linebuffer[0] = bytecount
            linebuffer[1:addresslength+1] = cls._s123addr(addresslength, address)
            linebuffer[addresslength+1:bytecount] = buffer[offset:offset+bytesperline]
            linebuffer[bytecount] = ((~sum(linebuffer)) & 0xFF)
            line = "".join(["S", str(recordtype), binascii.hexlify(linebuffer).upper(), "\n"])
            fh.write(line)
            offset += bytesperline
            address += bytesperline
        return numrecords

    def tosrecfile(cls, filename, bytesperline=32, addresslength=None):
        """Writes content as S-Record file to given file name."""
        with open(filename, "w") as fh:
            cls.tosrecfh(fh, bytesperline, addresslength)

    def tosrecfh(self, fh, bytesperline=32, addresslength=None):
        """Writes content as S-Record file to given file handle."""
        numrecords = 0
        start, size = self.range()
        if addresslength is None:
            lastaddress = start + size - 1
            addresslength = self._addresslength(lastaddress)
        recordtype = addresslength - 1
        recordtype_end = 11 - addresslength
        for address, buffer in self._parts:
            numrecords += self._encodesrecline(fh, address, buffer, recordtype=recordtype, bytesperline=bytesperline)
        self._encodesrecline(fh, 0, self._s123addr(2, numrecords), recordtype=5, bytesperline=bytesperline)
        self._encodesrecline(fh, start, [], recordtype=recordtype_end, bytesperline=bytesperline)

    @classmethod
    def fromsrecfile(cls, filename):
        """Generates SRecord instance from S-Record file."""
        with open(filename, "r") as fh:
            cls.fromsrecfh(fh)

    @classmethod
    def fromsrecfh(cls, fh):
        """Generates SRecord instance from file handle which must point to S-Record lines."""
        self = cls()
        self.loadsrecfh(fh)
        return self

    def loadsrecfh(self, fh):
        """Loads data from S-Record file over file handle."""
        line = frep.readline()
        while line != '':
            (recordtype, address, data, datasize, crccorrect) = cls._parsesrecline(line)
            if recordtype >= 1 and recordtype <= 3:
                self.set(address, data, datasize)
            line = frep.readline()
        return self
