
controlWordSize = 24
ACTIVEHIGH = 1
ACTIVELOW = 0

# Definition for each of our control lines. We define which bit in the
# control word they occupy and if that control bit is active low or active high.


clLines = [
    {'key':"Cp", 'bit':23, 'active': ACTIVEHIGH, 'desc':"Enable PC count (inc PC)"},
    {'key':"Ep", 'bit':22, 'active': ACTIVEHIGH, 'desc':"Place PC onto the Bus"},
    {'key':"nLm", 'bit':21, 'active': ACTIVELOW, 'desc':"Load contents of Bus into Memory Address Reg"},
    {'key':"nCE", 'bit':20, 'active': ACTIVELOW, 'desc':"Place current data in RAM onto BUS"},

    {'key':"nLi", 'bit':19, 'active': ACTIVELOW, 'desc':"Load contents of Bus into the Instruction Reg"},
    {'key':"nEi", 'bit':18, 'active': ACTIVELOW, 'desc':"Place contents of the Instruction Reg onto the Bus"},
    {'key':"nLa", 'bit':17, 'active': ACTIVELOW, 'desc':"Load contents of the Bus into the A Reg"},
    {'key':"Ea",  'bit':16, 'active': ACTIVEHIGH, 'desc':"Place contents of the A Reg onto the BUS"},

    {'key':"Su",  'bit':15, 'active': ACTIVEHIGH, 'desc':"set ALU function to Subtract (otherwise it will be 'ADD')"},
    {'key':"Eu",  'bit':14, 'active': ACTIVEHIGH, 'desc':"Enable ALU (output directly to B Reg)"},
    {'key':"nLb", 'bit':13, 'active': ACTIVELOW, 'desc':"Load contents of B reg 'bus' into B Reg"},
    {'key':"nLo", 'bit':12, 'active': ACTIVELOW, 'desc':"Load contents of Bus into Output Reg"},

    {'key':"Lr",  'bit':11, 'active': ACTIVEHIGH, 'desc':"Load to RAM (STA op)"},
    {'key':"Lp",  'bit':10, 'active': ACTIVEHIGH, 'desc':"Load PC (JUMP instructions) used with f1 and f0"},
    {'key':"f1",  'bit':9, 'active': ACTIVEHIGH, 'desc':"JUMP condition function bit 1"},
    {'key':"f0",  'bit':8, 'active': ACTIVEHIGH, 'desc':"JUMP condition Function bit 0 {00 -> Carry, 01 -> Non Zero, 10 -> Parity Odd, 11 --> Always}"},
#    {'key':"Cp", 'bit':7, 'active': ACTIVEHIGH, 'desc':"TEST DUP"},

#
    # Free control lines for use later
    #{'key':"U0",  'bit':7, 'active': ACTIVEHIGH,'desc':"Some Decription"},
    {'key':"U1",  'bit':6, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U2",  'bit':5, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U3",  'bit':4, 'active': ACTIVEHIGH, 'desc':"Some Decription"},

    {'key':"U4",  'bit':3, 'active': ACTIVEHIGH,'desc':"Some Decription"},
    {'key':"U5",  'bit':2, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U6",  'bit':1, 'active': ACTIVEHIGH, 'desc':"Some Decription"},
    {'key':"U7",  'bit':0, 'active': ACTIVEHIGH, 'desc':"Some Decription"},

]
# Every microprocessor opcode instruction will have the
# same three controlwords for T1,T2 and T3,
# defined below
fetchControlWords = [{'Ep','nLm'},{'Cp'},{'nCE','nLi'}]



# Definition for each opcode in our microprocessor. We need to define
# those control lines which are active in each cycle.
# Note: The first three cycles T1, T2, T3
# are already defined in our 'fetchControlWords' array.

opcodes = [

    {'name':'LDA','bytecode': 0, 'control':
    [
        {'nLm','nEi'},
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


# Produce LogiSim memory file ROM/RAM  files
# from opcodes control word arrays.
# In this version - the 'Execute' control words proceed
# after the generic 'Fetch' control words

def produce24BitROM(romName, raw = True):

    opcodes.sort(key=sortKey)
    print("Producing 24bit Rom")

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
            file.write(f"{word:06x} ")
            #print(f"{word:06x} ", end = '')

        for word in op['controlwords']:
            file.write(f"{word:06x} ")
            #print(f"{word:06x} ", end = '')

        remaining =  8 - len(fetchWords) -  len(op['controlwords'])

        for i in range(remaining):
            file.write(f"{nopCntWord:06x} ")
            #print(f"{nopCntWord:06x} ", end = '')
        address += 8

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
    produce24BitROM('microcode24bit.rom', raw)
    produce8BitROM('microcode24bit-8bitrom-rom1.rom', 16,raw) # upper 8-bits
    produce8BitROM('microcode24bit-8bitrom-rom2.rom', 8,raw) #middle 8-bits
    produce8BitROM('microcode24bit-8bitrom-rom3.rom', 0,raw) #bottom 8-bits



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
