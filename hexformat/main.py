from multipartbuffer import MultiPartBuffer, Buffer
import binascii
import string


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
        line = fh.readline()
        while line != '':
            (recordtype, address, data, datasize, crccorrect) = cls._parsesrecline(line)
            if recordtype >= 1 and recordtype <= 3:
                self.set(address, data, datasize)
            line = fh.readline()
        return self




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
        
    def __eq__(self, other):
        """Compare with other instance for equality."""
        return super(IntelHex, self).__cmp__(other) and self._eip == other._eip and self._cs_ip == other._cs_ip

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
    def fromihexfile(cls, filename, ignore_checksum_errors=False):
        with open(filename, "r") as fh:
            return cls.fromihexfh(fh, ignore_checksum_errors)    

    @classmethod
    def fromihexfh(cls, fh, ignore_checksum_errors=False):
        self = cls()
        self.loadihexfh(fh, ignore_checksum_errors)
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

    def loadihexfile(self, filename, ignore_checksum_errors=False):
        with open(filename, "r") as fh:
            return self.loadihexfh(fh, ignore_checksum_errors)    
        
    def loadihexfh(self, fh, ignore_checksum_errors=False):
        highaddr = 0
        line = fh.readline()
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
            line = fh.readline()
        return self

    def toihexfile(self, filename, **settings):
        with open(filename, "w") as fh:
            return self.toihexfh(filename, **settings)
    
    def toihexfh(self, fh, **settings):
        (bytesperline, variant, cs_ip, eip) = self._parsesettings(False, **settings)
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
                        fh.write(self._encodeihexline(4, 0, [addresshigh>>24, (addresshigh>>16) & 0xFF]))
                    else:
                        fh.write(self._encodeihexline(2, 0, [addresshigh>>12, (addresshigh>>4) & 0xFF]))
                endpos = min( pos + bytesperline, datalength )
                fh.write(self._encodeihexline(0, addresslow, buffer[pos:endpos]))
                address += bytesperline
                pos = endpos
        if variant == 32 and eip is not None:
            fh.write(self._encodeihexline(5, 0, eip))
        elif variant == 16 and cs_ip is not None:
            fh.write(self._encodeihexline(3, 0, cs_ip))
        fh.write(self._encodeihexline(1))


class HexDump(MultiPartBuffer):

    def _encodehexdumpline(self, address, data, bytesperline, groupsize, bigendian, ascii):
        groups = list()
        cgroup = list()
        for n,byte in enumerate(data, 1):
            cgroup.append("{:02X}".format(byte))
            if n % groupsize == 0:
                groups.append(cgroup)
                cgroup = list()
        if cgroup:
            while len(cgroup) < groupsize:
                cgroup.append("  ")
            groups.append(cgroup)
        datastr = " ".join(["".join(bigendian and group or reversed(group)) for group in groups])
        asciistr = ""
        if ascii:
            asciistr = " |{{:{:d}s}}|".format(bytesperline).format("".join([char in string.printable and char or "." for char in str(data)]))
        numgroups = bytesperline/groupsize 
        hwidth = bytesperline * 2 + numgroups - 1
        return "{{:08X}}: {{:{:d}s}}{{:s}}\n".format(hwidth).format(address, datastr, asciistr)

    def _parsehexdumpline(self, line, bigendian):
        try:
            line = line.rstrip("\r\n")
            cidx = line.index(":")
            aidx = line.find("|")
            if aidx == -1:
                aidx = None
            address = int(line[0:cidx], 16)
            groups = line[cidx+1:aidx].split()
            data = Buffer()
            for group in groups:
                groupdata = Buffer.fromhex(group)
                if not bigendian:
                    groupdata = reversed(groupdata)
                data.extend(groupdata)
            return (address, data)
        except Exception as e:
            raise DecodeError("Invalid formatted input line: " + str(e))

    def tohexdumpfile(self, filename, bytesperline=16, groupsize=1, bigendian=True, ascii=True):
        with open(filename, "w") as fh:
            self.tohexdumpfh(fh, bytesperline, groupsize, bigendian, ascii)

    def tohexdumpfh(self, fh, bytesperline=16, groupsize=1, bigendian=True, ascii=True):
        groupsize = int(groupsize)
        if (bytesperline % groupsize) != 0:
            bytesperline = int(round( float(bytesperline) / groupsize )) * groupsize
        for address,buffer in self._parts:
            pos = 0
            datalength = len(buffer)
            while pos < datalength:
                endpos = min( pos + bytesperline, datalength )
                fh.write(self._encodehexdumpline(address, buffer[pos:endpos], bytesperline, groupsize, bigendian, ascii))
                address += bytesperline
                pos = endpos

    @classmethod
    def fromhexdumpfile(cls, filename, bigendian=True):
        with open(filename, "r") as fh:
            return cls.fromhexdumpfh(fh, bigendian)

    @classmethod
    def fromhexdumpfh(cls, fh, bigendian=True):
        self = cls()
        self.loadhexdumpfh(fh, bigendian)
        return self
        
    def loadhexdumpfile(self, filename, bigendian=True):
        with open(filename, "r") as fh:
            return cls.loadhexdumpfh(fh, bigendian)
        
    def loadhexdumpfh(self, fh, bigendian=True):
        line = fh.readline()
        while line != '':
            (address, data) = self._parsehexdumpline(line, bigendian)
            self.set(address, data)
            line = fh.readline()
        return self