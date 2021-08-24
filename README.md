# SAP2


![SAP2 Instructions](/images/SAP2-instructions.jpeg)

Instructions

Register instructions 4 registers (plus alternative reg bank) R0, R1, R2 and R3

Opcode | Comment|Flags
-------| -------|------
MOV Rx,Ry|Copy Ry into Rx| None
ADD Rx,Ry|Rx + Ry copied into Rx|C Z V S
SUB Rx,Ry|Rx - Ry -> Rx|C Z V S
AND Rx,Ry|Rx & Ry -> Rx|Z
OR Rx,Ry|Rx ^ Rx-> R|Z
XOR Rx,Ry| Rx ^ Ry -> Rx| Z S V

Opcode|Action|Flags
------|------|-----
MOVI Rx,8bit | 8-bit value -> Rx| None
LD Rx,16bitaddr |contents @addr -> Rx |yyy




24 August 2021
---

Added 'assembler.py' to allow us to produce LogiSim hex files for loading into RAM.

see 'test.asm' for example of our current set of Instructions

To assemble code - simple run './assembler.py test.asm' - this will produce a 'binary' version with the same
base name - but appended with '.hex' (i.e 'assembler.py mycode.asm' produces 'mycode.hex')
