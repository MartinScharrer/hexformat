import random

    
class RandomContent(object):
    def __init__(self, length=1):
        self._length = int(length)
        
    def __len__(self):
        return self._length
        
    def __mul__(self, m):
        return self.__class__( self._length * int(m) )
        
    def __imul__(self, m):
        self._length *= int(m)
       
    def __iter__(self):
        return self._produce( 1 )

    def __str__(self):
        return str(Buffer(self._produce( 1 )))
        
    def __getslice__(self, i, j):
        return self.__class__( j - i )

    def __getitem__(self, i):
        return random.randint(0, 255)
        
    def _produce(self, length):
        length = int(length) * self._length
        n = 0
        while n < length:
            n += 1
            yield random.randint(0, 255)
            
  