#!/usr/bin/env python3
import sys
import os.path
from enum import Enum
WSPACE = "\f\v\r\t\n "

class OutputType(Enum):
    BINARY = 0
    RAWHEX = 1
    ADDRESSEDHEX = 2


codeBuilder = {
    'mov' : {'build':'doubleRegSingleByteBuilder', 'bytecode':0x90},
    'movi' : {'build':'singleRegDoubleByteBuilder', 'bytecode':0x40},
    'movwi' : {'build':'threeByteBuilder', 'bytecode':0x1c},    # set SP to address -  instruction

    # Load/Store from/to Memory
    'ld' : {'build':'singleRegTripleByteBuilder', 'bytecode':0x14},
    'st' : {'build':'singleRegTripleByteBuilder', 'bytecode':0x18},

    'out' : {'build':'singleRegSingleByteBuilder','bytecode':0x10},
    'inc' : {'build':'singleRegSingleByteBuilder', 'bytecode':0x88},
    'dec' : {'build':'singleRegSingleByteBuilder','bytecode':0x8c},
    'decsp' : {'build':'singleByteBuilder','bytecode':0x1e},
    'incsp' : {'build':'singleByteBuilder', 'bytecode':0x1d},

    'pushr0' : {'build':'singleByteBuilder','bytecode':0x1f},
    'pushr2' : {'build':'singleByteBuilder','bytecode':0x20},
    'pushall' : {'build':'singleByteBuilder','bytecode':0x21},
    'popr0' : {'build':'singleByteBuilder','bytecode':0x22},
    'popr2' : {'build':'singleByteBuilder','bytecode':0x23},
    'popall' : {'build':'singleByteBuilder', 'bytecode':0x24},

    'shr' : {'build':'singleRegSingleByteBuilder','bytecode':0x80},
    'shl' : {'build':'singleRegSingleByteBuilder','bytecode':0x84},

    'add' : {'build':'doubleRegSingleByteBuilder', 'bytecode':0xa0},
    'sub' : {'build':'doubleRegSingleByteBuilder', 'bytecode':0xb0},
    'and' : {'build':'doubleRegSingleByteBuilder', 'bytecode':0xc0},
    'or' : {'build':'doubleRegSingleByteBuilder', 'bytecode':0xd0},
    'xor' : {'build':'doubleRegSingleByteBuilder', 'bytecode':0xe0},

    'addi' : {'build':'singleRegDoubleByteBuilder', 'bytecode':0x50},
    'subi' : {'build':'singleRegDoubleByteBuilder', 'bytecode':0x54},
    'andi' : {'build':'singleRegDoubleByteBuilder', 'bytecode':0x58},
    'ori' : {'build':'singleRegDoubleByteBuilder', 'bytecode':0x5c},
    'xori' : {'build':'singleRegDoubleByteBuilder', 'bytecode':0x44},


    'djnz' : {'build':'singleRegTripleByteBuilder', 'bytecode':0x60},
    'jpz' : {'build':'threeByteBuilder', 'bytecode':0x64},
    'jpnz' : {'build':'threeByteBuilder', 'bytecode':0x65},
    'jpc' : {'build':'threeByteBuilder', 'bytecode':0x66},
    'jpnc' : {'build':'threeByteBuilder', 'bytecode':0x67},

    'jps' : {'build':'threeByteBuilder', 'bytecode':0x68},
    'jpns' : {'build':'threeByteBuilder', 'bytecode':0x69},
    'jpo' : {'build':'threeByteBuilder', 'bytecode':0x6a},
    'jpno' : {'build':'threeByteBuilder', 'bytecode':0x6b},
    'jmp' : {'build':'threeByteBuilder', 'bytecode':0x6c},

    'call' : {'build':'threeByteBuilder', 'bytecode':0x6e},
    'ret' : {'build':'singleByteBuilder','bytecode':0x6f},

    'clc' : {'build':'singleByteBuilder','bytecode':0x01},
    'setc' : {'build':'singleByteBuilder','bytecode':0x02},

    'nop' : {'build':'singleByteBuilder','bytecode':0x00},
    'exx' : {'build':'singleByteBuilder','bytecode':0x25},
    'hlt' : {'build':'singleByteBuilder','bytecode':0xff},


    'org' : {'build':'nullBuilder'},
    'symbol' : {'build':'nullBuilder'},
    'comment' : {'build':'nullBuilder'},

    'db' : {'build':'dataBuilder','size':1},
    'dw' : {'build':'dataBuilder','size':2},
    'ds' : {'build':'dataBuilder','size':-1},
    'dt' : {'build':'stringBuilder','size':-1},
    'end' : {'build':'nullBuilder'},
}

class Builder:
    def __init__(self,symtable):
        self.symtable =  symtable
        self.cachewarning = set()


    def build(self, op):
        #print("BUILD ",op)
        return self.opCodeBuilder(op)

    def info(self,str,op):
            pass

    def warning(self, str, nm):
        if (nm not in self.cachewarning):
            print("**WARNING** "+str,nm)
            self.cachewarning.add(nm)

    def opCodeBuilder(self, op):

        nm = op['op']
        if (nm in codeBuilder):
            builderfnc = codeBuilder[nm]['build']
            try:
                return getattr(self,builderfnc)(op,codeBuilder[nm])
            except KeyError as e:
                self.warning(f"FAILED TO FIND INFO FOR OPCODE {nm}: {e}",nm)
                return  self.initByteArray(op)
            except AttributeError as e:
                self.warning(f"FAILED TO FIND BUILDER FOR OPCODE {nm} {e}",nm)
                return  self.initByteArray(op)
        self.warning("BUILDER NOT FOUND FOR ",nm)
        return  self.initByteArray(op)

    def stringBuilder(self, op, buildinfo):
        self.info("stringbuilder",op)
        bincode = [ord(_x) for _x in list(op['data'])]
        bincode.append(0)
        #assert(len(bincode) == op['size'],"See a code doctor - mismatch in size of data element")
        return bincode

    def dataBuilder(self, op, buildinfo):
        self.info("databuilder",op)
        bincode = self.initByteArray(op)
        nm = op['op']
        if (nm == 'db'):
            bincode[0] = op['data'] & 0xff
        if (nm == 'dw'):
            bincode[0] = op['data'] & 0xff
            bincode[1] = op['data']>>8 & 0xff
        return bincode

    def singleByteBuilder(self, op, buildinfo):
        self.info("singleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo['bytecode']
        return bincode

    def singleRegSingleByteBuilder(self, op, buildinfo):
        self.info("singleRegSingleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo['bytecode'] | op['reg']
        return bincode


    def singleRegDoubleByteBuilder(self, op, buildinfo):
        self.info("singleRegDoubleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo['bytecode'] | op['reg']
        bincode[1] = op['data']
        return bincode


    def singleRegTripleByteBuilder(self, op, buildinfo):
        self.info("singleRegTripleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo['bytecode'] | op['reg']
        # check if data is a 'symbol' - look up if needed
        dValue = op['data'] if isinstance(op['data'],int) else self.symtable[op['data']]

        bincode[1] = (dValue) & 0xff
        bincode[2] = (dValue>>8) & 0xff
        #print("singleRegTripleByteBuilder",op,bincode)
        return bincode


    def doubleRegSingleByteBuilder(self, op, buildinfo):
        self.info("doubleRegSingleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo['bytecode'] | (op['reg']<<2) | (op['regr']<<0)
        #print(f"{bincode[0]:02x}")
        return bincode


#   This probably needs to be rewritten - it's here just to handle
#   movwi sp,_16bitaddress instruction
    def threeByteBuilder(self, op, buildinfo):
        self.info("threeByteBuilder",op)

        bincode = self.initByteArray(op)
        bincode[0] = buildinfo['bytecode']

        dValue = op['data'] if isinstance(op['data'],int) else self.symtable[op['data']]

        bincode[1] = (dValue) & 0xff
        bincode[2] = (dValue>>8) & 0xff

        #print("threeByteBuilder",op,bincode)
        return bincode


    def nullBuilder(self, op, buildinfo):
        return [0] * 0

    def initByteArray(self, op):
        return [0] *  op['size']


class ParseError(Exception):
        def __init__(self,msg):
            self.msg = msg

        def __str__(self):
            return f"**ParseError**: <{self.msg}>"

class ParserDefinitionError(Exception):
        def __init__(self,msg):
            self.msg = msg

        def __str__(self):
            return f"**ParserError**: {self.msg}"

class ParserException(Exception):
        def __init__(self,msg):
            self.msg = msg

        def __str__(self):
            return f"**ParserException**: {self.msg}"

class BaseParser():

    def __init__(self):
        print("BaseParser __init__")
        #self.text = text
        #self.pos = 0
        #self.len = len(text)
        self._cache = dict()


    def __str__(self):
        return f"<{self.text}> pos:{self.pos} out of {self.len} current <{self.text[self.pos:]}>"

    def init(self,text):
        self.text = text
        self.pos = 0
        self.len = len(text)

    def start(self):
        raise ParserException('Abstract Function needs to overrriden')

    def parse(self):
        raise ParserException('Abstract Function needs to overrriden')

    def current(self):
        return self.text[self.pos:]

    def gobblewhitespace(self):
        while self.pos < self.len and self.text[self.pos] in WSPACE:
            self.pos += 1
        #print("gooble ended at ",self.pos,self.text[self.pos:])


#    def position(self):
#        print(self.pos, "out of ",self.len, "text", self.text)

    def eof(self):
        return self.pos == self.len

    def next(self):
        chars = [] ;
        self.gobblewhitespace()
        while self.pos < self.len and self.text[self.pos] not in WSPACE :
            chars.append(self.text[self.pos])
            self.pos += 1
        return ''.join(chars)

    def match(self,wantedtok):
        lentoken = len(wantedtok)
        nxt = self.text[self.pos:(self.pos + lentoken)]
        if (nxt != wantedtok):
            raise ParseError('COUND NOT MATCH')
        self.pos = self.pos + lentoken
        return nxt


    def wanted(self,wantedtok):
        try:
            return self.match(wantedtok)
        except Exception as e:
            return None

    def trymatch(self,*wantedtoks):
        self.gobblewhitespace()
        z = list(wantedtoks)
        z.sort(key = lambda e: len(e),reverse=True)
        #print(z)

        for tok in z:
            caughttok = self.wanted(tok)
            if (caughttok != None):
                self.gobblewhitespace()
                return caughttok

        return None


    def produceCharsPattern(self,pattern):

        wanted = set()

        # First scan for '//' and add the next character onto 'wanted' removing that character and '//'
        newarraypattern = []

        splt = pattern.split('//')
        newarraypattern += splt[0]

        for index,s in enumerate(splt):
            if (index > 0):
                if (len(s) > 0):
                    wanted.add(s[0])  # add delimited characters to our required set
                    newarraypattern += s[1:] # start to build up a pattern string without delimeters and their associated character

        #print("Completed",newarraypattern)

    #    for grp in pattern.split()
        newpattern = ''.join(newarraypattern)

        p = newpattern.split('-')

        for i in range(len(p) - 1):

            left = p[i][-1]
            right = p[i + 1][0]

            assert ord(left) < ord(right),f"Pattern order Problem with {left}-{right}"

            for a in range(ord(left),ord(right)+1):
                    wanted.add(chr(a))


        remaining = p[-1][1 if len(p) > 1 else 0:]

        for ch in remaining:
            wanted.add(ch)

        return ''.join(list(wanted))

    def peek_chars(self, pattern):
        try:
            return self.chars(pattern)
        except Exception as e:
            pass
            return None

    def chars(self, pattern, bump = True):
        #self.gobblewhitespace()
        if (pattern not in self._cache):
            self._cache[pattern] = self.produceCharsPattern(pattern)
        ch = self.text[self.pos]
        if ch in self._cache[pattern]:
            if (bump):
                self.pos += 1
            return ch
        raise ParserException(f"Parser.chars Expected {pattern} but got <{ch}>")



    def tryrules(self,*rules):
        self.gobblewhitespace()
        for rule in rules:
            try:
                rv = getattr(self, rule)()
                if (rv is not None):
                    return rv
            except Exception as e:
                print(f"EXCEPTION {e}")


class AssemblerParser(BaseParser):
    def __init__(self):
        super().__init__()

    def start(self):
        print("Start ")

    def parse(self,text):
        super().init(text)
        print("Parse ")
        #self.text = text
        #self.len = len(text)
        #self.pos = 0
        allops = []
        while (self.pos < self.len):
            rv = self.tryrules('comment','symbol','directive','instruction')
            if (rv is not None):
                allops.append(rv)
            if (rv is None):
                raise ParserException(f"Can not parse {self.text}")

            print("**Built Operation**",rv,self)

        return allops

    def comment(self):
        if self.peek_chars(';#'):
            data = self.text[self.pos:]
            self.pos = self.len + 1
            return {'op':'comment','data':data, 'size' : 0}

    def symbolstr(self):
        symbol = []
        ch = self.chars('A-Za-z0-9_')
        symbol.append(ch)

        while True:
            ch = self.peek_chars('A-Za-z0-9_')
            if (ch is None):
                break
            symbol.append(ch)

        return ''.join(symbol)


    def symbol(self):
        if (self.peek_chars(":")):
            str = self.symbolstr()
            return {'op':'symbol','data': str,'size':0}

    def directive(self):
        if (self.peek_chars(".")):
            return self.tryrules('org','end','db','dw','dt')

    def org(self):
        if (self.trymatch('org')):
            print("org",self)
            return {'op':'org', 'data': self.number(),'size':0}

    def end(self):
        if (self.trymatch('end')):
            return {'op':'end','size':0}

    def dw(self):
        if (self.trymatch('dw')):
            return {'op':'dw', 'data': self.number(),'size':2}

    def db(self):
        if (self.trymatch('db')):
            return {'op':'db', 'data': self.number(),'size':1}

    def dt(self):
        if (self.trymatch('dt')):
            strmatch = 'A-Za-z0-9_@ '
            astr = []
            self.chars("'")

            ch = self.chars(strmatch)
            astr.append(ch)

            while True:
                ch = self.peek_chars(strmatch)
                if (ch is None):
                    break
                astr.append(ch)

            self.chars("'")
            fstr = ''.join(astr)
            return {'op':'dt', 'data': fstr,'size':len(fstr) + 1}


    def instruction(self):
        return self.tryrules('movwi','intermediate8','reg8','ld','call','singlebyte','singleop','out','pushpop','djnz')

    def registers16(self):
            t = self.trymatch('sp')
            print("reg16",self,t)
            return t

    def singleop(self):
        op = self.trymatch('exx','pushall','popall','ret','nop','hlt','clc','setc')
        if (op is not None):
            return {'op': op, 'size':1}
        return None

    def out(self):
        op = self.trymatch('out','shl','shr')
        if (op is not None):
            reg = self.tryrules('registers')
            return {'op': op, 'reg':reg, 'size':1}
        return None

    def pushpop(self):
        op = self.trymatch('pop','push')
        if (op is not None):
            reg = self.tryrules('registers')
            return {'op': op+'r'+str(reg), 'reg':reg, 'size':1}
        return None

    def singlebyte(self):
        op = self.trymatch('inc','dec')
        if (op is not None):
            print('singlebyte',op,self)
            reg = self.tryrules('registers','registers16')
            return {'op': op if isinstance(reg,int) else op+reg, 'reg':reg, 'size':1}
        return None


    def djnz(self):
        op = self.trymatch('djnz')
        if (op is not None):
            reg = self.registers()
            self.chars(',')
            data = self.tryrules('number','symbolstr')
            return {'op': op, 'reg': reg,'data':data, 'size':3}
        return None

    def call(self):
        op = self.trymatch('call','jmp','jpz','jpnz','jpc','jpnc','jps','jpns','jpo','jpno')
        if (op is not None):
            data = self.tryrules('number','symbolstr')
            return {'op': op, 'data':data, 'size':3}
        return None

    def ld(self):
        op = self.trymatch('ld','st')
        if (op is not None):
            regl = self.tryrules('registers')
            self.chars(',')
            data = self.tryrules('number','symbolstr')
            return {'op': op, 'reg': regl, 'data':data, 'size':3}
        return None

    def movwi(self):
        op = self.trymatch('movwi')
        if (op is not None):
            regl = self.tryrules('registers16')
            self.chars(',')
            data = self.tryrules('number','symbolstr')
            return {'op': op, 'reg': regl, 'data':data, 'size':3}
        return None


    def registers(self):
        r = self.chars('rR')
        reg = self.chars('0-3')
        return int(reg)


    def number(self):
        num = self.tryrules('binarynumber','hexnumber','octalnumber','decnumber')
        return num



    def regreginstruction(self,opcode):
        rx = self.registers()
        self.chars(',')
        ry = self.registers()
        return {'op':opcode, 'reg':rx, 'regr': ry, 'size':1}

    def intermediate(self,opcode):
        rx = self.registers()
        self.chars(',')
        value = self.number()
        return {'op':opcode, 'reg':rx, 'data':value,'size':2}


    def reg8(self):
        m = self.trymatch('mov','add','sub','and','or','xor')
        if (m):
            return self.regreginstruction(m)
        return None

    def intermediate8(self):
        m = self.trymatch('movi','addi','subi','andi','ori','xori')
        if (m):
            return self.intermediate(m)
        return None

    def octalnumber(self):
        chars = []

        if (self.trymatch('0o')):
            chars.append('0')
            chars.append('o')
            chars.append(self.chars('0-7'))

            while True:
                char = self.peek_chars('0-7')
                if char is None:
                    break
                chars.append(char)
            return int(''.join(chars),8)


    def binarynumber(self):
        chars = []
        #v = self.trymatch('0b')
        if (self.trymatch('0b')):
            chars.append('0')
            chars.append('b')
            chars.append(self.chars('0-1'))
            while True:
                char = self.peek_chars('0-1')
                if char is None:
                    break
                chars.append(char)
            return int(''.join(chars),2)


    def hexnumber(self):
        chars = []

        if (self.trymatch('0x')):
            chars.append('0')
            chars.append('x')
            chars.append(self.chars('0-9A-Fa-f'))

            while True:
                char = self.peek_chars('0-9A-Fa-f')
                if char is None:
                    break
                chars.append(char)
            return int(''.join(chars),16)



    def decnumber(self):
        chars = []
        sgn = self.peek_chars('+//-')
        if sgn is not None:
            chars.append(sgn)

        chars.append(self.chars('0-9'))

        while True:
            ch = self.peek_chars('0-9')
            if ch is None:
                break
            chars.append(ch)

        return int(''.join(chars))




#p = MyParser(".dt 'Hello' ; xxx")
#p.parse()
#print(p.chars("0"))
#raise ParserDefinitionError("Some Parserdefintion Error")
#print(peekahead_chars('0-9'))

if __name__ == '__main__':

    class SyntaxError(Exception):
        def __init__(self, msg, pos):
            self.msg = msg
            self.pos = pos

        def __str__(self):
            return f'{self.msg} at line {self.pos}'



    def produceHexFile(binName,binarray):
        return produceRawHexFile(binName,binarray)

    def produceRawHexFile(binName,ops):

        file = open(binName, "w+")
        file.write("v2.0 raw\n")
        totalsize = 0
        bcnt = 0

        for op in ops:
            if op['size'] > 0:
                binarray = builder.build(op)
                totalsize += len(binarray)
                for index,bytecode in enumerate(binarray):
                    file.write(f"{bytecode:02x} ")
                    if (bcnt % 8 == 7):
                        file.write("\n")
                    bcnt += 1

        file.write("\n")
        file.close()
        return totalsize

    def produceBinFile(binName,ops):
        combinarray = []

        file = open(binName, "wb")

        for op in ops:
            binarray = builder.build(op)
            combinarray += binarray

        file.write(bytes(combinarray))
        file.close()
        return len(combinarray)


    def produceV3HexFile(binName,ops):

        file = open(binName, "w+")
        file.write("v3.0 hex words addressed\n")
        address = 0
        lastaddr = -1
        totalsize = 0

        for op in ops:
            address = op['pc']
            binarray = builder.build(op)
            sz = len(binarray)
            totalsize += sz

            if (sz > 0):
                diff = (address -lastaddr)
                if (diff > 0):
                    file.write(f"\n{address:04x}: ")
                for index,byteopcode in enumerate(binarray):
                    file.write(f"{byteopcode:02x} ")

                lastaddr = op['pc'] + sz



                #if (index % 8 == 7):
                #    file.write("\n")

        file.write("\n")
        file.close()
        return totalsize

    def processLabels(ops,labels):
        if (op['op'] == 'symbol'):
            labelnm = op['data']
            addr = op['pc']
            if (labelnm in labels):
                raise SyntaxError('Replicated label',op['line'])
            labels[labelnm] = addr


    def info(str,end=None):
        print(str,end='')


    def buildHelpText():
        return " Example: './assembler.py example.asm [options -v (verbose), -d (debug), -q (quiet), -s (symbol table)] -3 [default] addressed hex output -1 raw hex output -b binary output'"


    def handleCommandArgs(argv):
        options=set()
        file = None

        for index,arg in enumerate(argv):
            if (arg.startswith('-') and len(arg) > 1):
                options.add(arg[1])
            else:
                if (index > 0):
                    file = arg
                else:
                    assembler = arg

        return options,file,assembler



    # ** Main Process Starts here ***

    #print(f"Arguments count: {len(sys.argv)}")
    #for i, arg in enumerate(sys.argv):
    #    print(f"Argument {i:>6}: {arg}")
    options,sourceFilename,assembler = handleCommandArgs(sys.argv)

    try:

        if (sourceFilename is None):
            hText = buildHelpText()
            raise Exception(f"Source file is needed to assemble!\n{hText}")

        if (not os.path.isfile(sourceFilename)):
            raise Exception(f"Sourcefile '{sourceFilename}' does not exist.")

    except Exception as e:
        print(e)
        sys.exit(-1)

    outTypeBinary = 0
    outTypeRaw = 1
    outTypeAddr = 2

    parser = AssemblerParser()
    pc = 0
    line = 0
    code = []
    labels = {}
    errors = 0

    verbose ='v' in options
    debug = 'd' in options
    quiet = 'q' in options
    symtable = 's' in options
    help = 'h' in options
    outType  = OutputType.BINARY if 'b' in options else OutputType.RAWHEX if '1' in options else OutputType.ADDRESSEDHEX

    if (help):
        print(buildHelpText())
        sys.exit(0);

    if (not quiet):
        print(f"Trying to assemble '{sourceFilename}' verbose:{verbose}... quiet:{quiet} debug:{debug} symtable:{symtable}\n")

    asm = open(sourceFilename, "r")
    completed = False

    while not completed:
        try:

            text = asm.readline()
            if len(text) == 0:
                break
            line = line + 1
            ops = parser.parse(text.strip())
            # ops is an array of operation instructions - (in the case of 'label' followed by opcode instruction)
            if (ops is not None):
                for op in ops:
                    if (op is not None):
                        op['line'] = line
                        if (debug):
                            print(op)
                        code.append(op)
                        if (op['op'] == 'end'):
                            completed = True

        except KeyboardInterrupt:
            pass
        except (EOFError, SystemExit):
            break
        except IndexError as e:
            print(f'Index Error: {e} Line {line}')
            #break
        except (ParseError, ZeroDivisionError) as e:
            print(f'Parse Error: {e} Line {line} {text}')
            errors += 1

    # Parsing complete
    if (errors > 0):
        if (not quiet):
            print("Build Failed! See a Code Doctor. Quick!")
        sys.exit(-1)

    try:

        # Pre-process build a symbol address table
        for op in code:
            if (op['op'] == 'org'):
                pc = op['data']
            op['pc'] = pc
            pc += op['size']
            if (verbose):
                print(op)
            processLabels(op,labels)

        if (not quiet and symtable):
            info("Symbol Table:\n")
            for lbl in labels:
                info(f"\t'{lbl}': 0x{labels[lbl]:04x}\n")

        # Now build up binary version of our code
        builder = Builder(labels)
        binName = sourceFilename.split(".")[0] + (".bin" if outType == OutputType.BINARY else ".hex")

        if (not quiet):
            print(f"Producing LogiSym bin file '{binName}'")

        #size = produceHexFile(binName,code)
        #match optype:
        #    case OutputType.RAWHEX:
        #            print("RAWHEX")
        #            break
        #    case OutputType.BINARY:
        #            print("BINARY")
        #            break
        #    case OutputType.ADDRESSEDHEX:
        #            print("ADDRESSEDHEX")
        #            break
        #info(f"{outType}")
        if (outType == OutputType.BINARY):
            size = produceBinFile(binName, code)
        elif (outType == OutputType.RAWHEX):
            size = produceHexFile(binName, code)
        elif (outType == OutputType.ADDRESSEDHEX):
            size = produceV3HexFile(binName, code)
        else:
            pass

        #OutputType.RAWHEX
        #OutputType.BINARY
        #OutputType.ADDRESSEDHEX



        if (not quiet):
            print(f"\nSize: {size} bytes")
            print("complete.\n")

        sys.exit(0)
    except (SyntaxError) as e:
        print(f"Syntax Error {e}")
