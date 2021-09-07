# SAP2 Inspired Project


![SAP2 Inspired Project](/images/alusub.jpg)

24 August 2021
---

This SAP2 inspired microprocessor written for the **LogiSim Evolution** CAD can be built with standard TTL/CMOS logic chips.
Fed up with soldering - I wanted to 'build' the microprocessor before my attempt to describe this in *Verilog
HDL* and then place the design on one of my Altera FPGAs. It will support over 80 instructions which are listed below.


At some point I will add in I/O instructions and have it drive a VGA/Video Composite output
along with a Serial UART. I will also split the current 64k RAM into a 32k ROM with 32k RAM
(**Now completed! ROM 0x0000 - 0x7fff RAM 0x8000 - 0xffff**)
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
**Issues**
---

I am currently using **32** (!!!!) control lines. Way too much.

If you look at the spreadsheet (*uprocISA.ods*)  the processor opcodes with their bitcode make up, you can see I missed a trick with their values. Had I grouped the Reg/Reg instructions a little better I think I can reduce on the width of the controller ROM. I need to change the Reg instructions 8-bit bitcode to something like **1aaaddss** where the 3-bit value **aaa** is the ALU function, and the two 2-bit values **dd** and **ss** are the **d**estination and **s**ource Registers.

**dd**/**ss**|Reg
-------------|---
00|R0
01|R1
10|R2
11|R3

*aaa*|function
-----|--------
000| B + 0 (MOV rx,ry)?
001|A + B
010|A - B
011|A & B
100|A or B
101|A ^ B
110|SHR A + 0
111|SHL A + 0

(Note: A and B are the names I've given to the 8-bit ALU registers -
The function 'B+0' should not latch the Flag Register.)


See '*Proposed New ISA*' in the spreadsheet for updates.


Swapping the 32-bit ROM for 8-bit ROMs
---

 Although the current design uses a ROM with a 32-bit data output - you can easily swap this for 4 conventional ROMs with 8-bit data buses. The utility *buildcontrolrom.py* can be modified to build 4 microcode ROMs if you're inclined to build a real processor. I've included an alternative controller subcircuit (*controller_8bitroms*) for this purpose.



Updates
---
![SAP2 Inspired Project](/images/logicunit_function_generator2.jpg)
**2nd Septermber**: Added inbuilt assembler functions *@LOW* and *@HIGH* to calculate low and
high bytes from a 16-bit value.

```
.org 0x8000
  ; The following 3 groups of statements are equivalent.

  ; Group 1 - explicit 8-bit values
  movi r2,0xaa
  movi r3,0x81

  ; Group 2 - explicit 16-bit values using LOW and HIGH functions
  movi r2,@LOW(0x81aa)
  movi r3,@HIGH(0x81aa)

  ; Group 3 - symbol using LOW and HIGH functions
  movi r2,@LOW(lookuptable)
  movi r3,@HIGH(lookuptable)
  hlt

.org 0x81aa

:lookuptable
   .....
```

**27th August**: Addressing decoding is supported. I have now split the memory into two sections.
0x000 to 0x7fff now holds a ROM. 0x8000 to 0xffff is a 32 Kb RAM module. The ROM currently holds the 3 byte instruction 'JMP 0x8000' at address 0x0000 -

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
MOV Rx,Ry| Ry -> Rx |_|4
ADD Rx,Ry|Rx + Ry -> Rx|C Z V S|4
SUB Rx,Ry|Rx - Ry -> Rx| Z V S|4
AND Rx,Ry|Rx & Ry -> Rx|Z|4
OR Rx,Ry|Rx or Rx-> R|Z S V|4
XOR Rx,Ry| Rx ^ Ry -> Rx| Z S V|4
INC Rx | Rx + 1 -> Rx | Z S V O|5
SHL Rx | {Rx,Cf}<<1 -> Rx | Z S V C|5
SHR Rx | {Cf,Rx}>>1 -> Rx | Z S V C|5
DEC Rx | Rx - 1 -> Rx | Z S V O|5
INC SP | SP + 1 -> SP |_|5
DEC SP | SP - 1 -> SP |_|5
OUT Rx| Rx sent to Display Unit|_|4
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
MOVI Rx,8bit | 8-bit value -> Rx| _|6
LD Rx,16bitaddr |@(addr) -> Rx |_|7
ST Rx,16bitaddr |@(addr) <- Rx |_|7
MOVWI SP,16bitaddr| 16-bit value -> SP| _|7
MOVWI R0,16bitaddr+| 16-bit value -> {R1,R0}|_|7
MOVWI R2,16bitaddr+| 16-bit value -> {R3,R2}|_|7
*4 Opcodes in total(bottom 2 to be implemented)*

Opcode|Action|Flags|Tstates
------|------|-----|-------
DJNZ Rx,16bitaddr | Rx - 1 -> Rx, 16bitaddr if NZ ? PC + 1 -> PC| Z S V O|8
JPNZ 16bitaddr | PC <- PC + 1 if Z ? 16bitaddr|_|8
JPNC 16bitaddr | PC <- PC + 1 if C ? 16bitaddr|_|8
JMP  16bitaddr | PC <- 16bitaddr |_|8
CALL 16bitaddr | @SP <- PC + 1, PC <- 16bitaddr, SP <- SP - 2| _|14
RET| PC <- @SP|_|10
*9 Opcodes in total*

Opcode|Action|Flags|Tstates
------|------|-----|-------
PUSH R0| R0 -> @SP, R1-> @SP+1 SP <- SP - 2|_|9
PUSH R2| R2 -> @SP, R3-> @SP+1 SP <- SP - 2|_|9
POP R0 | @SP -> R1, @SP+1 -> R0, SP <- SP + 2|_|9
POP R2 | @SP -> R3, @SP+1 -> R2, SP <- SP + 2|_|9
*4 Ocodes in total*


Opcode|Action|Flags|Tstates
------|------|-----|-------
CLC| Cf <- 0| C |5
SETC|Cf <- 1| C|5
NOP| no operation|_|4
EXX| Switch Reg Bank|_|4
HLT| Stop uProc|_|4
*5 Ocodes in total*

**CLC and SETC are currently 'fudged' as they affect the sign and overflow FLAGS**


Example: 16-bit Jump table (using the preprocessor *cpp*)
---
```
.org 0x8000
#define tableentry(_nm) jmp _nm \
                      nop

:start
movwi r0,0x1234
movwi r2,0xabcd

movi r0,0
call indexjmp

movi r0,1
call indexjmp

movi r0,2
call indexjmp

movi r0,0x66
out r0
hlt

:indexjmp
  ; Call from a list of functions define at 'functable'
  ; indexed by the lower 6-bit number in R0 -

  ; Assuming our table has each entry defined by
  ; 4 bytes - (1 x jpm addr + 1 x nop instructions) -
  ; we simply multiply the 16 bit value R1R0 pair by 4
  ; and add the result to the address
  ; of the start of the table (functable).
  ; The resultant address is pushed onto the stack
  ; and called by executing a RET instruction

  andi r0,0x3f
  movi r1,0
  clc
  shl r0
  shl r1
  shl r0
  shl r1

  movi r2,@LOW(functable)
  movi r3,@HIGH(functable)

  add  r2,r0
  add r3,r1

  push r2
  ret





:fnc1
  movi r0,0x11
  out r0
  ret

:fnc2
  movi r0,0x22
  out r0
  ret

:fnc3
  movi r0,0x33
  out r0
  ret

.org 0x8100
:functable
  tableentry(fnc1)
  tableentry(fnc2)
  tableentry(fnc3)

  .end


```


16-Bit Multiply (using *cpp*)
---

```

; Preprocess this source with the standard C preprocessor 'cpp'
; Eg. 'cpp -DADDRESS=0x8000 -P testmacro.asm tmp.asm'
; and then assemble the processed cpp version - 'assember.py tmp.asm'



#ifndef ADDRESS
#define ADDRESS 0x8000
#endif

#define multbit(_skipadd)  clc \
                          shr r1 \
                          shr r0 \
                          jpnc _skipadd \
                          push r2 \
                          exx \
                          pop r2 \
                          clc \
                          add r0,r2 \
                          add r1,r3 \
                          exx \
                    :_skipadd \
                          clc \
                          shl r2 \
                          shl r3

;                         RAM Source
                          .org ADDRESS

:start
                          movi r0, 0xab
                          movi r1, 0x00   ; mov r0r1, 0x00ab

                          movi r2, 0x78
                          movi r3, 0x01    ; mov r2r3, 0x0178
                          ; Answer should be 0xfb28

                          call mult16bit
                          hlt

:mult16bit
                          ; r0r1 = r0r1 x r2r3
                          exx
                          push r0     ; preserve main bank regs
                          push r2
                          movi r0,0
                          movi r1,0
                          exx

                          multbit(bit0)
                          multbit(bit1)
                          multbit(bit2)
                          multbit(bit3)

                          multbit(bit4)
                          multbit(bit5)
                          multbit(bit6)
                          multbit(bit7)

                          multbit(bit8)
                          multbit(bit9)
                          multbit(bit10)
                          multbit(bit11)

                          multbit(bit12)
                          multbit(bit13)
                          multbit(bit14)
                          multbit(bit15)


                          ; place answer in the bank we started with
                          exx
                          push r0
                          exx
                          pop r0
                          ; Restore secondary bank regs
                          exx
                          pop r2
                          pop r0
                          exx

                          ret

                          .end


```

```
# Simple script to preprocess assembler source with cpp
cpp $@ a.asm
./assembler.py a.asm -3 -s
rm -f a.asm
```

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

**The utilities where developed and tested on Python 3.7**

Thanks to...
---

**Dieter Muller** - (not the footballer!) - For his notes on building a 6502. His chapters on using multiplexers inspired my ALU sub-circuit. http://www.6502.org/users/dieter/

**Ben Eater** - I had already built part of an ALU before watching his videos - but it was his engaging Youtube content that really inspired me to finish off my first complete CPU. https://www.youtube.com/c/BenEater

**Shiva** -  My old workmate - who posed me the question on 'How do you multiply two numbers without using the
multiply or add operators?' - a question he was asked in a job interview back in 2015.


Look out for
---
**James Sharman** - His YouTube content is amazing. Anyone new to building or understanding microprocessors - I would recommend watching **Ben's** channel - followed by **James's** videos on his **Pipelined CPU**. I use to work with James back in the 90s. He was **THE NERD** in our group of nerds. https://www.youtube.com/user/weirdboyjim
