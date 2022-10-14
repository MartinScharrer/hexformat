""" Provide class to handle Motorola SRecord content.

  License::

    MIT License

    Copyright (c) 2015-2022 by Martin Scharrer <martin.scharrer@web.de>

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software
    and associated documentation files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
    BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import binascii

from hexformat.base import DecodeError, EncodeError, HexFormat

BYTESPERLINE_MAX = 253


# noinspection PyPep8Naming
class RECORD_TYPE(object):
    S0 = 0
    S1 = 1
    S2 = 2
    S3 = 3
    S5 = 5
    S6 = 6
    S7 = 7
    S8 = 8
    S9 = 9
    HEADER = S0
    DATA_16 = S1
    DATA_24 = S2
    DATA_32 = S3
    COUNT_16 = S5
    COUNT_24 = S6
    FOOTER_32 = S7
    FOOTER_24 = S8
    FOOTER_16 = S9


class SRecord(HexFormat):
    """Motorola `S-Record`_ hex file representation class.

       The SRecord class is able to parse and generate binary data in the S-Record representation.

       Attributes:
         _SRECORD_ADDRESSLENGTH (tuple): Address length in bytes for each record type.
         _STANDARD_FORMAT (str): The standard format used by :meth:`.fromfh` and :meth:`.fromfile` if no format was
                                 given.
         _startaddress (int): Starting execution location. This tells the programmer which address contains the start
                              routine. Default: 0.
         _header (data buffer or None): Header data written using record type 0 if not None. The content is application
                                        specific.

       .. _`S-Record`: http://en.wikipedia.org/wiki/SREC_%28file_format%29
    """

    _SRECORD_ADDRESSLENGTH = (2, 2, 3, 4, 2, 2, 3, 4, 3, 2)
    _STANDARD_FORMAT = 'srec'
    _DEFAULT_HEADER = bytearray(b'')
    _DEFAULT_STARTADDRESS = 0
    _DEFAULT_ADDRESSLENGTH = None
    _DEFAULT_BYTESPERLINE = 32
    _DEFAULT_WRITE_NUMBER_OF_RECORDS = False
    _SETTINGS = ['startaddress', 'addresslength', 'bytesperline', 'header', 'write_number_of_records']

    def __init__(self, **settings):
        super(SRecord, self).__init__()
        self._startaddress = None
        self._addresslength = None
        self._bytesperline = None
        self._header = None
        self._write_number_of_records = None
        self.settings(**settings)

    @property
    def startaddress(self):
        return self._startaddress

    @startaddress.setter
    def startaddress(self, startaddress):
        self._startaddress = self._parse_startaddress(startaddress)

    @staticmethod
    def _parse_startaddress(startaddress):
        if startaddress is not None:
            startaddress = int(startaddress)
            if startaddress < 0 or startaddress > 0xFFFFFFFF:
                raise ValueError("startaddress must be between 0 and 0xFFFFFFFF")
        return startaddress

    @property
    def addresslength(self):
        return self._addresslength

    @addresslength.setter
    def addresslength(self, addresslength):
        self._addresslength = self._parse_addresslength(addresslength)

    @staticmethod
    def _parse_addresslength(addresslength):
        if addresslength is not None:
            addresslength = int(addresslength)
            if addresslength < 2 or addresslength > 4:
                raise ValueError("addresslength must be 2, 3 or 4 bytes")
        return addresslength

    @property
    def bytesperline(self):
        return self._bytesperline

    @bytesperline.setter
    def bytesperline(self, bytesperline):
        self._bytesperline = self._parse_bytesperline(bytesperline)

    @staticmethod
    def _parse_bytesperline(bytesperline):
        if bytesperline is not None:
            bytesperline = int(bytesperline)
            if bytesperline < 1 or bytesperline > 253:
                raise ValueError("bytesperline must be between 1 and 253")
        return bytesperline

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, header):
        self._header = self._parse_header(header)

    @staticmethod
    def _parse_header(header):
        if header is not None:
            header = bytearray(iter(header))[0:BYTESPERLINE_MAX]
        return header

    @property
    def write_number_of_records(self):
        return self._write_number_of_records

    @write_number_of_records.setter
    def write_number_of_records(self, write_number_of_records):
        self._write_number_of_records = self._parse_write_number_of_records(write_number_of_records)

    @staticmethod
    def _parse_write_number_of_records(write_number_of_records):
        if write_number_of_records is not None:
            write_number_of_records = bool(write_number_of_records)
        return write_number_of_records

    def tosrecfile(self, filename, **settings):
        """Writes content as S-Record file to given file name.

           Opens filename for writing and calls :meth:`tosrecfh` with the file handle and all arguments.
           See :meth:`tosecfh` for description of the arguments.

           Returns:
             self
        """
        with open(filename, "w") as fh:
            return self.tosrecfh(fh, **settings)

    # noinspection PyIncorrectDocstring
    def tosrecfh(self, fh, **settings):
        """Writes content as S-Record file to given file handle.

           Args:
             fh (file handle or compatible): Destination of S-Record lines.
             bytesperline (int): Number of data bytes per line.
             addresslength (None or int in range 2..4): Address length in bytes. This determines the used file format
                    variant. If None then the shortest possible address length large enough to encode the highest
                    address present is used.
             write_number_of_records (bool): If True then the number of data records is written as a record type 5 or 6.
                                         This adds an additional verification method if the S-Record file is consistent.

           Returns:
             self
        """
        (startaddress, addresslength, bytesperline, header, write_number_of_records) = self._parse_settings(**settings)

        if addresslength is None:
            start, size = self.range()
            endaddress = start + size - 1
            addresslength = self._minaddresslength(endaddress)

        recordtype = addresslength - 1
        recordtype_end = 10 - recordtype
        numdatarecords = 0

        if header:
            self._encodesrecline(fh, RECORD_TYPE.HEADER, 0, header, BYTESPERLINE_MAX)
        for address, buffer in self._parts:
            numdatarecords += self._encodesrecline(fh, recordtype, address, buffer, bytesperline)
        if write_number_of_records:
            if numdatarecords <= 0xFFFF:
                self._encodesrecline(fh, RECORD_TYPE.COUNT_16, numdatarecords, bytearray(), BYTESPERLINE_MAX)
            elif numdatarecords <= 0xFFFFFF:
                self._encodesrecline(fh, RECORD_TYPE.COUNT_24, numdatarecords, bytearray(), BYTESPERLINE_MAX)

        self._encodesrecline(fh, recordtype_end, startaddress, bytearray(), BYTESPERLINE_MAX)
        return self

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
        if address <= 0xFFFF:
            addresslength = 2
        elif address <= 0xFFFFFF:
            addresslength = 3
        elif address <= 0xFFFFFFFF:
            addresslength = 4
        else:
            raise ValueError("Address must not be larger than 32 bit.")
        return addresslength

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
        if not (2 <= addresslength <= 4):
            raise ValueError("Invalid address length (%s). Valid values are 2, 3 or 4." % (str(addresslength),))
        try:
            return address.to_bytes(addresslength, 'big')
        except AttributeError:
            if addresslength == 2:
                return ((address >> 8) & 0xFF), (address & 0xFF)
            elif addresslength == 3:
                return ((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF)
            else:
                return ((address >> 24) & 0xFF), ((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF)

    @classmethod
    def _encodesrecline(cls, fh, recordtype, address, buffer, bytesperline=32):
        """Encode given data to a S-Record line.

           One or more S-Record lines are encoded from the given address and buffer and written to the given
           file handle.

           Args:
             fh (file handle or compatible): Destination of S-Record lines.
             recordtype (int: 0..3, 5..9): S-Record record type. If equal to 123 the a record type 1, 2 or 3 is
                                           determined by the minimum address byte width.
             address (int): Address of first byte in buffer data.
             buffer (Buffer): Buffer with data to be encoded.
             bytesperline (int): Number of bytes to be written on a single line.

           Raises:
             EncodeError: on unsupported record type.
        """
        endaddress = address + len(buffer)
        try:
            recordtype = int(recordtype)
            addresslength = int(cls._SRECORD_ADDRESSLENGTH[recordtype])
        except (IndexError, TypeError, ValueError):
            raise EncodeError("Unsupported record type.")

        bytesperline = max(1, min(bytesperline, 254 - addresslength))
        bytecount = bytesperline + addresslength + 1
        numdatarecords = 0
        pos = 0
        while address < endaddress or numdatarecords == 0:
            numdatarecords += 1
            if address + bytesperline > endaddress:
                bytesperline = endaddress - address
                bytecount = bytesperline + addresslength + 1
            linebuffer = bytearray([0, ] * (bytecount + 1))
            linebuffer[0] = bytecount
            linebuffer[1:addresslength + 1] = cls._s123addr(addresslength, address)
            linebuffer[addresslength + 1:bytecount] = buffer[pos:pos + bytesperline]
            linebuffer[bytecount] = ((~sum(linebuffer)) & 0xFF)
            line = "".join(["S", str(recordtype), binascii.hexlify(linebuffer).upper().decode(), "\n"])
            fh.write(line)
            pos += bytesperline
            address += bytesperline
        return numdatarecords

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
            databytes = bytearray.fromhex(line[2:])
        except:
            raise DecodeError("misformatted S-Record line.")
        bytecount = databytes[0]
        if bytecount != len(databytes) - 1:
            raise DecodeError("Byte count does not match line data.")
        crccorrect = ((sum(databytes) & 0xFF) == 0xFF)
        al = cls._SRECORD_ADDRESSLENGTH[recordtype]
        address = int(line[4:4 + 2 * al], 16)
        datasize = bytecount - al - 1
        data = databytes[1 + al:-1]
        return recordtype, address, data, datasize, crccorrect

    @classmethod
    def fromsrecfile(cls, filename, raise_error_on_miscount=True):
        """Generates SRecord instance from S-Record file.

           Opens filename for reading and calls :meth:`fromsrecfh` with the file handle.

           Args:
             filename (str): Name of S-Record file.
             raise_error_on_miscount (bool): If True a DecodeError is raised if the number of records read differs from
                                             stored number of records.

           Returns:
             New instance of class with loaded data.
        """
        with open(filename, "r") as fh:
            return cls.fromsrecfh(fh, raise_error_on_miscount)

    @classmethod
    def fromsrecfh(cls, fh, raise_error_on_miscount=True):
        """Generates SRecord instance from file handle which must point to S-Record lines.

           Creates new instance and calls :meth:`loadsrecfh` on it.

           Args:
             fh (file handle or compatible): Source of S-Record lines.
             raise_error_on_miscount (bool): If True a DecodeError is raised if the number of records read differs from
                                             stored number of records.

           Returns:
             New instance of class with loaded data.
        """
        self = cls()
        self.loadsrecfh(fh, raise_error_on_miscount=raise_error_on_miscount)
        return self

    def loadsrecfile(self, filename, overwrite_metadata=False, overwrite_data=True, raise_error_on_miscount=True):
        """Loads S-Record lines from named file.

           Creates new instance and calls :meth:`loadsrecfh` on it.

           Args:
             filename (str): Name of S-Record file.
             overwrite_metadata (bool): If True existing metadata will be overwritten.
             overwrite_data (bool): If True existing data will be overwritten.
             raise_error_on_miscount (bool): If True a DecodeError is raised if the number of records read differs from
                                             stored number of records.

           Returns:
             self
        """
        with open(filename, "r") as fh:
            return self.loadsrecfh(fh, overwrite_metadata, overwrite_data, raise_error_on_miscount)

    def loadsrecfh(self, fh, overwrite_metadata=False, overwrite_data=True, raise_error_on_miscount=True):
        """Loads data from S-Record file over file handle.

           Parses every source line using :meth:`_parsesrecline` and processes the decoded elements according to the
           record type.

           Args:
             fh (file handle or compatible): Source of S-Record lines.
             overwrite_metadata (bool): If True existing metadata will be overwritten.
             overwrite_data (bool): If True existing data will be overwritten.
             raise_error_on_miscount (bool): If True a DecodeError is raised if the number of records read differs from
                                             stored number of records.

           Returns:
             self

           Raises:
             DecodeError: If decoded record type is outside of range 0..9.
             DecodeError: If raise_error_on_miscount is True and number of records read differ from stored number of
                          records.
        """
        line = fh.readline()
        numdatarecords = 0
        while line != '':
            (recordtype, address, data, datasize, crccorrect) = self.__class__._parsesrecline(line)
            if 1 <= recordtype <= 3:
                self.set(address, data, datasize, overwrite=overwrite_data)
                if numdatarecords == 0:
                    if overwrite_metadata or self._bytesperline is None:
                        self.bytesperline = datasize
                    if overwrite_metadata or self._addresslength is None:
                        self.addresslength = recordtype + 1
                numdatarecords += 1
            elif recordtype == 0:
                if overwrite_metadata or self._header is None:
                    self.header = data
            elif recordtype == 5 or recordtype == 6:
                if overwrite_metadata or self._write_number_of_records is None:
                    self.write_number_of_records = True
                if raise_error_on_miscount and numdatarecords != address:
                    raise DecodeError(
                        "Number of records read ({:d}) differs from stored number of records ({:d}).".format(
                            numdatarecords, address))
            elif 7 <= recordtype <= 9:
                if overwrite_metadata or self._startaddress is None:
                    self.startaddress = address
            else:
                raise DecodeError("Unsupported record type " + str(recordtype))
            line = fh.readline()
        if self._write_number_of_records is None:
            self.write_number_of_records = False
        return self
