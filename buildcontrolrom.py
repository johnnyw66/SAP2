
controlWordSize = 32
ACTIVEHIGH = 1
ACTIVELOW = 0

# Definition for each of our control lines. We define which bit in the
# control word they occupy and if that control bit is active low or active high.


clLines = [
    {'key':"Cp", 'bit':31, 'active': ACTIVEHIGH, 'desc':"Enable PC count (inc PC)"},
    {'key':"Ep", 'bit':30, 'active': ACTIVEHIGH, 'desc':"Place PC onto the Bus"},
    {'key':"nLm", 'bit':29, 'active': ACTIVELOW, 'desc':"Load contents of Bus into Memory Address Reg"},
    {'key':"nCE", 'bit':28, 'active': ACTIVELOW, 'desc':"Place current data in RAM onto BUS"},

    {'key':"nLi", 'bit':27, 'active': ACTIVELOW, 'desc':"Load contents of Bus into the Instruction Reg"},
    {'key':"nEi", 'bit':26, 'active': ACTIVELOW, 'desc':"Place contents of the Instruction Reg onto the Bus"},
    {'key':"nLa", 'bit':25, 'active': ACTIVELOW, 'desc':"Load contents of the Bus into the A Reg"},
    {'key':"Ea",  'bit':24, 'active': ACTIVEHIGH, 'desc':"Place contents of the A Reg onto the BUS"},

    {'key':"Su",  'bit':23, 'active': ACTIVEHIGH, 'desc':"set ALU function to Subtract (otherwise it will be 'ADD')"},
    {'key':"Eu",  'bit':22, 'active': ACTIVEHIGH, 'desc':"Enable ALU (output directly to B Reg)"},
    {'key':"nLb", 'bit':21, 'active': ACTIVELOW, 'desc':"Load contents of B reg 'bus' into B Reg"},
    {'key':"nLo", 'bit':20, 'active': ACTIVELOW, 'desc':"Load contents of Bus into Output Reg"},

    {'key':"Lr",  'bit':19, 'active': ACTIVEHIGH, 'desc':"Load to RAM (STA op)"},
    {'key':"Lp",  'bit':18, 'active': ACTIVEHIGH, 'desc':"Load PC (JUMP instructions) used with f1 and f0"},
    {'key':"f1",  'bit':17, 'active': ACTIVEHIGH, 'desc':"JUMP condition function bit 1"},
    {'key':"f0",  'bit':16, 'active': ACTIVEHIGH, 'desc':"JUMP condition Function bit 0 {00 -> Carry, 01 -> Non Zero, 10 -> Parity Odd, 11 --> Always}"},
#    {'key':"Cp", 'bit':7, 'active': ACTIVEHIGH, 'desc':"TEST DUP"},

#
    # Free control lines for use later
    {'key':"nLal",  'bit':15, 'active': ACTIVELOW,'desc':"Load low byte of address with contents on DBUS"},
    {'key':"nLah",  'bit':14, 'active': ACTIVELOW, 'desc':"Load high byte of address with contents on DBUS"},
    {'key':"E16",  'bit':13, 'active': ACTIVEHIGH, 'desc':"Show DBUS<->ABUS regsiters (two) on Address Bus"},
    {'key':"Lf",  'bit':12, 'active': ACTIVEHIGH, 'desc':"Latch Flag Register"},

    {'key':"U4",  'bit':11, 'active': ACTIVEHIGH,'desc':"Some Decription"},
    {'key':"U5",  'bit':10, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U6",  'bit':9, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U7",  'bit':8, 'active': ACTIVEHIGH, 'desc':"Some Decription"},

    {'key':"U8",  'bit':7, 'active': ACTIVEHIGH,'desc':"Some Decription"},
    {'key':"U9",  'bit':6, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U10",  'bit':5, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U11",  'bit':4, 'active': ACTIVEHIGH, 'desc':"Some Decription"},

    {'key':"U12",  'bit':3, 'active': ACTIVEHIGH,'desc':"Some Decription"},
    {'key':"U13",  'bit':2, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U14",  'bit':1, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"dbg",  'bit':0, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
]
# Every microprocessor opcode instruction will have the
# same three controlwords for T1,T2 and T3,
# defined below
fetchControlWords = [{'Ep','nLm'},{'Cp'},{'nCE','nLi'}]



# Definition for each opcode in our microprocessor. We need to define
# those control lines which are active in each cycle.
# Note: The first three cycles T1, T2, T3
# are already defined in our 'fetchControlWords' array.
#    {'name':'LDI','bytecode': 0x6,
#    'control':
#    [
#        {'Ep','nLm'},
#        {'Cp','nCE','nLa'}
#    ]},

opcodes = [

    {'name':'LDA','bytecode': 0x00, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)
        {'nCE','nLa'}         # Finally Write the contents of the current address in MAR to A reg
    ]},


    {'name':'STA','bytecode': 0x01, 'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','nLm'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)

        {'Ea','Lr'}         # Finally Write the contents of A reg to the current address in MAR.
    ]},


    {'name':'ADD','bytecode': 0x02,
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

    {'name':'SUB','bytecode': 0x03,
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




    {'name':'JMP','bytecode': 0x04,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0','f1'},        # Enable both bytes of 2 address reg Write to PC if condition true
    ]},


    {'name':'JPNZ','bytecode': 0x05,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Ep','nLm'},
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'E16','Lp','f0'},        # Enable both bytes of 2 address reg Write to PC if condition true
    ]},

    {'name':'LDI','bytecode': 0x06,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLa'},

    ]},


    {'name':'SUBI','bytecode': 0x07,
    'control':
    [
        {'dbg'},
        {'Ep','nLm'},
        {'Cp','nCE','nLb'},
        {'nLa','Eu','Su','Lf'}
    ]},

    {'name':'OUT','bytecode': 0x08,
    'control':
    [
        {'Ea','nLo'},
    ]},



    {'name':'NOP','bytecode': 0x20, 'control':
    [
    ]},

    {'name':'HLT','bytecode': 0xff,
    'control':
    [

    ]}

]

opcodesOld = [

    {'name':'LDA','bytecode': 0, 'control':
    [
        {'Cp','nCE','nLal'},  # inc pc to point to high byte of address
        {'Cp','nCE','nLah'},  # inc pc to point to next opcode instruction
        {'nLm','E16'},        # Enable both bytes of 2 address reg Write to Memory Address Reg (MAR)
        {'nCE','nLa'}
    ]},

    {'name':'ADD','bytecode': 0x1,
    'control':
    [
        {'nLm','nEi'},
        {'nCE','nLb'},
        {'nLa','Eu'}
    ]},

    {'name':'SUB','bytecode': 0x2,
    'control':
    [
        {'nLm','nEi'},
        {'nCE','nLb'},
        {'nLa','Eu','Su'}
    ]},



    {'name':'STA','bytecode': 0x3,
    'control':
    [
        {'nLm','nEi'},
        {'Ea','Lr'}
    ]},

    {'name':'JMP','bytecode': 0x4,
    'control':
    [
        {'Lp','f0','f1'}
    ]},

    {'name':'JPNZ','bytecode': 0x5,
    'control':
    [
        {'Lp','f0'}
    ]},

    {'name':'LDI','bytecode': 0x6,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLa'}
    ]},

    {'name':'ADDI','bytecode': 0x7,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLb'},
        {'nLa','Eu'}

    ]},

    {'name':'SUBI','bytecode': 0x8,
    'control':
    [
        {'Ep','nLm'},
        {'Cp','nCE','nLb'},
        {'nLa','Eu','Su'}
    ]},

    {'name':'NOP','bytecode': 0x9,
    'control':
    [
    ]},

    {'name':'NOP1','bytecode': 0xa,
    'control':
    [
    ]},

    {'name':'NOP2','bytecode': 0xb,
    'control':
    [
    ]},

    {'name':'NOP3','bytecode': 0xc,
    'control':
    [
    ]},

    {'name':'NOP4','bytecode': 0xd,
    'control':
    [
    ]},

    {'name':'OUT','bytecode': 0xe,
    'control':
    [
        {'Ea','nLo'},
    ]},

    {'name':'HLT','bytecode': 0xf,
    'control':
    [

    ]},

]

# Calculate the NOP microcode control word

def buildNOPControlWord():

    NOPWord = 0

    for cl in clLines:
        NOPWord |= (cl['active']^1)<<cl['bit']
    return NOPWord

def getControlLine(controlLineName):

    for cl in clLines:
        if (cl['key'] == controlLineName):
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

    for cl in clLines:
        key = cl['key']
        if (key in keySet):
            raise Exception(f"Key {key} already defined for control line. Please check!")
        keySet.add(key)

        bitnum = 1<<cl['bit']
        if (bitnum & bitcheck != 0):
            raise Exception(f"Bit already defined for control line {cl['key']}. Please check!")
        bitcheck |= bitnum

def buildMicrocode():

    checkInteg()
    NOPWord = buildNOPControlWord()
    #print(f"NOP Word {NOPWord:06x}")
    for op in opcodes:
        #print(op)
        opSize = len(op['control'])
        op['tsize'] = opSize
        op['controlwords'] = []
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
    produce32BitROM('microcode32bit.rom', raw)
    produce32BitNOPROM('microcodeNOPs32bit.rom', raw)

    produce8BitROM('microcode32bit-8bitrom-rom1.rom', 24,raw) # upper 8-bits
    produce8BitROM('microcode32bit-8bitrom-rom2.rom', 16,raw) #middle 8-bits
    produce8BitROM('microcode32bit-8bitrom-rom3.rom', 8,raw) #bottom 8-bits
    produce8BitROM('microcode32bit-8bitrom-rom4.rom', 0,raw) #bottom 8-bits



# opcodes.sort(reverse=True, key=myFunc)
def sortKey(e):

    return e['bytecode']

def listMicrocode():

    opcodes.sort(key=sortKey)
    accum = len(fetchControlWords)

    for op in opcodes:
        op['wordoffset'] = accum
        accum += op['tsize']
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
