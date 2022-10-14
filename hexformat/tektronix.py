""" Provide class to handle Tektronix Extended Hex content.

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

from hexformat.base import HexFormat, DecodeError

TYPE_SYMBOL = 3
TYPE_DATA = 6
TYPE_TERMINATOR = 8


class TektronixExtHex(HexFormat):
    """Tektronix Extended Hex file representation class.

       The TektronixExtHex class is able to parse and generate binary data in the Tektronix Extended Hex representation.

       Attributes:

    """

    _STANDARD_FORMAT = 'tek'
    _STANDARD_STARTADDRESS = 0
    _STANDARD_ADDRESSLENGTH = None
    _STANDARD_BYTESPERLINE = 32
    _SETTINGS = ['startaddress', 'bytesperline', 'addresslength']

    def __init__(self, **settings):
        super(TektronixExtHex, self).__init__()
        self._startaddress = None
        self._bytesperline = None
        self._addresslength = None
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
    def bytesperline(self):
        return self._bytesperline

    @bytesperline.setter
    def bytesperline(self, bytesperline):
        self._bytesperline = self._parse_bytesperline(bytesperline)

    @staticmethod
    def _parse_bytesperline(bytesperline):
        if bytesperline is not None:
            bytesperline = int(bytesperline)
            if bytesperline < 1 or bytesperline > 124:
                raise ValueError("bytesperline must be between 0 and 124")
        return bytesperline

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

    def totekfile(self, filename, **settings):
        """Writes content as Tektronix Extended Hex file to given file name.

           Opens filename for writing and calls :meth:`totekfh` with the file handle and all arguments.
           See :meth:`totekfh` for description of the arguments.

           Returns:
             self
        """
        with open(filename, "w") as fh:
            return self.totekfh(fh, **settings)

    def totekfh(self, fh, **settings):
        """Writes content as Tektronix Extended Hex file to given file handle.

           Args:
             fh (file handle or compatible): Destination of Tektronix Extended Hex lines.
             settings: 

           Returns:
             self
        """
        (startaddress, bytesperline, addresslength) = self._parse_settings(**settings)

        if addresslength is None:
            start, size = self.range()
            endaddress = start + size - 1
            addresslength = len("{:X}".format(endaddress))

        for address, buffer in self._parts:
            self._encodetekline(fh, address, addresslength, buffer, 0, TYPE_DATA, bytesperline)

        self._encodetekline(fh, startaddress, addresslength, bytearray(), recordtype=TYPE_TERMINATOR, bytesperline=0)
        return self

    @classmethod
    def _encodetekline(cls, fh, address, addresslength, buffer, offset=0, recordtype=TYPE_DATA, bytesperline=32):
        """Encode given data to a Tektronix Extended Hex line.

           One or more Tektronix Extended Hex lines are encoded from the given address and buffer and written to the
           given file handle.

           Args:
             fh (file handle or compatible): Destination of Tektronix Extended Hex lines.
             address (int): Address of first byte in buffer data.
             buffer (Buffer): Buffer with data to be encoded.
             offset (int): Reading start index of buffer.
             recordtype (int: 0..9 or 123): Tektronix Extended Hex record type. If equal to 123 the a
                                            record type 1, 2 or 3 is determined by the minimum address byte width.
             bytesperline (int): Number of bytes to be written on a single line.

           Raises:
             EncodeError: on unsupported record type.
        """
        endaddress = address + len(buffer) - 1
        bytesperline = max(1, min(bytesperline, ((255 - 6 - addresslength) // 2)))
        length = 2 * bytesperline + addresslength + 6
        numdatarecords = 0
        while address < endaddress or numdatarecords == 0:
            numdatarecords += 1
            if address + bytesperline > endaddress:
                bytesperline = endaddress - address + 1
                length = 2 * bytesperline + addresslength + 6
            checksum = 0
            line = "{0:02X}{1:1X}{2:1X}{3:0{2:d}X}{4:s}".format(
                length, recordtype, addresslength, address,
                binascii.hexlify(buffer[offset:offset + bytesperline]).upper().decode())
            for char in line:
                checksum += int(char, 16)
            line = "%" + line[0:3] + "{:02X}".format(checksum) + line[3:] + "\n"
            fh.write(line)
            offset += bytesperline
            address += bytesperline
        return numdatarecords

    @classmethod
    def _parsetekline(cls, line):
        """Parse Tektronix Extended Hex line and return decoded parts as tuple.

           Args:
             line (str): Single input line, usually with line termination character(s).

           Returns:
             Tuple (recordtype, address, addresslength, data, datasize, checksum, checksumcorrect) with
             types (int, int, int, Buffer, int, int, bool).

           Raises:
             DecodeError: if line does not start with start code ("S").
             DecodeError: on misformatted input line.
             DecodeError: on byte count - line data mismatch.
        """
        try:
            line = line.rstrip("\r\n\t ")
            startcode = line[0]
            if startcode != "%":
                raise DecodeError("No valid Tektronix Extended Hex start code found.")
            length = int(line[1:3], 16)
            recordtype = int(line[3], 16)
            checksum = int(line[4:6], 16)
            addresslength = int(line[6], 16)
            datalength = ((length - addresslength - 6) // 2)
            beginofdata = 7 + addresslength
            address = int(line[7:beginofdata], 16)
            if datalength > 0:
                data = bytearray.fromhex(line[beginofdata:])
            else:
                data = bytearray()
            verifychecksum = 0
            for char in line[1:4] + line[6:length + 1]:
                verifychecksum += int(char, 16)
            checksumcorrect = (verifychecksum == checksum)
        except DecodeError:
            raise
        except:
            raise DecodeError("Misformatted Tektronix Extended Hex line.")
        return recordtype, address, addresslength, data, datalength, checksum, checksumcorrect

    @classmethod
    def fromtekfile(cls, filename):
        """Generates instance from Tektronix Extended Hex file.

           Opens filename for reading and calls :meth:`fromtekfh` with the file handle.

           Args:
             filename (str): Name of Tektronix Extended Hex file.

           Returns:
             New instance of class with loaded data.
        """
        with open(filename, "r") as fh:
            return cls.fromtekfh(fh)

    @classmethod
    def fromtekfh(cls, fh):
        """Generates instance from file handle which must point to Tektronix Extended Hex lines.

           Creates new instance and calls :meth:`loadtekfh` on it.

           Args:
             fh (file handle or compatible): Source of Tektronix Extended Hex lines.

           Returns:
             New instance of class with loaded data.
        """
        self = cls()
        self.loadtekfh(fh)
        return self

    def loadtekfile(self, filename, overwrite_metadata=False, overwrite_data=True, raise_error_on_miscount=True):
        """Loads Tektronix Extended Hex lines from named file.

           Creates new instance and calls :meth:`loadtekfh` on it.

           Args:
             filename (str): Name of Tektronix Extended Hex file.
             overwrite_metadata (bool): If True existing metadata will be overwritten.
             overwrite_data (bool): If True existing data will be overwritten.
             raise_error_on_miscount (bool): If True a DecodeError is raised if the number of records read differs from
                                             stored number of records.

           Returns:
             self
        """
        with open(filename, "r") as fh:
            return self.loadtekfh(fh, overwrite_metadata, overwrite_data, raise_error_on_miscount)

    def loadtekfh(self, fh, overwrite_metadata=False, overwrite_data=True, raise_error_on_miscount=True):
        """Loads data from Tektronix Extended Hex file over file handle.

           Parses every source line using :meth:`_parsetekline` and processes the decoded elements according to the
           record type.

           Args:
             fh (file handle or compatible): Source of Tektronix Extended Hex lines.
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
            (recordtype, address, addresslength, data, datalength, checksum,
             checksumcorrect) = self.__class__._parsetekline(line)
            if recordtype == TYPE_DATA:
                self.set(address, data, datalength, overwrite=overwrite_data)
                if numdatarecords == 0:
                    if overwrite_metadata or self._bytesperline is None:
                        self.bytesperline = datalength
                    if overwrite_metadata or self._addresslength is None:
                        self.addresslength = addresslength
                numdatarecords += 1
            elif recordtype == TYPE_TERMINATOR:
                if overwrite_metadata or self._startaddress is None:
                    self.startaddress = address
            elif recordtype == TYPE_SYMBOL:
                # Symbol type ignored; not supported yet
                pass
            else:
                raise DecodeError("Unsupported record type: {:d}".format(recordtype))
            line = fh.readline()
        return self
