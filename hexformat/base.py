""" Provide base class for hexformat classes.

  License::

    Copyright (C) 2015-2016 by Martin Scharrer <martin@scharrer-online.de>

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
import copy

from hexformat.multipartbuffer import MultiPartBuffer


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
                value = getattr(self, '_STANDARD_' + sname.upper())
            retvals.append(value)
        return retvals
