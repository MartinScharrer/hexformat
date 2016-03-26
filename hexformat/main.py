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
