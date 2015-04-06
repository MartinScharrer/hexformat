from multipartbuffer import MultiPartBuffer

class SRecord(MultiPartBuffer):
    _addresslength = (2,2,3,4,None,2,None,4,3,2)

    @classmethod
    def _parsesrecline(cls, line):
        try:
            line = line.rstrip("\r\n")
            startcode = line[0]
            if startcode != "S":
                raise ValueError
            recordtype = int(line[1])
            bytes = bytearray.fromhex(line[2:])
        except:
            raise ValueError
        bytecount = bytes[0]
        if bytecount != len(bytes)-1:
            raise ValueError
        crccorrect = ( (sum(bytes) & 0xFF) == 0xFF)
        al = cls._addresslength[recordtype]
        adresse = int(line[4:4+2*al], 16)
        datasize = bytecount - al - 1
        data = bytes[1+al:-1]
        return (recordtype, adresse, data, datasize, crccorrect)

    @classmethod
    def fromfile(cls, frep, format='auto'):
        format = format.lower()
        if format == 'srec':
            return cls.fromsrecfile(frep)
        elif format == 'bin':
            return cls.frombinfile(frep)

    @classmethod
    def fromsrecfile(cls, frep):
        self = cls()
        if not hasattr(frep, "readline"):
            frep = open(frep, "r")

        line = frep.readline()
        while line != '':
            (recordtype, adresse, data, datasize, crccorrect) = cls._parsesrecline(line)
            if recordtype >= 1 and recordtype <= 3:
                self.set(adresse, data, datasize)
            line = frep.readline()

        return self
