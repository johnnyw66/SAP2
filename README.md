# SAP2


![SAP2 Instructions](/images/SAP2-instructions.jpeg)


24 August 2021
---

Added 'assembler.py' to allow us to produce LogiSim hex files for loading into RAM.

see 'test.asm' for example of our current set of Instructions

To assemble code - simple run './assembler.py test.asm' - this will produce a 'binary' version with the same
base name - but appended with '.hex' (i.e 'assembler.py mycode.asm' produces 'mycode.hex')
