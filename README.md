# SAP2 Inspired Project - A LogiSim Evolution Simulation


![SAP2 Inspired Project](/images/alusub.jpg)



24 August 2021
---

This SAP2 inspired microprocessor written for the **LogiSim Evolution** CAD can be built with standard TTL/CMOS logic chips.
'Simple As Possible 2' is partially described in the Albert Malvino's book **'Digital Computer Electronics - An introduction to Microcomputers'** (pub: 1983).
The book goes on to describe the processor's architecture set containing 42 instructions.

A few years ago, I built a simple 8-bit microprocessor using TTL/CMOS logic. I wanted to limit the build using boolean logic chips - so I even built an 8-bit adder from AND/OR/XOR chips - rather than using something like a couple of 74HCT283s. I've included in this document a few photographs of the Arthimetic Logic Unit (ALU) and supporting boards from my initial build.

The final processor was massive - fitting on a king sized bed. Although the processor worked - It had a very limited instruction set and was not very practical, to say the least! Initially, I tried to build using just breadboards but got fed up with wires popping out of place whenever I moved my build from under my bed. In the end, I resorted to hours of soldering.

Four years on and fed up with soldering - I wanted to 'build' an improved microprocessor before my attempt to describe this in *Verilog
HDL* and then place the design on one of my Altera FPGAs. The processor will support over 90 instructions, all of which are listed below.

**LogiSim Evolution** is a design tool which allows the user to define and simulate logic circuits. It is free and open-source and works on many operating systems - such as Linux, Mac OS and Windows. The main prerequisite is having an installed Java runtime on your system. For a detailed look - checkout the many Youtube tutorials such as https://www.youtube.com/watch?v=cMz7wyY_PxE

In this project, I've included with the LogiSim source some Python utilities which I coded. Please do what you want with them. If you find them useful - please consider giving this project and repository a mention.


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
**2nd Septermber**: Added inbuilt assembler functions *>* and *<* to calculate low and
high bytes from a 16-bit value.

```
.org 0x8000
  ; The following 3 groups of statements are equivalent.

  ; Group 1 - explicit 8-bit values
  movi r2,0xaa
  movi r3,0x81

  ; Group 2 - explicit 16-bit values using LOW and HIGH functions
  movi r2,>0x81aa
  movi r3,<0x81aa

  ; Group 3 - symbol using LOW and HIGH functions
  movi r2,>lookuptable
  movi r3,<lookuptable
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

*Flag Register - **Z** Zero **S** Sign **V** Overflow **O** Parity (Odd)*


Opcode | Comment|Flags|Tstates
-------| -------|-----|-------
MOV Rx,Ry| Ry -> Rx |_|4
ADD Rx,Ry|Rx + Ry -> Rx|C Z V S|4
SUB Rx,Ry|Rx - Ry -> Rx| Z V S|4
AND Rx,Ry|Rx & Ry -> Rx|Z|4
OR Rx,Ry|Rx or Rx-> R|Z S V|4
XOR Rx,Ry| Rx ^ Ry -> Rx| Z S V|4
SWP Rx,Ry| Rx <-> Ry|_|8
INC Rx | Rx + 1 -> Rx | Z S V O|5
SHL Rx | {Rx,Cf}<<1 -> Rx | Z S V C|5
SHR Rx | {Cf,Rx}>>1 -> Rx | Z S V C|5
DEC Rx | Rx - 1 -> Rx | Z S V O|5
INC SP | SP + 1 -> SP |_|5
DEC SP | SP - 1 -> SP |_|5
OUT Rx| Rx sent to Display Unit|_|4
CSP Rx| SP copied to RxRy pair|_|5
*57 Opcodes in total*

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
JPZ 16bitaddr | PC <- PC + 1 if !Z ? 16bitaddr|_|8
JPNC 16bitaddr | PC <- PC + 1 if C ? 16bitaddr|_|8
JPC 16bitaddr | PC <- PC + 1 if !C ? 16bitaddr|_|8
JPNV 16bitaddr | PC <- PC + 1 if V ? 16bitaddr|_|8
JPV 16bitaddr | PC <- PC + 1 if !V ? 16bitaddr|_|8
JMP  16bitaddr | PC <- 16bitaddr |_|8
CALL 16bitaddr | @SP <- PC + 1, PC <- 16bitaddr, SP <- SP - 2| _|14
RET| PC <- @SP|_|10
*10 Opcodes in total*

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

  movi r2,>functable
  movi r3,<functable

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
Hello World
---

Already familiar with **LogiSim**? Perhaps you just want a taster of what this microprocessor can do?

Follow these simple steps, outlined below..

Run **LogiSim Evolution** and open the project file **sap2.cir** using the File sub-menu.
Once loaded, left click on the main circuit pane and keeping the mouse button down - scroll the pane so that you can see the **RAM Module**.
Left click on the this module and select **load image** option and then select the file **sqrt.hex** followed by clicking on **Open**. 
You should notice the Ram Module change from having a sequence of zeros to starting with the hex bytes **40 c5**

![Square Root Routine Loaded](/images/rammodule.png)

We're now going to run a simple square root test assembled from the source **sqrt.asm** (listed below).
The hexadecimal equivalent of this code is contained within the file **sqrt.hex**. 

**LogiSim** will store the binary equivalent in the Ram Module which the microprocessor will attempt to run, when started. 

The hex file **sqrt.hex** was produced using the Python utility **assembler.py** by running the command **python assembler.py sqrt.asm**.



````
.org 0x8000

movi r0,197
movi r1,1
movi r2,1

:loop
; Display the current estimate of sqr(197)
out r2
sub r0,r1
jpv foundit
jpz foundit

:continue
addi r1,2
inc r2
jmp loop

:foundit
hlt

.end
`````
In the **Simulate** sub menu - make sure that the **auto tick frequency** option is **64Hz**.
Scroll the main circuit window pane (left click and hold) to view the **DISPLAY MODULE**. Make sure you can see the **OUTPUT REGISTER** (Decimal)
display.

![Output Reg](/images/outputreg.png)


Start running the machine code by using the following commands:-

**CONTROL+K** to start the microprocessor clock which will run the assembled machine code.
You can use **CONTROL+R** to reset the microprocessor. Note: Mac Users replace the **CMD** key for **CONTROL**.

With the cicuit set to auto tick - the code will start to run, updating the decimal display until it reaches the result '15', which is an approximation (albeit poor) of the square root of 197. 

Note: Very near the output **DISPLAY MODULE**  I've also included debug output from the two banks of the four 8-bit registers (R3,R2,R1,R0 and their alternate counterparts). Look out for the labels **DBGREGBANK0** and **DBGREGBANK1** showing 32-bit values.





Software Requirements
----

**Java 8** (I used java version "1.8.0_60" - major version 52 and 1.11 - major version 55) on Mac OS X 10.15 (Catalina) - August 2021

To run LogiSim - just type the command **java -jar logisim-evolution-3.5.0-all.jar** from a terminal.

**Python 3.7** - Needed to run the assembler and build the display ROM and microcode instructions ROM.

At some point I will also produce a Python Simulator for a version of a SAP2 Single Board Computer!


Python Utilities included-
----
**buildcontrolrom.py** - Builds microcode instructions used by the **controller** subcircuit.

If you want to modify the design of the processor - making changes to its instruction architecture or changing the control lines (their active state or pin order) - you'll need to run this utility and upload the generated file into the control ROM. 
Simple run the python code from the command line.

*python3 buildcontrolrom.py*

![Running buildmicrocode](/images/buildcontrolrom-running.png)

![NoOp buildmicrocode](/images/buildcontrolrom-nopcode.png)

![32-bit Comparator LogiSim](/images/controller_32bit_comparator.png)

Make sure you look at the microcode **NOP** value after running this script. It should match the 32-bit hex value on the 32-bit comparator input in the **controller** sub-circuit. A mismatch in the circuit value will mean that all your machine code instructions taking the full 20 T states!

Running buildcontrolrom.py produces the file **microcode32bit.rom** which should be loaded into the control ROM found in the **controller** subcircuit. You only need to do this once, whenever you make a change to the Instruction Set or Control lines of the controller.

### What is Microcode and What Does the buildcontrolrom.py Utility Do?

Microcode is a low-level hardware description language utilized in the control unit of a microprocessor to implement its instruction set architecture (ISA). It serves as an intermediary between machine code instructions (those written by programmers) and the hardware's actual implementation of those instructions.
In a microprocessor, the control unit is responsible for fetching native instructions from memory, decoding them, and executing them. Microcode plays a crucial role in this process by translating individual instructions of the ISA into a sequence of micro-operations that the hardware can execute.

The **buildcontrolrom.py** Python utility is designed to produce a binary/hex file of the microcode used to control our microprocessor's lines. This microcode, stored in ROM, is utilized by our control unit to execute each opcode instruction through a predefined sequence.
Our microprocessor design currently employs 32 control lines, primarily for reading and writing to registers and memory.

### How it Works:

1. Instruction Fetch: The control unit retrieves the next instruction from memory.
1. Instruction Decode: The control unit decodes the instruction to determine the required operation.
1. Microcode Execution: Microcode translates the decoded instruction into a sequence of micro-operations, each corresponding to a specific hardware action such as reading from registers, performing arithmetic/logic operations, or accessing memory.
1. Hardware Execution: The hardware executes the micro-operations sequentially to complete the instruction.
1. Repeat: Steps 1-4 are repeated for each instruction in the program.

Microcode allows for a flexible and efficient implementation of the processor's instruction set, enabling support for various instructions while maintaining a relatively simple hardware design. Additionally, microcode can be updated or modified to fix bugs, add new instructions, or improve performance without requiring a complete processor redesign.

Let’s give you an example of how we coded one particular opcode in our ISA by referring to our source code **buildcontrolrom.py**.

First look at the portion of the Python source which defines these control lines.

````
clLines = [
    {'key':"Cp", 'bit':31, 'active': ACTIVEHIGH, 'desc':"Enable PC count (inc PC)"},
    {'key':"Ep", 'bit':30, 'active': ACTIVEHIGH, 'desc':"Place PC onto the Bus"},
    {'key':"nLm", 'bit':29, 'active': ACTIVELOW, 'desc':"Load contents of Bus into Memory Address Reg"},
    {'key':"nCE", 'bit':28, 'active': ACTIVELOW, 'desc':"Place current data in RAM onto BUS"},

    {'key':"nLi", 'bit':27, 'active': ACTIVELOW, 'desc':"Load contents of Bus into the Instruction Reg"},
    {'key':"nEi", 'bit':26, 'active': ACTIVELOW, 'desc':"Place contents of the Instruction Reg onto the Bus"},
    {'key':"nLa", 'bit':25, 'active': ACTIVELOW, 'desc':"Load contents of the Bus into the A Reg"},
    {'key':"Ea",  'bit':24, 'active': ACTIVEHIGH, 'desc':"Place contents of the A Reg onto the BUS"},

    {'key':"Eb",  'bit':23, 'active': ACTIVEHIGH, 'desc':"Place contents of the B Reg onto the BUS"},
    {'key':"Eu",  'bit':22, 'active': ACTIVEHIGH, 'desc':"Enable ALU (output directly to B Reg)"},
    {'key':"nLb", 'bit':21, 'active': ACTIVELOW, 'desc':"Load contents of B reg 'bus' into B Reg"},
    {'key':"nLo", 'bit':20, 'active': ACTIVELOW, 'desc':"Load contents of Bus into Output Reg"},

    {'key':"Lr",  'bit':19, 'active': ACTIVEHIGH, 'desc':"Load to RAM (STA op)"},
    {'key':"Lp",  'bit':18, 'active': ACTIVEHIGH, 'desc':"Load PC (JUMP instructions) used with f1 and f0"},
    {'key':"f1",  'alias':{'a1'},'bit':17, 'active': ACTIVEHIGH, 'desc':"JUMP condition function bit 1"},
    {'key':"f0",  'alias':{'a0','Su'},'bit':16, 'active': ACTIVEHIGH, 'desc':"JUMP condition Function bit 0 {00 -> Carry, 01 -> Non Zero, 10 -> Parity Odd, 11 --> Always}"},
#    {'key':"Cp", 'bit':7, 'active': ACTIVEHIGH, 'desc':"TEST DUP"},

#
    # Free control lines for use later
    {'key':"nLal",  'bit':15, 'active': ACTIVELOW,'desc':"Load low byte of address with contents on DBUS"},
    {'key':"nLah",  'bit':14, 'active': ACTIVELOW, 'desc':"Load high byte of address with contents on DBUS"},
    {'key':"E16",  'bit':13, 'active': ACTIVEHIGH, 'desc':"Show DBUS<->ABUS regsiters (two) on Address Bus"},
    {'key':"Lf",  'bit':12, 'active': ACTIVEHIGH, 'desc':"Latch Flag Register"},

    {'key':"Ek",  'bit':11, 'active': ACTIVEHIGH,'desc':"Load Conents of Bank Reg onto DBUS"},
    # Uses f0, f1
    {'key':"nLk",  'bit':10, 'active': ACTIVELOW, 'desc':"Latch Conents on DBUS into Bank Reg"},
    {'key':"k1",  'bit':9, 'active': ACTIVEHIGH, 'desc':"Bank Register Write Select bit 1"},
    {'key':"k0",  'bit':8, 'active': ACTIVEHIGH, 'desc':"Bank Register Write select bit 0"},

    # 'alias' allows us to refer to the same pins as different names - useful for shared select function pins
    {'key':"f2",  'alias':{'a2'}, 'bit':7, 'active': ACTIVEHIGH,'desc':"Select bit for Constant Bank/ALU Function"},
    {'key':"Ec",  'bit':6, 'active': ACTIVEHIGH, 'desc':"Place Constant (from Constant Bank) defined by {f2,f1,f0} on the DBUS"},
    {'key':"Xx",  'bit':5, 'active': ACTIVEHIGH, 'desc':"Swap over reg banks (EXX instruction)"},
    {'key':"Sa",  'bit':4, 'active': ACTIVEHIGH, 'desc':"'Source Address' Source for A B Reg pair can come from DBUS or Address BUS (0 is DBUS)"},

    {'key':"Us",  'bit':3, 'active': ACTIVEHIGH,'desc':"Increment if 1 or Decrement if 0 - used with Cs"},
    {'key':"Es",  'bit':2, 'active': ACTIVEHIGH, 'desc':"Place Stack Address on Address Bus"},
    {'key':"Cs",  'bit':1, 'active': ACTIVEHIGH, 'desc':"Enable Counting"},
    {'key':"nLs",  'bit':0, 'active': ACTIVELOW, 'desc':"Load StackPointer with contents on ABUS"},
]

````


The definitions defined in this array are somewhat verbose and slightly inefficient in terms of speed - but I hope you agree that the tradeoff is readability. I’ve added a simple description in the ‘desc’ field which I hope you will also find useful.

Our controller controls 32 lines on our SAP2, each one you should find on our hardware design.

Let’s look at one of them.

````
{'key':"nLal",  'bit':15, 'active': ACTIVELOW,'desc':"Load low byte of address with contents on DBUS"},
````

This line is defined by the key name, along with the control bit and the required signal level the control unit needs to used when the line is active. **ACTIVELOW** means the defined bit will be set to 0 when required.  **ACTIVEHIGH** will set that control line to 1 when activated.

You may have noticed that I have reinforced the ‘active’ state with a pre index of ‘n’ in the key name.
So in the above example, bit 15 of our control unit will control actions on the Load address low byte 8 bit register. Since this control line is active low, I have placed an ‘n’ at the start. (‘n’ for ‘NOT’).


Now let’s look at a particular sequence of microcode instructions for one of the opcodes.
Look at the `opcodes` array in **buildcontrolrom.py** taking note of the comment that the first 3 microcode instructions are always the same for  all our opcode instructions -(search for the name **‘LD R0’**). The first three opcodes defined elsewhere - will read in the instruction to a meta register called the Instruction Register (IR) and bump the microprocessor’s program counter (PC) so it points to any more opcode data or the next opcode instruction to run.


````
    {'name':'LD R0','bytecode': 0x14, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'nCE','nLk'}         # Finally Write the contents of the current address in MAR to R0 reg
    ]},
````
The entry  {'Ep','nLm'} means that the control output must set bit 30 and reset bit 29 when that particular microcode is triggered. Other bits on the 32 bit word are determined by the **microcode NOP value**.

We can see from this entry that there are 6 control line instructions. Along with the default 3 from the FETCH cycles this makes a total of 9 control line instructions.
On each microprocessor clock tick the control unit will take these 9 instructions and set/reset particular control lines.  The 9 instructions are used to build a portion of ROM used for our particular instruction (LD RO,address). You will see that each element in the array consists of a series of bits, defined by their clLines keys which are combined together to build a 32 bit control word.  So for this particular instruction our control unit will go through 9 clock cycles to present each of the 32 bits.


### The microcode ‘NOP’ value

A few words about this value.  It is calculated by going through all of the 32 bits defined clLines and setting the lines high or low depending on the ‘active’ value. We need to make sure that the NOP code value will present control lines on the control unit to the level that will effectively do nothing on the registers/latch lines they are controlling.

The NOP value I have given for the defined clLines described above is 
**3e 30 c4 01** hexadecimal (0011 0111 0011 0000 1010 0100 0000 0001 binary). The binary value is simply calculated by going through bits 31 to 0 defined in the table clLines, setting that bit’s value to 0 for **ACTIVEHIGH** and 1 for **ACTIVELOW**.

```
# simple way of calculating NOP value
nop_value = 0
for control in clLines:
    nop_value |= ((1<<control['bit']) if control['active'] == ACTIVELOW else 0) 
print(f"NOP value = {nop_value:04x}")

```
**assembler.py** - Python utitlity to convert assembler source (.asm) to binary (hex) machine code.
Remember the RAM module starts at the address 32768 so most times (unless you're updating the processor's ROM routines) - you will need to use the directive **.ORG 0x8000**.

```
Example Usage: ./assembler.py example.asm [options]

Options:-
 -v verbose
 -d debug
 -q quiet
 -s symbol table
 -3 [default] V3 addressed hex output
 -2 raw hex output
 -b binary output
 -n no output [-c dissassembled code]
 -r ROM address offset on V3 Hex output
```


**staticdisplay.py** Builds 7-Seg Control line Rom for the Decimal Display circuit.

**The utilities were developed and tested on Python 3.7**

Coming Soon! SAP2 Single Board Computer Emulator.
---
July 2024 - I've started to code a SAP2 SBC simulator in Python. Watch this space!!

Thanks to...
---

**Dieter Muller** - (not the footballer!) - For his notes on building a 6502. His chapters on using multiplexers inspired my ALU sub-circuit. http://www.6502.org/users/dieter/

**Ben Eater** - I had already built part of an ALU before watching his videos - but it was his engaging Youtube content that really inspired me to finish off my first complete CPU. https://www.youtube.com/c/BenEater

**Shiva** -  My old workmate - who posed me the question on 'How do you multiply two numbers without using the
multiply or add operators?' - a question he was asked in a job interview back in 2015.


Look out for
---
**James Sharman** - His YouTube content is an excellent 'adventure' into building a **Pipelined CPU**. Anyone new to building or understanding microprocessors - I would recommend watching **Ben's** channel - followed by **James's** videos on his **Pipelined CPU**. I use to work with James back in the 90s on the very latest gaming consoles. I'm guessing his inspiration for the pipeline design comes from working on the PlayStation PS1.  The PS1's CPU, the R3000, employed a 5-stage instruction pipeline.  https://www.youtube.com/user/weirdboyjim

**Bill Buzbee** - His **Magic-1** TTL mini computer is a truimph in terms of both hardware and software. His hardware is very cool - but the supporting software is **awesome**, making this the only **TTL Computer** on the Youtube community I know of. **Magic-1** has its own OS (Minix), Compiler, Assembler, Linker and Debugger!!! **We're not worthy!** https://www.youtube.com/channel/UCVI4UsYLoRkWOG_bDMaHGgA 




