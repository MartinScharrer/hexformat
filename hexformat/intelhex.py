""" Provide class to handle IntelHex content.

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

  Attributes:
    RT_DATA (int constant=0): Intel-Hex record type number for data record.
    RT_END_OF_FILE (int constant=1): Intel-Hex record type number for end of file record.
    RT_EXTENDED_SEGMENT_ADDRESS (int constant=2): Intel-Hex record type number for extend segment address record.
    RT_START_SEGMENT_ADDRESS (int constant=3): Intel-Hex record type number for start segment address record.
    RT_EXTENDED_LINEAR_ADDRESS (int constant=4): Intel-Hex record type number for extended linear address record.
    RT_START_LINEAR_ADDRESS (int constant=5): Intel-Hex record type number for start linear address record.

"""

from hexformat.base import DecodeError, EncodeError, HexFormat

# Intel-Hex Record Types
RT_DATA = 0
RT_END_OF_FILE = 1
RT_EXTENDED_SEGMENT_ADDRESS = 2
RT_START_SEGMENT_ADDRESS = 3
RT_EXTENDED_LINEAR_ADDRESS = 4
RT_START_LINEAR_ADDRESS = 5


class IntelHex(HexFormat):
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
    _VARIANTS = {'I08HEX': 8, 'I8HEX': 8, 'I16HEX': 16, 'I32HEX': 32, 8: 8, 16: 16, 32: 32}
    _DEFAULT_BYTESPERLINE = 16
    _DEFAULT_VARIANT = 32
    _DEFAULT_EIP = None
    _DEFAULT_CS_IP = None
    _SETTINGS = ['bytesperline', 'cs_ip', 'eip', 'variant']
    _STANDARD_FORMAT = 'ihex'

    def __init__(self, **settings):
        super(IntelHex, self).__init__()
        self._bytesperline = None
        self._cs_ip = None
        self._eip = None
        self._variant = None
        self.settings(**settings)

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
            if bytesperline < 1 or bytesperline > 255:
                raise ValueError("bytesperline must be between 1 and 255")
        return bytesperline

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, variant):
        self._variant = self._parse_variant(variant)

    def _parse_variant(self, variant):
        if variant is not None:
            if variant in self._VARIANTS:
                variant = self._VARIANTS[variant]
            else:
                raise ValueError("variant must be one of " + ", ".join((str(k) for k in self._VARIANTS.keys())))
        return variant

    @property
    def cs_ip(self):
        return self._cs_ip

    @cs_ip.setter
    def cs_ip(self, cs_ip):
        self._cs_ip = self._parse_cs_ip(cs_ip)

    @staticmethod
    def _parse_cs_ip(cs_ip):
        if cs_ip is not None:
            cs_ip = int(cs_ip)
            if cs_ip < 0 or cs_ip > 0xFFFFFFFF:
                raise ValueError("cs_ip value must not be larger than 32 bit.")
        return cs_ip

    @property
    def eip(self):
        return self._eip

    @eip.setter
    def eip(self, eip):
        self._eip = self._parse_eip(eip)

    @staticmethod
    def _parse_eip(eip):
        if eip is not None:
            eip = int(eip)
            if eip < 0 or eip > 0xFFFFFFFF:
                raise ValueError("eip value must not be larger than 32 bit.")
        return eip

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
            databytes = bytearray.fromhex(line[1:])
        except:
            raise ValueError
        bytecount = databytes[0]
        if bytecount != len(databytes) - 5:
            raise DecodeError("Data length does not match byte count.")
        checksumcorrect = ((sum(databytes) & 0xFF) == 0x00)
        address = (databytes[1] << 8) | databytes[2]
        recordtype = databytes[3]
        try:
            supposed_datalength = self._DATALENGTH[recordtype]
        except IndexError:
            raise DecodeError("Unsupported record type.")
        if supposed_datalength is not None and supposed_datalength != bytecount:
            raise DecodeError("Data length does not correspond to record type.")
        data = databytes[4:-1]
        return recordtype, address, data, bytecount, checksumcorrect

    def _encodeihexline(self, recordtype, address16bit, data):
        """Encode given data to Intel-Hex format.

           One or more Intel-Hex lines are encoded from the given address and buffer and written to the given
           file handle.

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
        # linelen = 2 * len(data) + 11
        linetempl = ":{:02X}{:04X}{:02X}{:s}{:02X}\n"
        bytecount = len(data)
        try:
            recordtype = int(recordtype)
            if recordtype < 0:
                raise IndexError
            supposed_datalength = self._DATALENGTH[recordtype]
        except (TypeError, IndexError):
            raise EncodeError("Unsupported record type.")
        if supposed_datalength is not None and supposed_datalength != bytecount:
            raise EncodeError("Data length does not correspond to record type.")
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
             filename (str): input filename
             ignore_checksum_errors (bool): If True no error is raised on checksum failures

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
        segmaddr = None
        line = fh.readline()
        while line != '':
            (recordtype, lowaddress, data, datasize, checksumcorrect) = self._parseihexline(line)
            if not checksumcorrect and not ignore_checksum_errors:
                raise DecodeError("Checksum mismatch.")
            if recordtype == 0:
                if highaddr is not None:
                    self.set((highaddr + lowaddress), data, datasize)
                else:
                    if (lowaddress + datasize) <= 0x10000:
                        self.set((segmaddr + lowaddress), data, datasize)
                    else:  # wrap on segment boundary:
                        fit = 0x10000 - lowaddress
                        self.set((segmaddr + lowaddress), data, fit)
                        self.set(segmaddr, data[fit:])

                if self._bytesperline is None:
                    self._bytesperline = datasize
            elif recordtype == 1:
                # End of file
                return self
            elif recordtype == 2:
                segmaddr = (data[0] << 12) | (data[1] << 4)
                highaddr = None
                if self._variant is None:
                    self._variant = 16
            elif recordtype == 3:
                self._cs_ip = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
                if self._variant is None:
                    self._variant = 16
            elif recordtype == 4:
                highaddr = (data[0] << 24) | (data[1] << 16)
                segmaddr = None
                if self._variant is None:
                    self._variant = 32
            elif recordtype == 5:
                self._eip = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
                if self._variant is None:
                    self._variant = 32
            else:
                raise DecodeError("Unsupported record type.")
            line = fh.readline()
        return self

    # noinspection PyIncorrectDocstring
    def toihexfile(self, filename, **settings):
        """Writes content as Intel-Hex file to given file name.

           Opens filename for writing and calls :meth:`toihexfh` with the file handle and all arguments.
           See :meth:`toihexfh` for description of the arguments.

           Args:
             filename (str): Input file name.
             bytesperline (int): Number of bytes per line.
             variant ('I08HEX', 'I8HEX', 'I16HEX', 'I32HEX', 8, 16, 32): Variant of Intel-Hex format.
             cs_ip (int, 32-bit): Value of CS:IP starting address used for I16HEX variant.
             eip (int, 32-bit): Value of EIP starting address used for I32HEX variant.

           Returns:
             self
        """
        with open(filename, "w") as fh:
            return self.toihexfh(fh, **settings)

    # noinspection PyIncorrectDocstring
    def toihexfh(self, fh, **settings):
        """Writes content as Intel-Hex file to given file handle.

           Args:
             fh (file handle or compatible): Destination of S-Record lines.
             bytesperline (int): Number of bytes per line.
             variant ('I08HEX', 'I8HEX', 'I16HEX', 'I32HEX', 8, 16, 32): Variant of Intel-Hex format.
             cs_ip (int, 32-bit): Value of CS:IP starting address used for I16HEX variant.
             eip (int, 32-bit): Value of EIP starting address used for I32HEX variant.

           Returns:
             self

           Raises:
             EncodeError: if selected address length is not wide enough to fit all addresses.
        """
        (bytesperline, cs_ip, eip, variant) = self._parse_settings(**settings)
        highaddr = 0
        addresshigh = 0
        for address, buffer in self._parts:
            pos = 0
            datalength = len(buffer)
            while pos < datalength:
                if variant == 32:
                    if address > 0xFFFFFFFF:
                        raise EncodeError("Address to large for format.")
                    addresslow = address & 0x0000FFFF
                    addresshigh = address & 0xFFFF0000
                elif variant == 16:
                    if address > 0xFFFFF:
                        raise EncodeError("Address to large for format.")
                    if address > (addresshigh + 0x0FFFF):
                        addresshigh = address & 0xFFF00
                    addresslow = address - addresshigh
                else:
                    if address > 0xFFFF:
                        raise EncodeError("Address to large for format.")
                    addresslow = address
                if addresshigh != highaddr:
                    highaddr = addresshigh
                    if variant == 32:
                        fh.write(self._encodeihexline(4, 0, [addresshigh >> 24, (addresshigh >> 16) & 0xFF]))
                    else:
                        fh.write(self._encodeihexline(2, 0, [addresshigh >> 12, (addresshigh >> 4) & 0xFF]))
                endpos = min(pos + bytesperline, datalength)
                fh.write(self._encodeihexline(0, addresslow, buffer[pos:endpos]))
                address += bytesperline
                pos = endpos
        if variant == 32 and eip is not None:
            fh.write(self._encodeihexline(5, 0, [eip >> 24, (eip >> 16) & 0xFF, (eip >> 8) & 0xFF, eip & 0xFF]))
        elif variant == 16 and cs_ip is not None:
            fh.write(self._encodeihexline(3, 0, [cs_ip >> 24, (cs_ip >> 16) & 0xFF, (cs_ip >> 8) & 0xFF, cs_ip & 0xFF]))
        fh.write(self._encodeihexline(1, 0, bytearray()))
        return self

    # noinspection PyProtectedMember
    def __eq__(self, other):
        """Compare with other instance for equality.

           Both instances are equal if both _parts lists, _eip and _cs_ip are identical.
        """
        return super(IntelHex, self).__eq__(other) and self._eip == other._eip and self._cs_ip == other._cs_ip
