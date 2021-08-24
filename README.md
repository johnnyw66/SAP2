# SAP2


![SAP2 Instructions](/images/SAP2-instructions.jpeg)

# Instructions

*User Register instructions 2 Banks of 4 registers R0, R1, R2 and R3 plus PC,SP and Flag Register*



Opcode | Comment|Flags|Tstates
-------| -------|-----|-------
MOV Rx,Ry| Ry -> Rx | None|4
ADD Rx,Ry|Rx + Ry -> Rx|C Z V S|4
SUB Rx,Ry|Rx - Ry -> Rx|C Z V S|4
AND Rx,Ry|Rx & Ry -> Rx|Z|4
OR Rx,Ry|Rx or Rx-> R|Z S V|4
XOR Rx,Ry| Rx ^ Ry -> Rx| Z S V|4
INC Rx | Rx + 1 -> Rx | Z S V O|5
DEC Rx | Rx - 1 -> Rx | Z S V O|5
INC SP | SP + 1 -> SP |None|5
DEC SP | SP - 1 -> SP |None|5
OUT Rx| Rx sent to Display Unit|4
*38 Opcodes in total*

Opcode|Action|Flags|Tstates
------|------|-----|-------
ADDI Rx,8bit| Rx + 8bit -> Rx|Z S V O|8
SUBI Rx,8bit| Rx - 8bit -> Rx|Z S V O|8
ANDI Rx,8bit| Rx - 8bit -> Rx|Z S V O|8
ORI Rx,8bit| Rx or 8bit -> Rx|Z S V O|8
XORI Rx,8bit| Rx ^ 8bit -> Rx|Z S V O|8
*20 Opcodes in total*

Opcode|Action|Flags|Tstates
------|------|-----|-------
MOVI Rx,8bit | 8-bit value -> Rx| None|7
LD Rx,16bitaddr |@(addr) -> Rx |None|0
ST Rx,16bitaddr |@(addr) <- Rx |None|0
MOVI SP,16bitaddr| 16-bit value -> SP| None|0
*4 Opcodes in total*

Opcode|Action|Flags|Tstates
------|------|-----|-------
DJNZ Rx,16bitaddr | Rx - 1 -> Rx, 16bitaddr if NZ ? PC + 1 -> PC| Z S V O|0
JPNZ 16bitaddr | PC <- PC + 1 if Z ? 16bitaddr| None|0
JPNC 16bitaddr | PC <- PC + 1 if C ? 16bitaddr| None|0
JMP  16bitaddr | PC <- 16bitaddr | None|0
CALL 16bitaddr | @SP <- PC + 1, PC <- 16bitaddr, SP <- SP - 2| None|14
RET| PC <- @SP| None|10
*9 Opcodes in total*

Opcode|Action|Flags|Tstates
------|------|-----|-------
PUSH R0| R0 -> @SP, R1-> @SP+1 SP <- SP - 2|None|9
PUSH R2| R2 -> @SP, R3-> @SP+1 SP <- SP - 2| None|9
POP R0 | @SP -> R1, @SP+1 -> R0, SP <- SP + 2| None|9
POP R2 | @SP -> R3, @SP+1 -> R2, SP <- SP + 2|None|9
*4 Ocodes in total*


Opcode|Action|Flags|Tstates
------|------|-----|-------
CLC| Cf <- 0| C |5
SETC|Cf <- 1| C|5
NOP| no operation| None|4
EXX| Switch Reg Bank| None|4
HLT| Stop uProc|None|4
*5 Ocodes in total*

**CLC and SETC are currently 'fudged' as they affect the sign and overflow FLAGS**


24 August 2021
---
This microprocessor written for the LogiSim Evolution CAD can be built with standard TTL/CMOS logic chips.
For what it's worth - I've included the circuit for a programmer unit so the user can enter byte code by hand.
I prefer to use the LogicSim GUI and my simple assembler utility.

Assemble your machine code from a 'asm' text file using the python utility - and load the program into the RAM memory unit (right click and select 'Load Image' - then select an assembled hex file )


To assemble code - simple run './assembler.py test.asm' - this will produce a 'binary' version with the same
base name - but appended with '.hex' (i.e 'assembler.py mycode.asm' produces 'mycode.hex')

Example code:


````
.org 0
:start
    movwi sp,0xffff   ; since SP is set to 0 on  reset - we don't really need this!
                      ; a push will decrement SP before placing the low byte
                      ;of the return address on the stack
    ld r0,count
    call display
    hlt

:display    
    out r0
    djnz r0,display
    ret

:count
  .db 255

.end
