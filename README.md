# SAP2 Inspired Project


![SAP2 Inspired Project](/images/alusub.jpg)


24 August 2021
---

This microprocessor written for the **LogiSim Evolution** CAD can be built with standard TTL/CMOS logic chips.
Fed up with soldering - I wanted to 'build' the microprocessor before my attempt to describe this in *Verilog
HDL* and then placing the design on one of my Altera FPGAs. It will support over 80 instructions which are listed below.


At some point I will add in I/O instructions and have it drive a VGA/Video Composite output
along with a Serial UART. I will also split the current 64k RAM into a 32k ROM with 32k RAM.
If my interest still holds - the ROM could contain some simple monitor program to load software over an RS232 serial port. Perhaps look at retargeting a C Compiler?


For what it's worth - I've included the sub-circuit for a programmer unit so the user can enter byte code by hand.
I prefer to use a combination of the LogicSim GUI and my simple **assembler utility**.

Assemble your machine code from an 'asm' text file using the included python utility **assembler.py** - and load the program into the RAM memory unit (right click the RAM unit and select 'Load Image' - then select an assembled file (.hex)). You start the LogicSim emulation by using the keys 'CMD/CTRL' + 'R'to reset the processor - followed by 'CMD/CTRL' + 'K' to start the CPU clock. You can change the speed of the processor by selecting **simulate** on the GUI and **Auto-Tick Frequency**.


To assemble code - simple run a command like *assembler.py test.asm* - this will produce a 'binary' version with the same base name - but appended with '.hex' (i.e *assembler.py mycode.asm* produces *mycode.hex*)

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

I've include a spreadsheet of my opcodes with their bytecode **make up**.
I've tried to group them wherever possible. I would appreciate any feedback.


**Issues**

I am currently using **32** (!!!!) control lines. Way too much. Although the current design uses a 32-bit data output - you can easily swap this for 4 conventional ROMs with 8-bit data buses. The utility *buildcontrolrom.py* can be modified to build 4 microcode ROMs if you're inclined to build a real processor.

Perhaps I can get some inspiration from looking at the design of the **Gigatron TTL computer** - which I built in 2018. Using 32 control lines seems like a bit of an overkill.

Updates
---

**27th August**: Addressing decoding is supported. I have now split the memory into two sections.
0x000 to 0x7fff now holds a ROM. 0x8000 to 0xffff is a 32 Kb RAM module. The ROM currently holds the 3 byte of instructions 'JMP 0x8000' at address 0x0000 -

Added example circuit to do memory mapped IO. Writes to 0x7ff0, 0x7ff1, 0x7ff2 set up registers to a crude sound system. See **sound.asm**

```
  .org 0x8000

  movi r0, 0xff   ; low freq
  movi r1, 0x00   ; high freq
  movi r2, 0x8f   ; volume - lower 4 bits and enable bit - MSB

:loopsnd
  call playfreq
  djnz r0, loopsnd
  movi r2,0x00
  call playfreq
  hlt



:playfreq
  st r0,0x7ff0    ; low freq
  st r1,0x7ff1    ; high freq 6 bits
  st r2, 0x7ff2   ; vol and enable (top bit)
  ret
.end

```

# Instruction Set

*User Register instructions 2 Banks of 4 registers R0, R1, R2, R3 plus PC,SP and Flag Register*



Opcode | Comment|Flags|Tstates
-------| -------|-----|-------
MOV Rx,Ry| Ry -> Rx | None|4
ADD Rx,Ry|Rx + Ry -> Rx|C Z V S|4
SUB Rx,Ry|Rx - Ry -> Rx| Z V S|4
AND Rx,Ry|Rx & Ry -> Rx|Z|4
OR Rx,Ry|Rx or Rx-> R|Z S V|4
XOR Rx,Ry| Rx ^ Ry -> Rx| Z S V|4
INC Rx | Rx + 1 -> Rx | Z S V O|5
SHL Rx | {Rx,Cf}<<1 -> Rx | Z S V C|5
SHR Rx | {Cf,Rx}>>1 -> Rx | Z S V C|5
DEC Rx | Rx - 1 -> Rx | Z S V O|5
INC SP | SP + 1 -> SP |None|5
DEC SP | SP - 1 -> SP |None|5
OUT Rx| Rx sent to Display Unit|None|4
*46 Opcodes in total*

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

Software Requirements
----

Java 8 (I used java version "1.8.0_60" - major version 52 and 1.11 - major version 55) on Mac OS X 10.15 (Catalina) - August 2021

To run LogiSim - just type the command **java -jar logisim-evolution-3.5.0-all.jar** from a terminal.

Python Utilities included-
----
**buildmicrocode.py** - Builds microcode instructions used by the **controller** subcircuit.
Note: If you change the control lines (their active state or pin order) - make sure you look at the
microcode **NOP** value after running this script. It should match the 32-bit hex value on the comparator input in the **controller** sub-circuit. A mismatch in the circuit value will mean that all your machine code instructions taking the full 20 T states!


**assembler.py** - Python utitlity to convert assembler source (.asm) to binary (hex) machine code.

**staticdisplay.py** Builds 7-Seg Control line Rom for the Decimal Display circuit.

Also, Thanks to...
---

**Dieter Muller** - (not the footballer!) - For his notes on building a 6502. His chapters on using multiplexers inspired my ALU sub-circuit. http://www.6502.org/users/dieter/

**Ben Eater** - I had already built part on an ALU before watching his videos - but it was his engaging Youtube content that really inspired me to finish off my first complete CPU. https://www.youtube.com/c/BenEater

**Shiva** -  My old workmate - who posed me the question on 'How do you multiply two numbers without using the
multiply or add operators' - a question he was asked back in a job interview in 2015.


Look out for
---
**James Sharman** - His YouTube content is amazing. Anyone new to building or understanding microprocessors - I would recommend watching **Ben's** channel - followed by **James's** videos on his **Pipelined CPU**. I use to work with James back in the 90s. He was **THE NERD** in our group of nerds. https://www.youtube.com/user/weirdboyjim
