import sys
from intelhex import IntelHex
from difflib import context_diff

ih = IntelHex.fromhexfile("test2.hex")

ih.fill(0x1F000, 0x2000)
ih._addrwidth = 16
ih.tohexfile("test2out.hex")


sys.stdout.writelines( context_diff(open("test2.hex", "r").readlines(), open("test2out.hex", "r").readlines(), fromfile='before.py', tofile='after.py') )

ih2 = IntelHex.frombinfile("test.zip")

ih2.tohexfile("testzip.hex")
ih2._addrwidth = 16
ih2.tohexfile("testzip2.hex")

IntelHex.fromhexfile("testzip.hex").tobinfile("testout.zip")
IntelHex.fromhexfile("testzip2.hex").tobinfile("testout2.zip")
