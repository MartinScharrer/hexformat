from srecord import SplitFile, Buffer, RandomContent, IntelHex
import sys

def test(num, str1, str2):
    str1 = str(str1)
    str2 = str(str2)
    if str1 != str2:
        print "%s: Failure: %s != %s" % (str(num), str1, str2)
    else:
        print "%s: OK: %s" % (str(num), str1)
 
teststr = "01234567"
teststr1 = "abc"

s = SplitFile()
s.set(0, teststr)
test ( 1, s._parts[0][1], teststr )

s = SplitFile()
s.set(0, teststr)
s.set(0, teststr1)
test ( 2, s._parts[0][1], teststr1 + teststr[len(teststr1):] )

s = SplitFile()
s.set(0, teststr)
s.set(1, teststr1)
test ( 3, s._parts[0][1], teststr[0] + teststr1 + teststr[len(teststr1)+1:] )

s = SplitFile()
s.set(0, teststr)
s.set(0, teststr1)
test ( 4, s._parts[0][1], teststr1 + teststr[len(teststr1):] )

r = RandomContent()
ih = IntelHex()
