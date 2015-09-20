""" Provide classes to handle IntelHex, SRecord and HexDump content.

  License::

    Copyright (C) 2015  Martin Scharrer <martin@scharrer-online.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

  Attributes:
    RT_DATA (int constant=0): Intel-Hex record type number for data record.
    RT_END_OF_FILE (int constant=1): Intel-Hex record type number for end of file record.
    RT_EXTENDED_SEGMENT_ADDRESS (int constant=2): Intel-Hex record type number for extend segment address record.
    RT_START_SEGMENT_ADDRESS (int constant=3): Intel-Hex record type number for start segment address record.
    RT_EXTENDED_LINEAR_ADDRESS (int constant=4): Intel-Hex record type number for extended linear address record.
    RT_START_LINEAR_ADDRESS (int constant=5): Intel-Hex record type number for start linear address record.
"""

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
    """Motorola `S-Record`_ hex file representation class.

       The SRecord class is able to parse and generate binary data in the S-Record representation.

       Attributes:
         _SRECORD_ADDRESSLENGTH (tuple): Address length in bytes for each record type.
         _STANDARD_FORMAT (str): The standard format used by :meth:`.fromfh` and :meth:`.fromfile` if no format was given.
         _start_address (int): Starting execution location. This tells the programmer which address contains the start routine. Default: 0.
         _header (data buffer or None): Header data written using record type 0 if not None. The content is application specific.

       .. _`S-Record`: http://en.wikipedia.org/wiki/SREC_%28file_format%29
    """

    _SRECORD_ADDRESSLENGTH = (2,2,3,4,None,2,None,4,3,2)
    _STANDARD_FORMAT = 'srec'
    _start_address = 0
    _header = None

    @classmethod
    def _parsesrecline(cls, line):
        """Parse S-Record line and return decoded parts as tuple.

           Args:
             line (str): Single input line, usually with line termination character(s).

           Returns:
             Tuple (recordtype, address, data, datasize, crccorrect) with types (int, int, Buffer, int, bool).

           Raises:
             DecodeError: if line does not start with start code ("S").
             DecodeError: on misformatted S-Record input line.
             DecodeError: on byte count - line data mismatch.
        """
        try:
            line = line.rstrip("\r\n")
            startcode = line[0]
            if startcode != "S":
                raise DecodeError("No valid S-Record start code found.")
            recordtype = int(line[1])
            bytes = bytearray.fromhex(line[2:])
        except:
            raise DecodeError("misformatted S-Record line.")
        bytecount = bytes[0]
        if bytecount != len(bytes)-1:
            raise DecodeError("Byte count does not match line data.")
        crccorrect = ( (sum(bytes) & 0xFF) == 0xFF)
        al = cls._SRECORD_ADDRESSLENGTH[recordtype]
        address = int(line[4:4+2*al], 16)
        datasize = bytecount - al - 1
        data = bytes[1+al:-1]
        return (recordtype, address, data, datasize, crccorrect)

    @staticmethod
    def _s123addr(addresslength, address):
        """Returns a tuple with the address bytes with the given length for encoding.

           Args:
             addresslength (int: 2..4): Address length in bytes. Valid values are 2, 3 or 4.
             address (int): Address to be encoded.

           Returns:
             Tuple with address bytes in big endian byte order (MSB first).
             The length of the tuple is equal to the addresslength argument.

           Raises:
             ValueError: If addresslength is not 2, 3 or 4.
        """
        if addresslength == 2:
            return ( ((address >> 8) & 0xFF), (address & 0xFF) )
        elif addresslength == 3:
            return ( ((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF) )
        elif addresslength == 4:
            return ( ((address >> 24) & 0xFF), ((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF) )
        else:
            raise ValueError("Invalid address length. Valid values are 2, 3 or 4.")

    @staticmethod
    def _minaddresslength(address):
        """Returns minimum byte length required to encode given address.

           Args:
             address (int): Address to be encoded.

           Returns:
             addresslength (int): Minimum number of bytes required to encode given address.

           Raise:
             ValueError: If address is too large to fit in 32 bit.
        """
        addresslength = 0
        if address <= 0xFFFF:
            addresslength = 2
        elif address <= 0xFFFFFF:
            addresslength = 3
        elif address <= 0xFFFFFFFF:
            addresslength = 4
        else:
            raise ValueError("Address must not be larger than 32 bit.")
        return addresslength

    @classmethod
    def _encodesrecline(cls, fh, address, buffer, offset=0, recordtype=123, bytesperline=32):
        """Encode given data to a S-Record line.

           One or more S-Record lines are encoded from the given address and buffer and written to the given file handle.

           Args:
             fh (file handle or compatible): Destination of S-Record lines.
             address (int): Address of first byte in buffer data.
             buffer (Buffer): Buffer with data to be encoded.
             offset (int): Reading start index of buffer.
             recordtype (int: 0..9 or 123): S-Record record type. If equal to 123 the a record type 1, 2 or 3 is determined by the minimum address byte width.
             bytesperline (int): Number of bytes to be written on a single line.

           Raises:
             EncodeError: on unsupported record type.
        """
        lastaddress = address + len(buffer) - 1
        if recordtype == 123:
            recordtype = cls._minaddresslength(lastaddress) - 1
        try:
            recordtype = int(recordtype)
            addresslength = int(cls._SRECORD_ADDRESSLENGTH[recordtype])
        except (IndexError, TypeError):
            raise EncodeError("Unsupported record type.")

        bytesperline = max(addresslength+2, min(bytesperline, 254-addresslength))
        bytecount = bytesperline + addresslength + 1
        numdatarecords = 0
        while address < lastaddress or numdatarecords == 0:
            numdatarecords += 1
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
        return numdatarecords

    def tosrecfile(cls, filename, bytesperline=32, addresslength=None, write_number_of_records=True):
        """Writes content as S-Record file to given file name.

           Opens filename for writing and calls :meth:`tosrecfh` with the file handle and all arguments.
           See :meth:`tosecfh` for description of the arguments.

           Returns:
             self
        """
        with open(filename, "w") as fh:
            return cls.tosrecfh(fh, bytesperline, addresslength, write_number_of_records, variant)

    def tosrecfh(self, fh, bytesperline=32, addresslength=None, write_number_of_records=True):
        """Writes content as S-Record file to given file handle.

           Args:
             fh (file handle or compatible): Destination of S-Record lines.
             bytesperline (int): Number of data bytes per line.
             addresslength (None or int in range 2..4): Address length in bytes. This determines the used file format variant.
                    If None then the shortest possible address length large enough to encode the highest address present is used.
             write_number_of_records (bool): If True then the number of data records is written as a record type 5 or 6.
                                             This adds an additional verification method if the S-Record file is consistent.

           Returns:
             self
        """
        numdatarecords = 0
        start, size = self.range()
        if addresslength is None:
            lastaddress = start + size - 1
            addresslength = self._minaddresslength(lastaddress)
        recordtype = addresslength - 1
        recordtype_end = 10 - recordtype
        if self._header is not None:
            self._encodesrecline(fh, 0, self._header, recordtype=0, bytesperline=32)
        for address, buffer in self._parts:
            numdatarecords += self._encodesrecline(fh, address, buffer, recordtype=recordtype, bytesperline=bytesperline)
        if write_number_of_records:
            if numdatarecords <= 0xFFFF:
                self._encodesrecline(fh, 0, self._s123addr(2, numdatarecords), recordtype=5, bytesperline=32)
            elif numdatarecords <= 0xFFFFFF:
                self._encodesrecline(fh, 0, self._s123addr(3, numdatarecords), recordtype=6, bytesperline=32)
        self._encodesrecline(fh, start, self._s123addr(recordtype, self._start_address), recordtype=recordtype_end, bytesperline=32)
        return self

    @classmethod
    def fromsrecfile(cls, filename):
        """Generates SRecord instance from S-Record file.

           Opens filename for reading and calls :meth:`fromsrecfh` with the file handle.

           Args:
             filename (str): Name of S-Record file.

           Returns:
             New instance of class with loaded data.
        """
        with open(filename, "r") as fh:
            return cls.fromsrecfh(fh)

    @classmethod
    def fromsrecfh(cls, fh):
        """Generates SRecord instance from file handle which must point to S-Record lines.

           Creates new instance and calls :meth:`loadsrecfh` on it.

           Args:
             fh (file handle or compatible): Source of S-Record lines.

           Returns:
             New instance of class with loaded data.
        """
        self = cls()
        self.loadsrecfh(fh)
        return self
        
    def loadsrecfile(self, filename, raise_error_on_miscount=True):
        """Loads S-Record lines from named file.

           Creates new instance and calls :meth:`loadsrecfh` on it.

           Args:
             filename (str): Name of S-Record file.
             raise_error_on_miscount (bool): If True a DecodeError is raised if the number of records read differs from stored number of records.

           Returns:
             self
        """
        with open(filename, "r") as fh:
            return self.loadsrecfh(fh, raise_error_on_miscount)        

    def loadsrecfh(self, fh, raise_error_on_miscount=True):
        """Loads data from S-Record file over file handle.

           Parses every source line using :meth:`_parsesrecline` and processes the decoded elements according to the record type.

           Args:
             fh (file handle or compatible): Source of S-Record lines.
             raise_error_on_miscount (bool): If True a DecodeError is raised if the number of records read differs from stored number of records.

           Returns:
             self

           Raises:
             DecodeError: If decoded record type is outside of range 0..9.
             DecodeError: If raise_error_on_miscount is True and number of records read differ from stored number of records.
        """
        line = fh.readline()
        numdatarecords = 0
        while line != '':
            (recordtype, address, data, datasize, crccorrect) = cls._parsesrecline(line)
            if recordtype >= 1 and recordtype <= 3:
                self.set(address, data, datasize)
                numdatarecords += 1
            elif recordtype == 0:
                self._header = data
            elif recordtype == 5 or recordtype == 6:
                if raise_error_on_miscount and numdatarecords != address:
                    raise DecodeError("Number of records read ({:d}) differs from stored number of records ({:d}).".format(numdatarecords,address))
            elif recordtype >=7 and recordtype <= 9:
                self._start_address = address
            else:
                raise DecodeError("Unsupported record type " + str(recordtype))
            line = fh.readline()
        return self

    def getstartaddress(self):
        """Getter mehtod of starting execution location.

           Returns:
             address (int): starting execution location.
        """
        return self._start_address

    def setstartaddress(self, start_address):
        """Sets starting execution location.

           Args:
             start_address (int): 16, 24 or 32 bit address of the starting execution location, i.e. where the start-up routine is located in the program data.

           Returns:
             self

           Raises:
             ValueError: if address is too large for 32 bit.
        """
        start_address = int(start_address)
        if start_address > 0xFFFFFFFF:
            raise ValueError("Start address must fit to 32-bit width.")
        self._start_address = start_address
        return self

    def getheader(self):
        """Return header data which is stored using record type 0.
           The header data usually

           Returns:
             Buffer (str): NULL ("\\\\x00") terminated string.
        """
        return self._header

    def setheader(self, header):
        """Sets S-Record header which will be written using record type 0.

           Args:
             header (None or str): Header data. A vendor specific ASCII text which can contains e.g.
                file/module name, version/revision number, date/time, product name, vendor name, memory designator on PCB, copyright notice.
                If None no header will be written.
                Will be truncated to a length of 251 if longer.
                If it does not end with a NULL ("\\\\x00") character, one is added.

           Returns:
             self
        """
        if header is None:
            self._header = None
        else:
            self._header = str(header)
            if len(self._header) >= 252:
                self._header = self._header[0:252]
                self._header += "\x00"
            elif self._header[-1] != "\x00":
                self._header += "\x00"
        return self


class IntelHex(MultiPartBuffer):
    """`Intel-Hex`_ file representation class.

       The IntelHex class is able to parse and generate binary data in the Intel-Hex representation.

       Args:
         bytesperline (int): Number of bytes per line.
         variant: Variant of Intel-Hex format. Must be one out of ('I08HEX', 'I8HEX', 'I16HEX', 'I32HEX', 8, 16, 32).
         cs_ip (int, 32-bit): Value of CS:IP starting address used for I16HEX variant.
         eip (int, 32-bit): Value of EIP starting address used for I32HEX variant.

       Attributes:
         _DATALENGTH (tuple): Data length according to record type.
         _VARIANTS (dict): Mapping dict from variant name to number.
         _DEFAULT_BYTES_PER_LINE (int): Default number of bytes per line.
         _DEFAULT_VARIANT: Default variant.
         _bytesperline (None or int): Number of bytes per line of this instance. If None the default value will be used.
         _cs_ip (None or int): CS:IP address for I16HEX variant. If None no CS:IP address will be written.
         _eip (None or int): EIP address for I32HEX variant. If None no CS:IP address will be written.
         _variant (None or 8, 16 or 32): Numeric file format variant. If None the default variant is used.

       .. _`Intel-Hex`: http://en.wikipedia.org/wiki/Intel_HEX
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
        """Parse Intel-Hex line and return decoded parts as tuple.

           Args:
             line (str): Single input line, usually with line termination character(s).

           Returns:
             Tuple (recordtype, address, data, bytecount, crccorrect) with types (int, int, Buffer, int, bool).

           Raises:
             DecodeError: on lines which do not start with start code (":").
             DecodeError: on data length - byte count mismatch.
             DecodeError: on unknown record type.
             DecodeError: on data length - record type mismatch.
        """
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
        """Encode given data to Intel-Hex format.

           One or more Intel-Hex lines are encoded from the given address and buffer and written to the given file handle.

           Args:
             recordtype (int: 0..5): Intel-Hex record type.
             address16bit (int): Lower 16-bit part of address of first byte in buffer data.
             data (Buffer): Buffer with data to be encoded.

           Returns:
             line (str): Intel-Hex encoded line.

           Raises:
             DecodeError: on unknown record type.
             DecodeError: on datalength - record type mismatch.
        """
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
        """Generates IntelHex instance from Intel-Hex file.

           Opens filename for reading and calls :meth:`fromihexfh` with the file handle.

           Args:
             ignore_checksum_errors (bool): If True no error is raised on checksum failures.

           Returns:
             New instance of class with loaded data.
        """
        with open(filename, "r") as fh:
            return cls.fromihexfh(fh, ignore_checksum_errors)

    @classmethod
    def fromihexfh(cls, fh, ignore_checksum_errors=False):
        """Generates IntelHex instance from file handle which must point to Intel-Hex lines.

           Creates new instance and calls :meth:`loadihexfh` on it.

           Args:
             fh (file handle or compatible): Source of Intel-Hex lines.
             ignore_checksum_errors (bool): If True no error is raised on checksum failures.

           Returns:
             New instance of class with loaded data.
        """
        self = cls()
        self.loadihexfh(fh, ignore_checksum_errors)
        return self

    def settings(self, **kvargs):
        """Sets setting.

           Calls :meth:`_parsesettings` with the key-value pairs and stores the result in instance attributes.

           Args:
             bytesperline (int): Number of bytes per line.
             variant: Variant of Intel-Hex format. Must be one out of ('I08HEX', 'I8HEX', 'I16HEX', 'I32HEX', 8, 16, 32).
             cs_ip (int, 32-bit): Value of CS:IP starting address used for I16HEX variant.
             eip (int, 32-bit): Value of EIP starting address used for I32HEX variant.

           Returns:
             self
        """
        (self._bytesperline, self._variant, self._cs_ip, self._eip) = self._parsesettings(True, **kvargs)
        return self

    def _parsesettings(self, isinit, **kvargs):
        """Parses settings and returns tuple with all settings. Default values are substituted if needed.

           Args:
             isinit (bool): If False substitute None values with default values.
             bytesperline (int): Number of bytes per line.
             variant: Variant of Intel-Hex format. Must be one out of ('I08HEX', 'I8HEX', 'I16HEX', 'I32HEX', 8, 16, 32).
             cs_ip (int, 32-bit): Value of CS:IP starting address used for I16HEX variant.
             eip (int, 32-bit): Value of EIP starting address used for I32HEX variant.

           Returns:
             Tuple with settings: (bytesperline, variant, cs_ip, eip)

           Raises:
             ValueError: If cs_ip or eip value is larger than 32 bit.
        """
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
                raise ValueError("cs_ip value must not be larger than 32 bit.")
            cs_ip = bytearray.fromhex("{:08x}".format(cs_ip))
        else:
            cs_ip = self._cs_ip
        if 'eip' in kvargs:
            eip = int(kvargs['eip'])
            if eip > 0xFFFFFFFF:
                raise ValueError("eip value must not be larger than 32 bit.")
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
        """Loads Intel-Hex lines from named file.

           Creates new instance and calls :meth:`loadihexfh` on it.

           Args:
             filename (str): Name of Intel-Hex file.
             ignore_checksum_errors (bool): If True no error is raised on checksum failures.

           Returns:
             self
        """
        with open(filename, "r") as fh:
            return self.loadihexfh(fh, ignore_checksum_errors)

    def loadihexfh(self, fh, ignore_checksum_errors=False):
        """Loads Intel-Hex lines from file handle.

           Args:
             fh (file handle or compatible): Source of Intel-Hex lines.
             ignore_checksum_errors (bool): If True no error is raised on checksum failures.

           Returns:
             self

           Raises:
             DecodeError: on checksum mismatch if ignore_checksum_errors is False.
             DecodeError: on unsupported record type.
        """
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
        """Writes content as Intel-Hex file to given file name.

           Opens filename for writing and calls :meth:`toihexfh` with the file handle and all arguments.
           See :meth:`toihexfh` for description of the arguments.

           Args:
             bytesperline (int): Number of bytes per line.
             variant: Variant of Intel-Hex format. Must be one out of ('I08HEX', 'I8HEX', 'I16HEX', 'I32HEX', 8, 16, 32).
             cs_ip (int, 32-bit): Value of CS:IP starting address used for I16HEX variant.
             eip (int, 32-bit): Value of EIP starting address used for I32HEX variant.

           Returns:
             self
        """
        with open(filename, "w") as fh:
            return self.toihexfh(fh, **settings)

    def toihexfh(self, fh, **settings):
        """Writes content as Intel-Hex file to given file handle.

           Args:
             fh (file handle or compatible): Destination of S-Record lines.
             bytesperline (int): Number of bytes per line.
             variant: Variant of Intel-Hex format. Must be one out of ('I08HEX', 'I8HEX', 'I16HEX', 'I32HEX', 8, 16, 32).
             cs_ip (int, 32-bit): Value of CS:IP starting address used for I16HEX variant.
             eip (int, 32-bit): Value of EIP starting address used for I32HEX variant.

           Returns:
             self

           Raises:
             EncodeError: if selected address length is not wide enough to fit all addresses.
        """
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
        return self

    def __eq__(self, other):
        """Compare with other instance for equality.

           Both instances are equal if both _parts lists, _eip and _cs_ip are identical.
        """
        return super(IntelHex, self).__eq__(other) and self._eip == other._eip and self._cs_ip == other._cs_ip


class HexDump(MultiPartBuffer):
    """`Hex dump`_ representation class.

       The HexDump class is able to generate and parse hex dumps of binary data.

       .. _`Hex dump`: http://en.wikipedia.org/wiki/Hex_dump
    """

    def _encodehexdumpline(self, address, data, bytesperline, groupsize, bigendian, ascii):
        """Return encoded hex dump line.

           Args:
             address (int): Address of first byte in buffer.
             data (Buffer): To be encoded data.
             bytesperline (int): Number of data bytes per line.
             groupsize (int): Number of data bytes to be grouped together.
             bigendian (bool): If True the bytes in a group are written in big endian (Motorola style, MSB first) order,
                               otherwise in little endian (Intel style, LSB first) order.
             ascii (bool): If True the ASCII representation is written after the hex values.

           Returns:
             Encoded hex dump line.
        """
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
        """Parses hex dump line to extract address and data.

           Args:
             line (str): Hex dump line to be parsed.
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style, MSB first) order,
                               otherwise in little endian (Intel style, LSB first) order.

           Returns:
             Tuple (address, data) with types (int, Buffer).
        """
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

    @classmethod
    def fromhexdumpfile(cls, filename, bigendian=True):
        """Generates HexDump instance from hex dump file.

           Opens filename for reading and calls :meth:`fromhexdumpfh` with the file handle.

           Args:
             filename (str): Name of file to be loaded.
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style, MSB first) order,
                               otherwise in little endian (Intel style, LSB first) order.

           Returns:
             New instance of class with loaded data.
        """
        with open(filename, "r") as fh:
            return cls.fromhexdumpfh(fh, bigendian)

    @classmethod
    def fromhexdumpfh(cls, fh, bigendian=True):
        """Generates HexDump instance from file handle which must point to hex dump lines.

           Creates new instance and calls :meth:`loadhexdumpfh` on it.

           Args:
             fh (file handle or compatible): Source of Intel-Hex lines.
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style, MSB first) order,
                               otherwise in little endian (Intel style, LSB first) order.

           Returns:
             New instance of class with loaded data.
        """
        self = cls()
        self.loadhexdumpfh(fh, bigendian)
        return self

    def loadhexdumpfile(self, filename, bigendian=True):
        """Loads hex dump lines from named file.

           Args:
             filename (str): Name of file to be loaded.
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style, MSB first) order,
                               otherwise in little endian (Intel style, LSB first) order.

           Returns:
             self
        """
        with open(filename, "r") as fh:
            return cls.loadhexdumpfh(fh, bigendian)

    def loadhexdumpfh(self, fh, bigendian=True):
        """Loads hex dump lines from file handle.

           Args:
             fh (file handle or compatible): Source of Intel-Hex lines.
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style, MSB first) order,
                               otherwise in little endian (Intel style, LSB first) order.

           Returns:
             self
        """
        line = fh.readline()
        while line != '':
            (address, data) = self._parsehexdumpline(line, bigendian)
            self.set(address, data)
            line = fh.readline()
        return self

    def tohexdumpfile(self, filename, bytesperline=16, groupsize=1, bigendian=True, ascii=True):
        """Writes hex dump to named file.

           Opens filename for writing and calls :meth:`.tohexdumpfh` on it.

           Args:
             filename (str): Name of file to be written.
             bytesperline (int): Number of data bytes per line.
             groupsize (int): Number of data bytes to be grouped together.
             bigendian (bool): If True the bytes in a group are written in big endian (Motorola style, MSB first) order,
                               otherwise in little endian (Intel style, LSB first) order.
             ascii (bool): If True the ASCII representation is written after the hex values.

           Returns:
             self
        """
        with open(filename, "w") as fh:
            return self.tohexdumpfh(fh, bytesperline, groupsize, bigendian, ascii)

    def tohexdumpfh(self, fh, bytesperline=16, groupsize=1, bigendian=True, ascii=True):
        """Writes hex dump to file handle.

           Args:
             fh (file handle or compatible): File handle to be written to.
             bytesperline (int): Number of data bytes per line.
             groupsize (int): Number of data bytes to be grouped together.
             bigendian (bool): If True the bytes in a group are written in big endian (Motorola style, MSB first) order,
                               otherwise in little endian (Intel style, LSB first) order.
             ascii (bool): If True the ASCII representation is written after the hex values.

           Returns:
             self
        """
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
        return self
        