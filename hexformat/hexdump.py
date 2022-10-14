""" Provide class for HexDump content.

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

import string

from . import DecodeError
from .base import HexFormat


class HexDump(HexFormat):
    """`Hex dump`_ representation class.

       The HexDump class is able to generate and parse hex dumps of binary data.

       .. _`Hex dump`: http://en.wikipedia.org/wiki/Hex_dump
    """

    @staticmethod
    def _encodehexdumpline(address, data, bytesperline, groupsize, bigendian, ascii):
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
        for n, byte in enumerate(data, 1):
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
            asciistr = " |{{:{:d}s}}|".format(bytesperline).format(
                "".join([char in string.printable and char or "." for char in str(data)]))
        numgroups = int(bytesperline / groupsize)
        hwidth = bytesperline * 2 + numgroups - 1
        return "{{:08X}}: {{:{:d}s}}{{:s}}\n".format(hwidth).format(address, datastr, asciistr)

    @staticmethod
    def _parsehexdumpline(line, bigendian):
        """Parses hex dump line to extract address and data.

           Args:
             line (str): Hex dump line to be parsed.
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style,
                               MSB first) order, otherwise in little endian (Intel style, LSB first) order.

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
            groups = line[cidx + 1:aidx].split()
            data = bytearray()
            for group in groups:
                groupdata = bytearray.fromhex(group)
                if not bigendian:
                    groupdata = reversed(groupdata)
                data.extend(groupdata)
            return address, data
        except Exception as e:
            raise DecodeError("Invalid formatted input line: " + str(e))

    @classmethod
    def fromhexdumpfile(cls, filename, bigendian=True):
        """Generates HexDump instance from hex dump file.

           Opens filename for reading and calls :meth:`fromhexdumpfh` with the file handle.

           Args:
             filename (str): Name of file to be loaded.
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style,
                               MSB first) order, otherwise in little endian (Intel style, LSB first) order.

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
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style,
                               MSB first) order, otherwise in little endian (Intel style, LSB first) order.

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
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style,
                               MSB first) order, otherwise in little endian (Intel style, LSB first) order.

           Returns:
             self
        """
        with open(filename, "r") as fh:
            return self.loadhexdumpfh(fh, bigendian)

    def loadhexdumpfh(self, fh, bigendian=True):
        """Loads hex dump lines from file handle.

           Args:
             fh (file handle or compatible): Source of Intel-Hex lines.
             bigendian (bool): If True the bytes in a group will be interpreted in big endian (Motorola style,
                               MSB first) order, otherwise in little endian (Intel style, LSB first) order.

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
            bytesperline = int(round(float(bytesperline) / groupsize)) * groupsize
        for address, buffer in self._parts:
            pos = 0
            datalength = len(buffer)
            while pos < datalength:
                endpos = min(pos + bytesperline, datalength)
                fh.write(
                    self._encodehexdumpline(address, buffer[pos:endpos], bytesperline, groupsize, bigendian, ascii))
                address += bytesperline
                pos = endpos
        return self
