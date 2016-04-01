About
*****
The **hexformat** Python package allows the processing of several HEX data formats.
Supported formats are the Intel-Hex format, the Motorola S-Record_ format as well as the simple `hex dump`_ format.
The first two are often used for programming microcontrollers while the last is often used to display binary data in a user readable way.

Files in the mentioned format can be created, modified (e.g. set, delete and fill data) and read from or written to files.
A base class :class:`.MultiPartBuffer` is provided which implements the handling of multiple data parts where every part is identified by its corresponding start address.
This base class allows for the basic operations like reading and writing binary files as well as modifing the binary data.
The specific classes :class:`.IntelHex`, :class:`.SRecord` and :class:`.HexDump` are derivated from it which implement the parsing and generating of the corresponding HEX formats as well as implementing file format specific features. 

.. _Intel-Hex: http://en.wikipedia.org/wiki/Intel_HEX
.. _S-Record: http://en.wikipedia.org/wiki/SREC_%28file_format%29
.. _`hex dump`: http://en.wikipedia.org/wiki/Hex_dump

Motivation
~~~~~~~~~~
This package was mainly created to replace the srecord_ command line tool and its complicated interface with a clean python interface for use with handling microcontroller HEX files.
The existing Python library intelhex_ was used for a while, but then the need for the S-Record format appeared.
Also *intelhex.IntelHex* did not provide a suitable interface for the most often used operations.

.. _srecord: http://srecord.sourceforge.net/
.. _intelhex: https://pypi.python.org/pypi/IntelHex


License
~~~~~~~
This work is free software under the GPL v3 or any later version::

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

