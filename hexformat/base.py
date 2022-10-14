""" Provide base class for hexformat classes.

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
import copy

from hexformat.multipartbuffer import MultiPartBuffer


class HexformatError(Exception):
    """General hexformat exception. Base class for all other exceptions of this module."""
    pass


class DecodeError(HexformatError):
    """Exception is raised if errors during the decoding of a hex file occur."""
    pass


class EncodeError(HexformatError):
    """Exception is raised if errors during the encoding of a hex file occur."""
    pass


class HexFormat(MultiPartBuffer):
    _SETTINGS = tuple()

    def __init__(self):
        super(HexFormat, self).__init__()

    @classmethod
    def fromother(cls, other, shallow_copy=False):
        self = cls()
        if isinstance(other, MultiPartBuffer):
            if shallow_copy:
                self._parts = other._parts
            else:
                self._parts = copy.deepcopy(other._parts)
        else:
            raise TypeError
        return self

    def settings(self, **settings):
        for name, value in settings.items():
            if name in self._SETTINGS:
                setattr(self, name, value)
            else:
                raise AttributeError("Unknown setting {:s}".format(name))
        return self

    def _parse_settings(self, **settings):
        retvals = list()
        for sname in self._SETTINGS:
            value = None
            if sname in settings:
                value = getattr(self, '_parse_' + sname)(settings[sname])
            if value is None:
                value = getattr(self, sname)
            if value is None:
                value = getattr(self, '_DEFAULT_' + sname.upper())
            retvals.append(value)
        return retvals
