# SAP2


![SAP2 Instructions](/images/SAP2-instructions.jpeg)

Instructions

Register instructions 4 registers (plus alternative reg bank) R0, R1, R2 and R3

Opcode | Comment|Flags
-------| -------|------
MOV Rx,Ry|Copy Ry into Rx| None
ADD Rx,Ry|Rx + Ry -> Rx|C Z V S
SUB Rx,Ry|Rx - Ry -> Rx|C Z V S
AND Rx,Ry|Rx & Ry -> Rx|Z
OR Rx,Ry|Rx or Rx-> R|Z S V
XOR Rx,Ry| Rx ^ Ry -> Rx| Z S V

Opcode|Action|Flags
------|------|-----
ADDI Rx,8bit| Rx + 8bit -> Rx|Z S V O
SUBI Rx,8bit| Rx - 8bit -> Rx|Z S V O
ANDI Rx,8bit| Rx - 8bit -> Rx|Z S V O
ORI Rx,8bit| Rx or 8bit -> Rx|Z S V O
XORI Rx,8bit| Rx ^ 8bit -> Rx|Z S V O

Opcode|Action|Flags
------|------|-----
MOVI Rx,8bit | 8-bit value -> Rx| None
LD Rx,16bitaddr |@(addr) -> Rx |None
ST Rx,16bitaddr |@(addr) <- Rx |None
MOVI SP,16bitaddr| 16-bit value -> SP| None

Opcode|Action|Flags
------|------|-----
DJNZ Rx,16bitaddr | Rx - 1 -> Rx, 16bitaddr if NZ ? PC + 1 -> PC| Z S V O
JPNZ 16bitaddr | PC <- PC + 1 if Z ? 16bitaddr| Z S V O
JPNC 16bitaddr | PC <- PC + 1 if C ? 16bitaddr| Z S V O
JMP  16bitaddr | PC <- 16bitaddr | None
CALL 16bitaddr | @SP <- PC + 1, PC <- 16bitaddr| Z S V O
 

24 August 2021
---

Added 'assembler.py' to allow us to produce LogiSim hex files for loading into RAM.

see 'test.asm' for example of our current set of Instructions

To assemble code - simple run './assembler.py test.asm' - this will produce a 'binary' version with the same
base name - but appended with '.hex' (i.e 'assembler.py mycode.asm' produces 'mycode.hex')
