
class IntelHex(MultiPartBuffer):
    def tofile(self, fh, format='hex'):
        import intelhex
        ih = intelhex.IntelHex()
        for start,buffer in self._parts:
            ih.fromdict(dict([ (start+n), byte ] for n,byte in enumerate1(buffer) ))
        ih.tofile(fh, format)
        
class SRecord(object):
    _addresslength = (2,2,3,4,None,2,None,4,3,2)
        
    @classmethod
    def _parseline(cls, line):
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
        adresse = hexstr2int(line[4:4+2*al])      
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
            (recordtype, bytecount, adresse, data, datasize, crccorrect) = cls._parseline(line)
            if recordtype >= 1 and recordtype <= 3:
                self.add(adresse, data, datasize)
            line = frep.readline()
