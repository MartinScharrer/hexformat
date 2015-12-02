""" Provide class for HexDump content.

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

from hexformat.multipartbuffer import MultiPartBuffer, Buffer
import string

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
        