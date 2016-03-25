""" Provide classes for popular hex formats as well as auxiliary classes to generate fill patterns.

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


class HexformatError(Exception):
    """General hexformat exception. Base class for all other exceptions of this module."""
    pass


class DecodeError(HexformatError):
    """Exception is raised if errors during the decoding of a hex file occur."""
    pass


class EncodeError(HexformatError):
    """Exception is raised if errors during the encoding of a hex file occur."""
    pass
