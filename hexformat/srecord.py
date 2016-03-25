""" Provide classto handle Motorola SRecord content.

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

"""

import binascii

from hexformat.main import HexFormat
from hexformat.multipartbuffer import Buffer


class SRecord(HexFormat):
    """Motorola `S-Record`_ hex file representation class.

       The SRecord class is able to parse and generate binary data in the S-Record representation.

       Attributes:
         _SRECORD_ADDRESSLENGTH (tuple): Address length in bytes for each record type.
         _STANDARD_FORMAT (str): The standard format used by :meth:`.fromfh` and :meth:`.fromfile` if no format was given.
         _startaddress (int): Starting execution location. This tells the programmer which address contains the start routine. Default: 0.
         _header (data buffer or None): Header data written using record type 0 if not None. The content is application specific.

       .. _`S-Record`: http://en.wikipedia.org/wiki/SREC_%28file_format%29
    """

    _SRECORD_ADDRESSLENGTH = (2, 2, 3, 4, None, 2, 3, 4, 3, 2)
    _STANDARD_FORMAT = 'srec'
    _STANDARD_HEADER = Buffer(b'')
    _STANDARD_STARTADDRESS = 0
    _STANDARD_ADDRESSLENGTH = None
    _STANDARD_BYTESPERLINE = 32
    _STANDARD_WRITE_NUMBER_OF_RECORDS = False
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
                raise ValueError("bytesperline must be between 0 and 253")
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
            header = Buffer(header)
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

    def tosrecfile(cls, filename, **settings):
        """Writes content as S-Record file to given file name.

           Opens filename for writing and calls :meth:`tosrecfh` with the file handle and all arguments.
           See :meth:`tosecfh` for description of the arguments.

           Returns:
             self
        """
        with open(filename, "w") as fh:
            return cls.tosrecfh(fh, **settings)

    def tosrecfh(self, fh, **settings):
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
        (startaddress, addresslength, bytesperline, header, write_number_of_records) = self._parse_settings(**settings)

        if addresslength is None:
            start, size = self.range()
            endaddress = start + size - 1
            addresslength = self._minaddresslength(endaddress)

        recordtype = addresslength - 1
        recordtype_end = 10 - recordtype
        numdatarecords = 0

        self._encodesrecline(fh, 0, header, recordtype=0, bytesperline=len(header))
        for address, buffer in self._parts:
            numdatarecords += self._encodesrecline(fh, address, buffer, recordtype=recordtype,
                                                   bytesperline=bytesperline)
        if write_number_of_records:
            if numdatarecords <= 0xFFFF:
                self._encodesrecline(fh, numdatarecords, Buffer(), recordtype=5, bytesperline=253)
            elif numdatarecords <= 0xFFFFFF:
                self._encodesrecline(fh, numdatarecords, Buffer(), recordtype=6, bytesperline=253)

        self._encodesrecline(fh, startaddress, Buffer(), recordtype=recordtype_end, bytesperline=253)
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
            return (((address >> 8) & 0xFF), (address & 0xFF))
        elif addresslength == 3:
            return (((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF))
        elif addresslength == 4:
            return (((address >> 24) & 0xFF), ((address >> 16) & 0xFF), ((address >> 8) & 0xFF), (address & 0xFF))
        else:
            raise ValueError("Invalid address length (%s). Valid values are 2, 3 or 4." % (str(addresslength),))

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
        endaddress = address + len(buffer) - 1
        if recordtype == 123:
            recordtype = cls._minaddresslength(endaddress) - 1
        try:
            recordtype = int(recordtype)
            addresslength = int(cls._SRECORD_ADDRESSLENGTH[recordtype])
        except (IndexError, TypeError):
            raise EncodeError("Unsupported record type.")

        bytesperline = max(1, min(bytesperline, 254 - addresslength))
        bytecount = bytesperline + addresslength + 1
        numdatarecords = 0
        while address < endaddress or numdatarecords == 0:
            numdatarecords += 1
            if address + bytesperline > endaddress:
                bytesperline = endaddress - address + 1
                bytecount = bytesperline + addresslength + 1
            linebuffer = bytearray([0, ] * (bytecount + 1))
            linebuffer[0] = bytecount
            linebuffer[1:addresslength + 1] = cls._s123addr(addresslength, address)
            linebuffer[addresslength + 1:bytecount] = buffer[offset:offset + bytesperline]
            linebuffer[bytecount] = ((~sum(linebuffer)) & 0xFF)
            line = "".join(["S", str(recordtype), binascii.hexlify(linebuffer).upper().decode(), "\n"])
            fh.write(line)
            offset += bytesperline
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
            bytes = bytearray.fromhex(line[2:])
        except:
            raise DecodeError("misformatted S-Record line.")
        bytecount = bytes[0]
        if bytecount != len(bytes) - 1:
            raise DecodeError("Byte count does not match line data.")
        crccorrect = ((sum(bytes) & 0xFF) == 0xFF)
        al = cls._SRECORD_ADDRESSLENGTH[recordtype]
        address = int(line[4:4 + 2 * al], 16)
        datasize = bytecount - al - 1
        data = bytes[1 + al:-1]
        return (recordtype, address, data, datasize, crccorrect)

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

    def loadsrecfile(self, filename, overwrite_metadata=False, overwrite_data=True, raise_error_on_miscount=True):
        """Loads S-Record lines from named file.

           Creates new instance and calls :meth:`loadsrecfh` on it.

           Args:
             filename (str): Name of S-Record file.
             raise_error_on_miscount (bool): If True a DecodeError is raised if the number of records read differs from stored number of records.

           Returns:
             self
        """
        with open(filename, "r") as fh:
            return self.loadsrecfh(fh, overwrite_metadata, overwrite_data, raise_error_on_miscount)

    def loadsrecfh(self, fh, overwrite_metadata=False, overwrite_data=True, raise_error_on_miscount=True):
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
            (recordtype, address, data, datasize, crccorrect) = self.__class__._parsesrecline(line)
            if recordtype >= 1 and recordtype <= 3:
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
            elif recordtype >= 7 and recordtype <= 9:
                if overwrite_metadata or self._startaddress is None:
                    self.startaddress = address
            else:
                raise DecodeError("Unsupported record type " + str(recordtype))
            line = fh.readline()
        if self._write_number_of_records is None:
            self.write_number_of_records = False
        return self
