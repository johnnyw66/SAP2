# SAP2 Inspired Project


![SAP2 Inspired Project](/images/alusub.jpg)


24 August 2021
---

This microprocessor written for the LogiSim Evolution CAD can be built with standard TTL/CMOS logic chips.
Fed up with soldering - I wanted to 'build' the microprocessor before my attempt to describe this in *Verilog
HDL* and then placing the design on one of my Altera FPGAs. It will support 80 instructions which are listed below.


At some point I will add in I/O instructions and have it drive a VGA/Video Composite output
along with a Serial UART. I will also split the current 64k RAM into a 32k ROM with 32k RAM.
If my interest still holds - the ROM could contain some simple monitor program to load software over an RS232 serial port.
Perhaps look at retargeting a C Compiler?


For what it's worth - I've included the circuit for a programmer unit so the user can enter byte code by hand.
I prefer to use a combination of the LogicSim GUI and my simple assembler utility.

Assemble your machine code from a 'asm' text file using the python utility - and load the program into the RAM memory unit (right click and select 'Load Image' - then select an assembled hex file )


To assemble code - simple run *assembler.py test.asm* - this will produce a 'binary' version with the same
base name - but appended with '.hex' (i.e *assembler.py mycode.asm* produces *mycode.hex*)

Example code:


````
.org 0
:start
    movwi sp,0xffff   ; since SP is set to 0 on  reset - we don't really need this!
                      ; A push or call will decrement SP before placing the low byte
                      ; of the return address on the stack
    ld r0,count
    call display
    hlt

:display    
    out r0
    djnz r0,display
    ret

:count
  .db 255
  .ds 20 ; reserve 20 bytes ('zeroised')
  .dw 0xfffe ; 2-byte word

.end
`````

**Issues**

I am currently using **32** (!!!!) control lines. Way too much. Although the current design uses a 32-bit data output -
you can easily swap this for 4 conventional ROMs with 8-bit data buses. The utility *buildcontrolrom.py* can be modified
to build 4 microcode ROMs if you're inclined to build a real processor.


Perhaps I can get some inspiration from looking at the design of **Gigatron TTL computer** - which I built in 2018.
Using 32 control lines seems like a bit of an overkill.


# Instruction Set

*User Register instructions 2 Banks of 4 registers R0, R1, R2, R3 plus PC,SP and Flag Register*



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
OUT Rx| Rx sent to Display Unit|None|4
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
