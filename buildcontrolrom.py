#!/usr/bin/env python3

controlWordSize = 32
ACTIVEHIGH = 1
ACTIVELOW = 0

# Definition for each of our control lines. We define which bit in the
# control word they occupy and if that control bit is active low or active high.

opcodeTable = {}

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
# Every microprocessor opcode instruction will have the
# same three controlwords for T1,T2 and T3,
# defined below
fetchControlWords = [{'Ep','nLm'},{'Cp'},{'nCE','nLi'}]


def decorateRawALUFunction(bSet,rawno):
    if (rawno & 1 == 1):
        bSet.add('a0')
    if (rawno & 2 == 2):
        bSet.add('a1')
    if (rawno & 4 == 4):
        bSet.add('a2')

    return bSet

def decorateReadReg(bSet,regNo):
    if (regNo & 1 == 1):
        bSet.add('f0')
    if (regNo & 2 == 2):
        bSet.add('f1')
    return bSet

def decorateWriteReg(bSet,regNo):
    if (regNo & 1 == 1):
        bSet.add('k0')
    if (regNo & 2 == 2):
        bSet.add('k1')
    return bSet

def decorateFunction(bSet,function):
    if (function == 'ADD'):
        decorateRawALUFunction(bSet,0)
    elif (function == 'SUB'):
        decorateRawALUFunction(bSet,1)
    elif (function == 'AND'):
        decorateRawALUFunction(bSet,2)
    elif (function == 'OR'):
        decorateRawALUFunction(bSet,3)
    elif (function == 'XOR'):
        decorateRawALUFunction(bSet,4)
    elif (function == 'SHR'):
        decorateRawALUFunction(bSet,5)
    elif (function == 'SHL'):
        decorateRawALUFunction(bSet,6)


    return bSet


def alufunction(*args):
    posargs = args[0]
    keywords = args[1]
    control = []


    fnc = keywords['afnc']
    rx = keywords['rx']

    control.append(decorateReadReg({'Ek','nLa'},rx))

    if ('ry' in keywords):
        control.append(decorateReadReg({'Ek','nLb'},keywords['ry']))

    control.append(decorateWriteReg(decorateFunction({'nLk','Eu','Lf'},fnc),rx))

    return control

def bankregfunction(*args):
    control = {}
    return control

def aluimmediate(*args):
        posargs = args[0]
        keywords = args[1]
        control = []
        fnc = keywords['afnc']
        rx = keywords['rx']
        control.append({'Ep','nLm'})
        control.append({'Cp','nCE','nLb'})
        control.append(decorateReadReg({'Ek','nLa'},keywords['rx']))
        control.append(decorateWriteReg(decorateFunction({'nLk','Eu','Lf'},fnc),rx))
        return control

macros = {
            'alumacro': alufunction,
            'aluimmediatemacro' : aluimmediate
}


def macro(mname,*posargs,**keywords):
    fnc = macros[mname]
    return fnc(posargs,keywords)

# Definition for each opcode in our microprocessor. We need to define
# those control lines which are active in each cycle.
# Note: The first three cycles T1, T2, T3
# are already defined in our 'fetchControlWords' array.

opcodes = [
   {'name':'NOP','bytecode': 0x00, 'control': []
        #macro('alumacro', rx=3, ry=2, afnc = 'SUB',latchflag = True)
   },

   # CLEAR CARRY IS A BODGE! - IT SCREWS UP OTHER FLAGS
   # SEE A MICROCODE DOCTOR- QUICK!
   {'name':'CLC','bytecode': 0x01, 'control':[
        {'Ec','nLb','nLa'},  # Constant 0 (Value is 0) on the bus, Save in A and B REG
        {'Eu','Lf'} # Doing a 0 + 0 with our ALU Will set Zero flag, maybe affect Sign - Latch new flag state (Lf)
   ]},

   # SET CARRY IS A BODGE! - IT SCREWS UP OTHER FLAGS
   # SEE A MICROCODE DOCTOR- QUICK!
   {'name':'SETC','bytecode': 0x02, 'control':[
        {'Ec','f0','f1','f2','nLb','nLa'},  # Constant 7 (Value is 0xff) on the bus, Save in A and B REG
        {'Eu','Lf'} # Will set Zero flag, maybe affect Sign and Overflow - Latch new flag state (Lf)
   ]},


   # Legacy instructions - which work on A/B regsiters
    # Legacy OPCODES TBDeprecated

    {'name':'ADD','bytecode': 0x03,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'nCE','nLb'},        #
        {'nLa','Eu','Lf'}
    ]},

    {'name':'SUB','bytecode': 0x04,
        'control':
        [
            {'Ep','nLm'},
            {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
            {'Ep','nLm'},
            {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
            {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

            {'nCE','nLb'},        #
            {'nLa','Eu','Su','Lf'}
    ]},




    {'name':'JMP','bytecode': 0x05,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0','f1'},        # Enable both bytes of 2 address reg Write to PC if condition true
    ]},


    {'name':'JPNZ','bytecode': 0x06,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0'},        # Enable both bytes of 2 address reg Write to PC if condition true
    ]},

    {'name':'LDI','bytecode': 0x07,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLa'},

    ]},


    {'name':'SUBI','bytecode': 0x08,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLb'},
        {'nLa','Eu','Su','Lf'}
    ]},

    {'name':'OUT','bytecode': 0x09,
    'control':
    [
        {'Ea','nLo'},
    ]},


    {'name':'LDA','bytecode': 0x0a, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)
        {'nCE','nLa'}         # Finally Write the contents of the current address in MAR to A reg
    ]},


    {'name':'STA','bytecode': 0x0b, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'Ea','Lr'}         # Finally Write the contents of A reg to the current address in MAR.
    ]},



    # NEW BANK REG instructions
    # k1,k0 used to determin which register to write to.
    # f1,f0 used to determin which register to read from.

    # {k1,k0}: b00 - R0, b01 - R1, b10 - R2, b11 - R3
    # {f1,f0}: b00 - R0, b01 - R1, b10 - R2, b11 - R3

    {'name':'OUT R0','bytecode': 0x10,
    'control':
    [
        {'Ek','nLo'},
    ]},
    {'name':'OUT R1','bytecode': 0x11,
    'control':
    [
        {'Ek','f0','nLo'},
    ]},
    {'name':'OUT R2','bytecode': 0x12,
    'control':
    [
        {'Ek','f1','nLo'},
    ]},
    {'name':'OUT R3','bytecode': 0x13,
    'control':
    [
        {'Ek','f0','f1','nLo'},
    ]},


    {'name':'LD R0','bytecode': 0x14, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'nCE','nLk'}         # Finally Write the contents of the current address in MAR to R0 reg
    ]},


    {'name':'LD R1','bytecode': 0x15, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'nCE','nLk','k0'}         # Finally Write the contents of the current address in MAR to R0 reg
    ]},

    {'name':'LD R2','bytecode': 0x16, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'nCE','nLk','k1'}         # Finally Write the contents of the current address in MAR to R0 reg
    ]},

    {'name':'LD R3','bytecode': 0x17, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'nCE','nLk','k1','k0'}         # Finally Write the contents of the current address in MAR to R0 reg
    ]},

    {'name':'ST R0','bytecode': 0x18, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'Ek','Lr'}         # Finally Write the contents of REG0 reg to the current address in MAR.
    ]},

    {'name':'ST R1','bytecode': 0x19, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'Ek','Lr','f0'}         # Finally Write the contents of REG0 reg to the current address in MAR.
    ]},

    {'name':'ST R2','bytecode': 0x1a, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'Ek','Lr','f1'}         # Finally Write the contents of REG0 reg to the current address in MAR.
    ]},

    {'name':'ST R3','bytecode': 0x1b, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'Ek','Lr','f1','f0'}         # Finally Write the contents of REG0 reg to the current address in MAR.
    ]},


    {'name':'LDI SP','bytecode': 0x1c, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLs'},        # Enable both bytes of 2 address reg and Write to Stack Reg.

    ]},

    {'name':'INC SP','bytecode': 0x1d, 'control':
    [
        {'Cs','Us'}
    ]},

    {'name':'DEC SP','bytecode': 0x1e, 'control':
    [
        {'Cs'}
    ]},

    {'name':'PUSH R0R1','bytecode': 0x1f, 'control':
    [
        {'Cs'}, #DEC SP
        {'Es','nLm'}, # Place Stack address in MAR
        {'Ek','Lr','Cs'}, #Place Contents of R0 into RAM location pointing by MAR. also DEC SP
        {'Es','nLm'}, #  Load SP adress into MAR
        {'Ek','f0','Lr'} # Place contents of R1 into RAM location pointed by MAR


    ]},

    {'name':'PUSH R2R3','bytecode': 0x20, 'control':
    [
        {'Cs'}, #DEC SP
        {'Es','nLm'}, # Place Stack address in MAR
        {'Ek','f1','Lr','Cs'}, #Place Contents of R2 into RAM location pointing by MAR. also DEC SP
        {'Es','nLm'}, #  Load SP adress into MAR
        {'Ek','f0','f1','Lr'} # Place contents of R3 into RAM location pointed by MAR


    ]},

    {'name':'TODO PUSHALL','bytecode': 0x21, 'control':
    [
    ]},

    {'name':'POP R0R1','bytecode': 0x22, 'control':
    [
        {'Es','nLm'},
        {'nCE','nLk','k0'},
        {'Cs','Us'},
        {'Es','nLm'},
        {'nCE','nLk','Cs','Us'}

    ]},

    {'name':'POP R2R3','bytecode': 0x23, 'control':
    [
        {'Es','nLm'},
        {'nCE','nLk','k0','k1'}, #R3
        {'Cs','Us'},
        {'Es','nLm'},
        {'nCE','nLk','k1','Cs','Us'} #R2

    ]},

    {'name':'TODO POPALL','bytecode': 0x24, 'control':
    [
    ]},

    {'name':'EXX','bytecode': 0x25,
    'control':
    [
        {'Xx'},
    ]},

    {'name':'MOVIW R0','bytecode': 0x28,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLk'},   # write low byte (in memory) to R0 and inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLk','k0'},  # write high byte to R1, inc pc to point to next opcode instruction
    ]},

    {'name':'MOVIW R2','bytecode': 0x2a,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLk','k1'},  # write low byte (in memory) to R2 and inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLk','k1','k0'},  # write high byte to R3, inc pc to point to next opcode instruction

    ]},


    # NEW Swap Instructions Test
    {'name':'SWAP R0,R2','bytecode': 0x32,
    'control':
        macro('alumacro', rx=0, ry=2, afnc = 'XOR',latchflag = False) + \
        macro('alumacro', rx=2, ry=0, afnc = 'XOR',latchflag = False) + \
        macro('alumacro', rx=0, ry=2, afnc = 'XOR',latchflag = False)
    },

    {'name':'SWAP R1,R3','bytecode': 0x37,
    'control':
        macro('alumacro', rx=1, ry=3, afnc = 'XOR',latchflag = False) + \
        macro('alumacro', rx=3, ry=1, afnc = 'XOR',latchflag = False) + \
        macro('alumacro', rx=1, ry=3, afnc = 'XOR',latchflag = False)
    },

    {'name':'MOVIR0','bytecode': 0x40,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLk'},

    ]},

    {'name':'MOVIR1','bytecode': 0x41,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLk','k0'},
    ]},

    {'name':'MOVIR2','bytecode': 0x42,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLk','k1'},
    ]},
    {'name':'MOVIR3','bytecode': 0x43,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLk','k0','k1'},
    ]},



    # XORI TODO

    {'name':'TODO XORIR0','bytecode': 0x44,
    'control':
        macro('aluimmediatemacro', rx=0, afnc = 'XOR',latchflag = True)
    },
    {'name':'TODO XORIR1','bytecode': 0x45,
    'control':
        macro('aluimmediatemacro', rx=1, afnc = 'XOR',latchflag = True)
    },
    {'name':'TODO XORIR2','bytecode': 0x46,
    'control':
        macro('aluimmediatemacro', rx=2, afnc = 'XOR',latchflag = True)
    },
    {'name':'TODO XORIR3','bytecode': 0x47,
    'control':
        macro('aluimmediatemacro', rx=3, afnc = 'XOR',latchflag = True)
    },

    # OPCODES 0x48 to 0x4f are unused



    # 0x50 other Logic immediate functions

    {'name':'ADDI R0,','bytecode': 0x50,
    'control':
    [
        {'Ep','nLm'},       # Place PC into MAR
        {'Cp','nCE','nLb'}, # inc PC next memory byte into B
        {'Ek','nLa'},       # R0-->A
        {'nLk','Eu','Lf'}   # ALU funcion 0 (add) - Results into R0, latch flag REG
    ]},

    {'name':'ADDI R1,','bytecode': 0x51,
    'control':
    [
        {'Ep','nLm'},       # Place PC into MAR
        {'Cp','nCE','nLb'}, # inc PC next memory byte into B
        {'Ek','nLa','f0'},       # R1-->A
        {'nLk','k0','Eu','Lf'}   # ALU funcion 0 (add) - Results into R0, latch flag REG
    ]},

    {'name':'ADDI R2,','bytecode': 0x52,
    'control':
    [
        {'Ep','nLm'},       # Place PC into MAR
        {'Cp','nCE','nLb'}, # inc PC next memory byte into B
        {'Ek','nLa','f1'},       # R2-->A
        {'nLk','k1','Eu','Lf'}   # ALU funcion 0 (add) - Results into R0, latch flag REG
    ]},

    {'name':'ADDI R3,','bytecode': 0x53,
    'control':
    [
        {'Ep','nLm'},       # Place PC into MAR
        {'Cp','nCE','nLb'}, # inc PC next memory byte into B
        {'Ek','nLa','f1','f0'},       # R3-->A
        {'nLk','k1','k0','Eu','Lf'}   # ALU funcion 0 (add) - Results into R0, latch flag REG
    ]},


    # Subtract - Same as Add but with 'Su' line set when using ALU


    {'name':'SUBI R0,','bytecode': 0x54,
    'control':
    [
        {'Ep','nLm'},       # Place PC into MAR
        {'Cp','nCE','nLb'}, # inc PC next memory byte into B
        {'Ek','nLa'},       # R0-->A
        {'nLk','Eu','Su','Lf'}   # ALU funcion 0 (add) - Results into R0, latch flag REG
    ]},

    {'name':'SUBI R1,','bytecode': 0x55,
    'control':
    [
        {'Ep','nLm'},       # Place PC into MAR
        {'Cp','nCE','nLb'}, # inc PC next memory byte into B
        {'Ek','nLa','f0'},       # R1-->A
        {'nLk','k0','Eu','Su','Lf'}   # ALU funcion 0 (add) - Results into R0, latch flag REG
    ]},

    {'name':'SUBI R2,','bytecode': 0x56,
    'control':
    [
        {'Ep','nLm'},       # Place PC into MAR
        {'Cp','nCE','nLb'}, # inc PC next memory byte into B
        {'Ek','nLa','f1'},       # R2-->A
        {'nLk','k1','Eu','Su','Lf'}   # ALU funcion 0 (add) - Results into R0, latch flag REG
    ]},

    {'name':'SUBI R3,','bytecode': 0x57,
    'control':
    [
        {'Ep','nLm'},       # Place PC into MAR
        {'Cp','nCE','nLb'}, # inc PC next memory byte into B
        {'Ek','nLa','f1','f0'},       # R3-->A
        {'nLk','k1','k0','Eu','Su','Lf'}   # ALU funcion 0 (add) - Results into R0, latch flag REG
    ]},


    # ANDI base 0x58 (0x58, 0x59, 0x5a, 0x5b)

    {'name':'TOTEST ANDI R0','bytecode': 0x58,
    'control':
        macro('aluimmediatemacro', rx=0, afnc = 'AND',latchflag = True)
    },
    {'name':'TOTEST ANDI R0','bytecode': 0x59,
    'control':
        macro('aluimmediatemacro', rx=1, afnc = 'AND',latchflag = True)
    },
    {'name':'TOTEST ANDI R0','bytecode': 0x5a,
    'control':
        macro('aluimmediatemacro', rx=2, afnc = 'AND',latchflag = True)
    },
    {'name':'TOTEST ANDI R0','bytecode': 0x5b,
    'control':
        macro('aluimmediatemacro', rx=3, afnc = 'AND',latchflag = True)
    },

    # ORI base 0x5C (0x5c, 0x5d, 0x5e, 0x5f)

    {'name':'TOTEST ORI R0','bytecode': 0x5c,
    'control':
        macro('aluimmediatemacro', rx=0, afnc = 'OR',latchflag = True)
    },
    {'name':'TOTEST ORI R1','bytecode': 0x5d,
    'control':
        macro('aluimmediatemacro', rx=1, afnc = 'OR',latchflag = True)
    },
    {'name':'TOTEST ORI R2','bytecode': 0x5e,
    'control':
        macro('aluimmediatemacro', rx=2, afnc = 'OR',latchflag = True)
    },
    {'name':'TOTEST ORI R3','bytecode': 0x5f,
    'control':
        macro('aluimmediatemacro', rx=3, afnc = 'OR',latchflag = True)
    },


    # XORI is found at base 0x44!




    # Jumping and conditional Jumping

    {'name':'DJNZ R0','bytecode': 0x60,
    'control':
    [
        {'Ek','nLa'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Su','Lf','nLk'},

        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0'},        # Enable both bytes of 2 address reg Write to PC if condition true
                                #f0 = 1 means NZ check on condition
    ]},

    {'name':'DJNZ R1','bytecode': 0x61,
    'control':
    [
        {'Ek','nLa','f0'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Su','Lf','nLk','k0'},

        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0'},        # Enable both bytes of 2 address reg Write to PC if condition true
                                #f0 = 1 means NZ check on condition
    ]},

    {'name':'DJNZ R2','bytecode': 0x62,
    'control':
    [
        {'Ek','nLa','f1'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Su','Lf','nLk','k1'},

        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0'},        # Enable both bytes of 2 address reg Write to PC if condition true
                                #f0 = 1 means NZ check on condition
    ]},

    {'name':'DJNZ R3','bytecode': 0x63,
    'control':
    [
        {'Ek','nLa','f1','f0'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Su','Lf','nLk','k1','k0'},

        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0'},        # Enable both bytes of 2 address reg Write to PC if condition true
                                #f0 = 1 means NZ check on condition
    ]},




    {'name':'JPZ NOT SUPPORTED!!','bytecode': 0x64,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp'},        # Enable both bytes of 2 address reg Write to PC if condition true
                            # f0,f1 bits select the condition
                            # f0,f1 = 00 current set to JPC
    ]},


    {'name':'JPNZ','bytecode': 0x65,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0'},        # Enable both bytes of 2 address reg Write to PC if condition true
        #f1f0 = 01 JPNZ  1
    ]},

    {'name':'JPC','bytecode': 0x66,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp'},        # Enable both bytes of 2 address reg Write to PC if condition true
                            # f0,f1 bits select the condition
        #f1f0 = 00 JPC  0

    ]},

    {'name':'JPNC','bytecode': 0x67,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f1'},    # Enable both bytes of 2 address reg Write to PC if condition true
                              # f0,f1 bits select the condition
        #f1f0 = 10 JPC  2

    ]},
    # JPS(0x68),JPNS(0x69), JPO(0x6a), JPNO(0x6b) not currently SUPPORTED

    {'name':'JMP','bytecode': 0x6c,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0','f1'},        # Enable both bytes of 2 address reg Write to PC if condition true
        #f1f0 = 11 JMP  3
    ]},

    #OP 0x6e is reserved (unused)

    {'name':'CALL ','bytecode': 0x6e, 'control':
    [

        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        # ASBUSLReg and ASBUSHReg contain place to jump -
        # all we do now is push the current value of PC onto the stack
        {'Ep','nLm','Sa','nLa','nLb'}, # Low byte of PC in A REG - High byte of PC in B REG

        # Now save A REG and B REG onto the Stack
        # A PUSH AB instruction!
        {'Cs'}, #DEC SP
        {'Es','nLm'}, # Place Stack address in MAR
        {'Ea','Lr','Cs'}, #Place Contents of R0 into RAM location pointing by MAR. also DEC SP
        {'Es','nLm'}, #  Load SP adress into MAR
        {'Eb','Lr'}, # Place contents of R1 into RAM location pointed by MAR

        # finally do the 'jump'

        {'E16','Lp','f0','f1'},        # Enable both bytes of 2 address reg Write to PC f0,f1 = 11 means it will JUMP


    ]},


    {'name':'RET ','bytecode': 0x6f, 'control':
    [

        {'Es','nLm'},
        {'nCE','nLah'},
        {'Cs','Us'},
        {'Es','nLm'},
        {'nCE','nLal','Cs','Us'},

        {'E16','Lp','f0','f1'}

    ]},

    # Shift Instructions 0x80

    {'name': 'SHR R0', 'bytecode':0x80,'control' :
            macro('alumacro', rx=0, afnc = 'SHR',latchflag = True)
    },
    {'name': 'SHR R1', 'bytecode':0x81,'control' :
            macro('alumacro', rx=1, afnc = 'SHR',latchflag = True)
    },
    {'name': 'SHR R2', 'bytecode':0x82,'control' :
            macro('alumacro', rx=2, afnc = 'SHR',latchflag = True)
    },
    {'name': 'SHR R3', 'bytecode':0x83,'control' :
            macro('alumacro', rx=3, afnc = 'SHR',latchflag = True)
    },

    {'name': 'SHL R0', 'bytecode':0x84,'control' :
            macro('alumacro', rx=0, afnc = 'SHL',latchflag = True)
    },
    {'name': 'SHL R1', 'bytecode':0x85,'control' :
            macro('alumacro', rx=1, afnc = 'SHL',latchflag = True)
    },
    {'name': 'SHL R2', 'bytecode':0x86,'control' :
            macro('alumacro', rx=2, afnc = 'SHL',latchflag = True)
    },
    {'name': 'SHL R3', 'bytecode':0x87,'control' :
            macro('alumacro', rx=3, afnc = 'SHL',latchflag = True)
    },


    # inc

    {'name':'INC R0','bytecode': 0x88,
    'control':
    [
        {'Ek','nLa'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Lf','nLk'},

    ]},

    {'name':'INC R1','bytecode': 0x89,
    'control':
    [
        {'Ek','nLa','f0'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Lf','nLk','k0'},

    ]},

    {'name':'INC R2','bytecode': 0x8a,
    'control':
    [
        {'Ek','nLa','f1'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Lf','nLk','k1'},

    ]},

    {'name':'INC R3','bytecode': 0x8b,
    'control':
    [
        {'Ek','nLa','f1','f0'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Lf','nLk','k0','k1'},

    ]},

    #

    {'name':'DEC R0','bytecode': 0x8c,
    'control':
    [
        {'Ek','nLa'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Su','Lf','nLk'}
    ]},

    {'name':'DEC R1','bytecode': 0x8d,
    'control':
    [
        {'Ek','nLa','f0'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Su','Lf','nLk','k0'}
    ]},

    {'name':'DEC R2','bytecode': 0x8e,
    'control':
    [
        {'Ek','nLa','f1'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Su','Lf','nLk','k1'}
    ]},

    {'name':'DEC R3','bytecode': 0x8f,
    'control':
    [
        {'Ek','nLa','f1','f0'},
        {'Ec','f0','nLb'},  # Constant 1 (Value is 1) on the bus, Save in B REG
        {'Eu','Su','Lf','nLk','k1','k0'}
    ]},



    # 'MOV Rx, Ry' -  Move into REGx the contents of REGy
    # Use Ek and f0,f1 combinations for the register you are reading
    # and 'nLk' with k0,k1 combinations for the register you are writing to.
    # {f1,f0}: b00 - R0, b01 - R1, b10 - R2, b11 - R3
    # {k1,k0}: b00 - R0, b01 - R1, b10 - R2, b11 - R3

    # R0 base 0x90
    {'name':'MOV R0,R0','bytecode': 0x90,
    'control':
    [
        {'Ek','nLk'},
    ]},

    {'name':'MOV R0,R1','bytecode': 0x91,
    'control':
    [
        {'Ek','f0','nLk'},
    ]},

    {'name':'MOV R0,R2','bytecode': 0x92,
    'control':
    [
        {'Ek','f1','nLk'},
    ]},

    {'name':'MOV R0,R3','bytecode': 0x93,
    'control':
    [
        {'Ek','f1','f0','nLk'},
    ]},

    # R1 dest base 0x94
    {'name':'MOV R1,R0','bytecode': 0x94,
    'control':
    [
        {'Ek','nLk','k0'},
    ]},

    {'name':'MOV R1,R1','bytecode': 0x95,
    'control':
    [
        {'Ek','nLk','k0','f0'},
    ]},

    {'name':'MOV R1,R2','bytecode': 0x96,
    'control':
    [
        {'Ek','nLk','k0','f1'},
    ]},

    {'name':'MOV R1,R3','bytecode': 0x97,
    'control':
    [
        {'Ek','nLk','k0','f1','f0'},
    ]},


    # R2 dest
    {'name':'MOV R2,R0','bytecode': 0x98,
    'control':
    [
        {'Ek','nLk','k1'},
    ]},

    {'name':'MOV R2,R1','bytecode': 0x99,
    'control':
    [
        {'Ek','nLk','k1','f0'},
    ]},

    {'name':'MOV R2,R2','bytecode': 0x9a,
    'control':
    [
        {'Ek','nLk','k1','f1'},
    ]},

    {'name':'MOV R2,R3','bytecode': 0x9b,
    'control':
    [
        {'Ek','nLk','k1','f1','f0'},
    ]},

    # R3 dest base 0x9c
    {'name':'MOV R3,R0','bytecode': 0x9c,
    'control':
    [
        {'Ek','nLk','k1','k0'},
    ]},

    {'name':'MOV R3,R1','bytecode': 0x9d,
    'control':
    [
        {'Ek','nLk','k1','k0','f0'},
    ]},

    {'name':'MOV R3,R2','bytecode': 0x9e,
    'control':
    [
        {'Ek','nLk','k1','k0','f1'},
    ]},

    {'name':'MOV R3,R3','bytecode': 0x9f,
    'control':
    [
        {'Ek','nLk','k1','k0','f1','f0'},
    ]},

    # R0 dest

    {'name':'ADD R0,R0','bytecode': 0xa0,
    'control':
    [
        {'Ek','nLa'},
        {'Ek','nLb'},
        {'nLk','Eu','Lf'}
    ]},

    {'name':'ADD R0,R1','bytecode': 0xa1,
    'control':
    [
        {'Ek','nLa'},
        {'Ek','f0','nLb'},
        {'nLk','Eu','Lf'}
    ]},

    {'name':'ADD R0,R2','bytecode': 0xa2,
    'control':
    [
        {'Ek','nLa'},
        {'Ek','f1','nLb'},
        {'nLk','Eu','Lf'}
    ]},

    {'name':'ADD R0,R3','bytecode': 0xa3,
    'control':
    [
        {'Ek','nLa'},
        {'Ek','f1','f0','nLb'},
        {'nLk','Eu','Lf'}
    ]},

    # R1 dest base 0xa4
    {'name':'ADD R1,R0','bytecode': 0xa4,
    'control':
    [
        {'Ek','f0','nLa'},
        {'Ek','nLb'},
        {'nLk','k0','Eu','Lf'}
    ]},

    {'name':'ADD R1,R1','bytecode': 0xa5,
    'control':
    [
        {'Ek','f0','nLa'},
        {'Ek','f0','nLb'},
        {'nLk','k0','Eu','Lf'}
    ]},
    {'name':'ADD R1,R2','bytecode': 0xa6,
    'control':
    [
        {'Ek','f0','nLa'},
        {'Ek','f1','nLb'},
        {'nLk','k0','Eu','Lf'}
    ]},
    {'name':'ADD R1,R3','bytecode': 0xa7,
    'control':
    [
        {'Ek','f0','nLa'},
        {'Ek','f1','f0','nLb'},
        {'nLk','k0','Eu','Lf'}
    ]},


    # R2 dest
    {'name':'ADD R2,R0','bytecode': 0xa8,
    'control':
    [
        {'Ek','f1','nLa'},
        {'Ek','nLb'},
        {'nLk','k1','Eu','Lf'}
    ]},

    {'name':'ADD R2,R1','bytecode': 0xa9,
    'control':
    [
        {'Ek','f1','nLa'},
        {'Ek','f0','nLb'},
        {'nLk','k1','Eu','Lf'}
    ]},
    {'name':'ADD R2,R2','bytecode': 0xaa,
    'control':
    [
        {'Ek','f1','nLa'},
        {'Ek','f1','nLb'},
        {'nLk','k1','Eu','Lf'}
    ]},
    {'name':'ADD R2,R3','bytecode': 0xab,
    'control':
    [
        {'Ek','f1','nLa'},
        {'Ek','f1','f0','nLb'},
        {'nLk','k1','Eu','Lf'}
    ]},



    # R3 dest base 0xac

    {'name':'ADD R3,R0','bytecode': 0xac,
    'control':
    [
        {'Ek','f1','f0','nLa'},
        {'Ek','nLb'},
        {'nLk','k1','k0','Eu','Lf'}
    ]},

    {'name':'ADD R3,R1','bytecode': 0xad,
    'control':
    [
        {'Ek','f1','f0','nLa'},
        {'Ek','f0','nLb'},
        {'nLk','k1','k0','Eu','Lf'}
    ]},
    {'name':'ADD R3,R2','bytecode': 0xae,
    'control':
    [
        {'Ek','f1','f0','nLa'},
        {'Ek','f1','nLb'},
        {'nLk','k1','k0','Eu','Lf'}
    ]},
    {'name':'ADD R3,R3','bytecode': 0xaf,
    'control':
    [
        {'Ek','f1','f0','nLa'},
        {'Ek','f1','f0','nLb'},
        {'nLk','k1','k0','Eu','Lf'}
    ]},



        # Sub R0 dest base 0xb0
        # @TODO TEST
        # R0 dest

        {'name':'SUB R0,R0','bytecode': 0xb0,
        'control':
        [
            {'Ek','nLa'},
            {'Ek','nLb'},
            {'nLk','Eu','Su','Lf'}
        ]},

        {'name':'SUB R0,R1','bytecode': 0xb1,
        'control':
        [
            {'Ek','nLa'},
            {'Ek','f0','nLb'},
            {'nLk','Eu','Su','Lf'}
        ]},

        {'name':'SUB R0,R2','bytecode': 0xb2,
        'control':
        [
            {'Ek','nLa'},
            {'Ek','f1','nLb'},
            {'nLk','Eu','Su','Lf'}
        ]},

        {'name':'SUB R0,R3','bytecode': 0xb3,
        'control':
        [
            {'Ek','nLa'},
            {'Ek','f1','f0','nLb'},
            {'nLk','Eu','Su','Lf'}
        ]},

        # R1 dest base 0xa4
        {'name':'SUB R1,R0','bytecode': 0xb4,
        'control':
        [
            {'Ek','f0','nLa'},
            {'Ek','nLb'},
            {'nLk','k0','Eu','Su','Lf'}
        ]},

        {'name':'SUB R1,R1','bytecode': 0xb5,
        'control':
        [
            {'Ek','f0','nLa'},
            {'Ek','f0','nLb'},
            {'nLk','k0','Eu','Su','Lf'}
        ]},
        {'name':'SUB R1,R2','bytecode': 0xb6,
        'control':
        [
            {'Ek','f0','nLa'},
            {'Ek','f1','nLb'},
            {'nLk','k0','Eu','Su','Lf'}
        ]},
        {'name':'SUB R1,R3','bytecode': 0xb7,
        'control':
        [
            {'Ek','f0','nLa'},
            {'Ek','f1','f0','nLb'},
            {'nLk','k0','Eu','Su','Lf'}
        ]},


        # R2 dest
        {'name':'SUB R2,R0','bytecode': 0xb8,
        'control':
        [
            {'Ek','f1','nLa'},
            {'Ek','nLb'},
            {'nLk','k1','Eu','Su','Lf'}
        ]},

        {'name':'SUB R2,R1','bytecode': 0xb9,
        'control':
        [
            {'Ek','f1','nLa'},
            {'Ek','f0','nLb'},
            {'nLk','k1','Eu','Su','Lf'}
        ]},
        {'name':'SUB R2,R2','bytecode': 0xba,
        'control':
        [
            {'Ek','f1','nLa'},
            {'Ek','f1','nLb'},
            {'nLk','k1','Eu','Su','Lf'}
        ]},
        {'name':'SUB R2,R3','bytecode': 0xbb,
        'control':
        [
            {'Ek','f1','nLa'},
            {'Ek','f1','f0','nLb'},
            {'nLk','k1','Eu','Su','Lf'}
        ]},



        # R3 dest base 0xac

        {'name':'SUB R3,R0','bytecode': 0xbc,
        'control':
        [
            {'Ek','f1','f0','nLa'},
            {'Ek','nLb'},
            {'nLk','k1','k0','Eu','Su','Lf'}
        ]},

        {'name':'SUB R3,R1','bytecode': 0xbd,
        'control':
        [
            {'Ek','f1','f0','nLa'},
            {'Ek','f0','nLb'},
            {'nLk','k1','k0','Eu','Su','Lf'}
        ]},
        {'name':'SUB R3,R2','bytecode': 0xbe,
        'control':
        [
            {'Ek','f1','f0','nLa'},
            {'Ek','f1','nLb'},
            {'nLk','k1','k0','Eu','Su','Lf'}
        ]},
        {'name':'SUB R3,R3','bytecode': 0xbf,
        'control':
        [
            {'Ek','f1','f0','nLa'},
            {'Ek','f1','f0','nLb'},
            {'nLk','k1','k0','Eu','Su','Lf'}
        ]},



        # Reg Logic AND Rx,Ry family base 0xc0

        {'name': 'AND R0,R0', 'bytecode':0xc0,'control' :
            macro('alumacro', rx=0, ry=0, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R0,R1', 'bytecode':0xc1,'control' :
            macro('alumacro', rx=0, ry=1, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R0,R2', 'bytecode':0xc2,'control' :
            macro('alumacro', rx=0, ry=2, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R0,R3', 'bytecode':0xc3,'control' :
            macro('alumacro', rx=0, ry=3, afnc = 'AND',latchflag = True)
        },

        {'name': 'AND R1,R0', 'bytecode':0xc4,'control' :
            macro('alumacro', rx=1, ry=0, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R1,R1', 'bytecode':0xc5,'control' :
            macro('alumacro', rx=1, ry=1, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R1,R2', 'bytecode':0xc6,'control' :
            macro('alumacro', rx=1, ry=2, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R1,R3', 'bytecode':0xc7,'control' :
            macro('alumacro', rx=1, ry=3, afnc = 'AND',latchflag = True)
        },


        {'name': 'AND R2,R0', 'bytecode':0xc8,'control' :
            macro('alumacro', rx=2, ry=0, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R2,R1', 'bytecode':0xc9,'control' :
            macro('alumacro', rx=2, ry=1, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R2,R2', 'bytecode':0xca,'control' :
            macro('alumacro', rx=2, ry=2, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R2,R3', 'bytecode':0xcb,'control' :
            macro('alumacro', rx=2, ry=3, afnc = 'AND',latchflag = True)
        },

        {'name': 'AND R3,R0', 'bytecode':0xcc,'control' :
            macro('alumacro', rx=3, ry=0, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R3,R1', 'bytecode':0xcd,'control' :
            macro('alumacro', rx=3, ry=1, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R3,R2', 'bytecode':0xce,'control' :
            macro('alumacro', rx=3, ry=2, afnc = 'AND',latchflag = True)
        },
        {'name': 'AND R3,R3', 'bytecode':0xcf,'control' :
            macro('alumacro', rx=3, ry=3, afnc = 'AND',latchflag = True)
        },




        # Reg Logic OR Rx,Ry family base 0xd0

        {'name': 'OR R0,R0', 'bytecode':0xd0,'control' :
            macro('alumacro', rx=0, ry=0, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R0,R1', 'bytecode':0xd1,'control' :
            macro('alumacro', rx=0, ry=1, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R0,R2', 'bytecode':0xd2,'control' :
            macro('alumacro', rx=0, ry=2, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R0,R3', 'bytecode':0xd3,'control' :
            macro('alumacro', rx=0, ry=3, afnc = 'OR',latchflag = True)
        },

        {'name': 'OR R1,R0', 'bytecode':0xd4,'control' :
            macro('alumacro', rx=1, ry=0, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R1,R1', 'bytecode':0xd5,'control' :
            macro('alumacro', rx=1, ry=1, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R1,R2', 'bytecode':0xd6,'control' :
            macro('alumacro', rx=1, ry=2, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R1,R3', 'bytecode':0xd7,'control' :
            macro('alumacro', rx=1, ry=3, afnc = 'OR',latchflag = True)
        },


        {'name': 'OR R2,R0', 'bytecode':0xd8,'control' :
            macro('alumacro', rx=2, ry=0, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R2,R1', 'bytecode':0xd9,'control' :
            macro('alumacro', rx=2, ry=1, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R2,R2', 'bytecode':0xda,'control' :
            macro('alumacro', rx=2, ry=2, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R2,R3', 'bytecode':0xdb,'control' :
            macro('alumacro', rx=2, ry=3, afnc = 'OR',latchflag = True)
        },

        {'name': 'OR R3,R0', 'bytecode':0xdc,'control' :
            macro('alumacro', rx=3, ry=0, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R3,R1', 'bytecode':0xdd,'control' :
            macro('alumacro', rx=3, ry=1, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R3,R2', 'bytecode':0xde,'control' :
            macro('alumacro', rx=3, ry=2, afnc = 'OR',latchflag = True)
        },
        {'name': 'OR R3,R3', 'bytecode':0xdf,'control' :
            macro('alumacro', rx=3, ry=3, afnc = 'OR',latchflag = True)
        },


        # Reg Logic XOR Rx,Ry family base 0xe0


        {'name': 'XOR R0,R0', 'bytecode':0xe0,'control' :
            macro('alumacro', rx=0, ry=0, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R0,R1', 'bytecode':0xe1,'control' :
            macro('alumacro', rx=0, ry=1, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R0,R2', 'bytecode':0xe2,'control' :
            macro('alumacro', rx=0, ry=2, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R0,R3', 'bytecode':0xe3,'control' :
            macro('alumacro', rx=0, ry=3, afnc = 'XOR',latchflag = True)
        },

        {'name': 'XOR R1,R0', 'bytecode':0xe4,'control' :
            macro('alumacro', rx=1, ry=0, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R1,R1', 'bytecode':0xe5,'control' :
            macro('alumacro', rx=1, ry=1, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R1,R2', 'bytecode':0xe6,'control' :
            macro('alumacro', rx=1, ry=2, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R1,R3', 'bytecode':0xe7,'control' :
            macro('alumacro', rx=1, ry=3, afnc = 'XOR',latchflag = True)
        },


        {'name': 'XOR R2,R0', 'bytecode':0xe8,'control' :
            macro('alumacro', rx=2, ry=0, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R2,R1', 'bytecode':0xe9,'control' :
            macro('alumacro', rx=2, ry=1, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R2,R2', 'bytecode':0xea,'control' :
            macro('alumacro', rx=2, ry=2, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R2,R3', 'bytecode':0xeb,'control' :
            macro('alumacro', rx=2, ry=3, afnc = 'XOR',latchflag = True)
        },

        {'name': 'XOR R3,R0', 'bytecode':0xec,'control' :
            macro('alumacro', rx=3, ry=0, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R3,R1', 'bytecode':0xed,'control' :
            macro('alumacro', rx=3, ry=1, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R3,R2', 'bytecode':0xee,'control' :
            macro('alumacro', rx=3, ry=2, afnc = 'XOR',latchflag = True)
        },
        {'name': 'XOR R3,R3', 'bytecode':0xef,'control' :
            macro('alumacro', rx=3, ry=3, afnc = 'XOR',latchflag = True)
        },


    {'name':'HLT','bytecode': 0xff,
    'control':
    [

    ]}

]


# Calculate the NOP microcode control word

def buildNOPControlWord():

    NOPWord = 0

    for cl in clLines:
        NOPWord |= (cl['active']^1)<<cl['bit']
    return NOPWord

def getControlLine(controlLineName):

    for cl in clLines:
        if (cl['key'] == controlLineName) or ('alias' in cl and controlLineName in cl['alias']):
            return cl
    raise Exception(f"Can not find defn for control line {controlLineName}")


def buildControlWord(controlList, NOPWord):

    controlWordMask = 0

    for clKey in controlList:
        cl = getControlLine(clKey)
        controlWordMask |= 1<<cl['bit']

    return controlWordMask ^ NOPWord

def checkInteg():

    bitcheck = 0 ;
    keySet = set()
    bytecodeSet = set()

    for cl in clLines:
        key = cl['key']

        if (key in keySet):
            raise Exception(f"Key {key} already defined for control line. Please check!")
        keySet.add(key)

        bitnum = 1<<cl['bit']
        if (bitnum & bitcheck != 0):
            raise Exception(f"Bit already defined for control line {cl['key']}. Please check!")
        bitcheck |= bitnum

    for op in opcodes:
        bytecode = op['bytecode']
        if (bytecode in bytecodeSet):
            raise Exception(f"ByteCode {bytecode} for opCode {op['name']} was already defined in the opcodes data. Please check!")
        bytecodeSet.add(bytecode)

def buildMicrocode():

    checkInteg()
    NOPWord = buildNOPControlWord()
    #print(f"NOP Word {NOPWord:06x}")
    for op in opcodes:
        #print(op)
        opSize = len(op['control'])
        op['tsize'] = opSize
        op['controlwords'] = []
        opcodeTable[op['bytecode']] = op

        #print()
        for tStateIndex,tStateCtrlst in enumerate(op['control']):
            op['controlwords'].append(buildControlWord(tStateCtrlst, NOPWord))
            #print(f"T{tStateIndex + 4} 0x{op['controlwords'][tStateIndex]:06x} {op['name']:6} 0x{op['bytecode']:01x}")
        #if (opSize < len(fetchControlWords)):
        #    op['controlwords'].append(NOPWord)
        #    op['tsize'] += 1

    return

# Useful for testing bits of our circuit

def produce32BitNOPROM(romName, raw = True):

    print("Producing 32bit Rom")

    file = open(romName, "w+")
    file.write("v2.0 raw\n")

    # 256*32 ops
    nopCntWord = buildNOPControlWord()

    for n in range(32*256):
        file.write(f"{nopCntWord:08x} ")
        if (n % 8 == 7):
            file.write("\n")

    file.close()

# Produce LogiSim memory file ROM/RAM  files
# from opcodes control word arrays.
# In this version - the 'Execute' control words proceed
# after the generic 'Fetch' control words
def produce32BitROMNEW(romName, raw = True):


    # Build up a couple of 'constants'

    nopCntWord = buildNOPControlWord()

    fetchWords = []
    for fmicrocode in fetchControlWords:
        fetchWords.append(buildControlWord(fmicrocode, nopCntWord))

    print(f"Producing 32bit Rom NOP {nopCntWord:08x}")

    file = open(romName, "w+")
    file.write("v2.0 raw\n")

    for bcode in range(256):
        bcodeExists = bcode in opcodeTable

        for word in fetchWords:
            file.write(f"{word:08x} ")

        remaining =  32 - len(fetchWords) -   (0 if not bcodeExists else len(opcodeTable[bcode]['controlwords']))

        if (bcode in opcodeTable):
            op = opcodeTable[bcode]

            for word in op['controlwords']:
                file.write(f"{word:08x} ")

        # Finish off trailing opcodes with NOPs
        for i in range(remaining):
            file.write(f"{nopCntWord:08x} ")

        file.write("\n")

    file.close()


# Produce LogiSim memory file ROM/RAM  files
# from opcodes control word arrays.
# In this version - the 'Execute' control words proceed
# after the generic 'Fetch' control words

def produce32BitROM(romName, raw = True):

    opcodes.sort(key=sortKey)
    nopCntWord = buildNOPControlWord()
    print(f"Producing 32bit Rom NOP {nopCntWord:08x}")

    file = open(romName, "w+")
    file.write("v2.0 raw\n" if raw else "v3.0 hex words addressed\n")

    fetchWords = []

    for fmicrocode in fetchControlWords:
        fetchWords.append(buildControlWord(fmicrocode, nopCntWord))

    # Now start producing ROM output
    address = 0
    lastbytecode = -1

    for op in opcodes:
        if (not raw):
            file.write(f"{address:02x}: ")

        bytecode = op['bytecode']
        #gap = bytecode - lastbytecode - 1
        #print(f"Filling in gap of {gap} opcodes")
        #if (gap > 0):
        #    for n in range(gap):
        #        file.write(f"Op Code {(lastbytecode + n + 1):02x}\n")
        #        for word in fetchWords:
        #            file.write(f"{word:08x} ")
#
#                remaining =  32 - len(fetchWords)
#
#                for i in range(remaining):
#                    file.write(f"{nopCntWord:08x} ")
            #print(f"{nopCntWord:06x} ", end = '')
#                address += 32

        #file.write(f"Op Code {op['bytecode']:02x}\n")
        for word in fetchWords:
            file.write(f"{word:08x} ")
            #print(f"{word:06x} ", end = '')

        for word in op['controlwords']:
            file.write(f"{word:08x} ")
            #print(f"{word:06x} ", end = '')

        remaining =  32 - len(fetchWords) -  len(op['controlwords'])

        for i in range(remaining):
            file.write(f"{nopCntWord:08x} ")
            #print(f"{nopCntWord:06x} ", end = '')
        address += 32
        lastbytecode = op['bytecode']

        file.write("\n")
        #print()
    file.close()

def produce8BitROM(romName, shift, raw = True):

    opcodes.sort(key=sortKey)
    print("Producing 8-bit Roms shift=",shift)

    file = open(romName, "w+")
    file.write("v2.0 raw\n" if raw else "v3.0 hex words addressed\n")

    fetchWords = []
    nopCntWord = buildNOPControlWord()

    for fmicrocode in fetchControlWords:
        fetchWords.append(buildControlWord(fmicrocode, nopCntWord))

    # Now start producing ROM output
    address = 0
    for op in opcodes:
        if (not raw):
            file.write(f"{address:02x}: ")

        for word in fetchWords:
            file.write(f"{((word>>shift) & 0xff) :02x} ")
            #print(f"{word:06x} ", end = '')

        for word in op['controlwords']:
            file.write(f"{((word>>shift) & 0xff) :02x} ")
            #print(f"{word:06x} ", end = '')

        remaining =  8 - len(fetchWords) -  len(op['controlwords'])

        for i in range(remaining):
            file.write(f"{((nopCntWord>>shift) & 0xff):02x} ")
            #print(f"{nopCntWord:06x} ", end = '')
        address += 8

        file.write("\n")
        #print()
    file.close()


def produceROMs(romType = 0, raw = True):
    #
    produce32BitROMNEW('microcode32bit.rom', raw)
    #produce32BitNOPROM('microcodeNOPs32bit.rom', raw)

    #produce8BitROM('microcode32bit-8bitrom-rom1.rom', 24,raw) # upper 8-bits
    #produce8BitROM('microcode32bit-8bitrom-rom2.rom', 16,raw) #middle 8-bits
    ##produce8BitROM('microcode32bit-8bitrom-rom3.rom', 8,raw) #bottom 8-bits
    #produce8BitROM('microcode32bit-8bitrom-rom4.rom', 0,raw) #bottom 8-bits



# opcodes.sort(reverse=True, key=myFunc)
def sortKey(e):

    return e['bytecode']

# Info only - does no real work
def listMicrocode():

    #opcodes.sort(key=sortKey)
    #accum = len(fetchControlWords)

    #for op in opcodes:
    #    op['wordoffset'] = accum
    #    accum += op['tsize']
    #    print(op)
    for bcode in range(256):
        if (bcode in opcodeTable):
            op = opcodeTable[bcode]
            print(op)



# Main Code

try:

    # DEBUG calculate Control Words for T1,T2,T3

    #NOPWord = buildNOPControlWord()

    #for tstateInd, dfn in enumerate(fetchControlWords):
    #    cw = buildControlWord(dfn,NOPWord)
        #print(f"T{tstateInd + 1:01d} controlword {cw:06x}")

    buildMicrocode()
    listMicrocode()
    produceROMs(romType = 0, raw = True)

except Exception as e:
    print(f"**ERROR** {e}")
