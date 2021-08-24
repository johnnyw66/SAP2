# SAP2


![SAP2 Instructions](/images/SAP2-instructions.jpeg)

Instructions

*Register instructions 2 Banks of 4 registers R0, R1, R2 and R3*


Opcode | Comment|Flags
-------| -------|------
MOV Rx,Ry|Copy Ry into Rx| None
ADD Rx,Ry|Rx + Ry -> Rx|C Z V S
SUB Rx,Ry|Rx - Ry -> Rx|C Z V S
AND Rx,Ry|Rx & Ry -> Rx|Z
OR Rx,Ry|Rx or Rx-> R|Z S V
XOR Rx,Ry| Rx ^ Ry -> Rx| Z S V

*24 Opcodes in total*

Opcode|Action|Flags
------|------|-----
ADDI Rx,8bit| Rx + 8bit -> Rx|Z S V O
SUBI Rx,8bit| Rx - 8bit -> Rx|Z S V O
ANDI Rx,8bit| Rx - 8bit -> Rx|Z S V O
ORI Rx,8bit| Rx or 8bit -> Rx|Z S V O
XORI Rx,8bit| Rx ^ 8bit -> Rx|Z S V O
*20 Opcodes in total*

Opcode|Action|Flags
------|------|-----
MOVI Rx,8bit | 8-bit value -> Rx| None
LD Rx,16bitaddr |@(addr) -> Rx |None
ST Rx,16bitaddr |@(addr) <- Rx |None
MOVI SP,16bitaddr| 16-bit value -> SP| None
*4 Opcodes in total*

Opcode|Action|Flags|Tstates
------|------|-----|-------
DJNZ Rx,16bitaddr | Rx - 1 -> Rx, 16bitaddr if NZ ? PC + 1 -> PC| Z S V O|0
JPNZ 16bitaddr | PC <- PC + 1 if Z ? 16bitaddr| None|0
JPNC 16bitaddr | PC <- PC + 1 if C ? 16bitaddr| None|0
JMP  16bitaddr | PC <- 16bitaddr | None|0
CALL 16bitaddr | @SP <- PC + 1, PC <- 16bitaddr, SP <- SP - 2| None|0
RET| PC <- @SP| None|0
*9 Opcodes in total*

Opcode|Action|Flags|Tstates
------|------|-----|-------
PUSH R0| R0 -> @SP, R1-> @SP+1 SP <- SP - 2|None|0
PUSH R2| R2 -> @SP, R3-> @SP+1 SP <- SP - 2| None|0
POP R0 | @SP -> R1, @SP+1 -> R0, SP <- SP + 2| None|0
POP R2 | @SP -> R3, @SP+1 -> R2, SP <- SP + 2|None|0


Opcode|Action|Flags|Tstates
------|------|-----|-------
CLC| Cf<-0| C |0|
SETC|Cf<-1| C|0
NOP| no operation| None|0
EXX| Switch Reg Bank| None|0
*5 Ocodes in total*


24 August 2021
---

Added 'assembler.py' to allow us to produce LogiSim hex files for loading into RAM.

see 'test.asm' for example of our current set of Instructions

To assemble code - simple run './assembler.py test.asm' - this will produce a 'binary' version with the same
base name - but appended with '.hex' (i.e 'assembler.py mycode.asm' produces 'mycode.hex')
