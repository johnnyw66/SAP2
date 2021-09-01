#!/usr/bin/env python3
"""
    Assembler for the SAP2 Microprocessor

    Johnny Wilson, Sussex August 2021
    Works with the LogiSim Evolution microprocessor circuit sap2.circ
    See  https://github.com/johnnyw66/SAP2
    Simple program

    .org 0x8000
:start
        movwi sp,0xffff     ; set stack pointer
        call display
        hlt

:display
        mov r0,255
:nxt
        out r0
        djnz r0, nxt
        ret


    .end


"""
import sys
import os.path
from enum import Enum, auto
from dataclasses import dataclass
from abc import abstractmethod, ABC


WSPACE = "\f\v\r\t\n "
RAMADDRESS = 0x8000
class OutputType(Enum):
    BINARY = auto()
    RAWHEX = auto()
    ADDRESSEDHEX = auto()

# Building Output Support
class Data(ABC):
    def __init__(self,data):
        self.data = data

    def getRawData(self):
        return self.data

    @abstractmethod
    def getData(self):
        pass

    def __str__(self):
        return f"Raw data {self.data}"

    def __repr__(self):
        return f"<Raw data: {self.data}>"


class SymbolWordData(Data):

    def __init__(self, data, lookup):
        super().__init__(data)
        print(f"Symbol Data<{data}>",)
        self.lut = lookup

    def getData(self):
        value = self.lut[self.data]
        return [value & 0xff, value>>8 & 0xff]

    def __repr__(self):
        return f"SymbolWordData: {super().__str__()}"

class WordData(Data):

    def __init__(self, data):
        super().__init__(data)

    def getData(self):
        value = self.data
        return [value & 0xff, value>>8 & 0xff]

    def __repr__(self):
        return f"WordData: {super().__str__()}"

class ByteData(Data):

    def __init__(self, data):
        super().__init__(data)

    def getData(self):
        value = self.data
        return [value]

class StringData(Data):

    def __init__(self, data):
        super().__init__(data)

    def getData(self):
            pass



@dataclass
class SupportOperation:
    data : str = None
    reg : int = None
    regr : int = None

    def __str__(self):
        return f"reg:{self.reg}  regr:{self.regr} data:{self.data}"

class ByteCodeResolver(ABC):

    @abstractmethod
    def getByteCode(self,supportdata: SupportOperation) -> int:
        pass

class SimpleByteCodeResolver(ByteCodeResolver):
    def __init__(self, bytecode: int):
        self.bytecode = bytecode

    def getByteCode(self,support: SupportOperation) -> int:
        return self.bytecode



class LookupByteCodeResolver(ByteCodeResolver):
    def __init__(self, table):
        self.lut = table

    def getByteCode(self,support: SupportOperation) -> int:
        return self.lut[support.reg]



class ByteCodeBuilder(ABC):

    @abstractmethod
    def build_bytecode(self, support_data: SupportOperation) -> [int]:
        pass


class SingleRegByteCodeBuilder(ByteCodeBuilder):
    def __init__(self, basebyte_resolver):
        self.basebyte_resolver = basebyte_resolver

    def build_bytecode(self, support: SupportOperation) -> [int]:
        print(f"build_bytecode")
        self.basebyte_resolver(support)

class DoubleRegByteCodeBuilder(ByteCodeBuilder):
    def __init__(self, basebyte_resolver):
        self.basebyte_resolver = basebyte_resolver

    def build_bytecode(self, support: SupportOperation) -> [int]:
        print(f"xxxxDoubleRegByteCodeBuilder:build_bytecode Support Data {support}")
        print(f"DoubleRegByteCodeBuilder:build_bytecode byte code = {self.basebyte_resolver.getByteCode(support):02x}")
        base_code = self.basebyte_resolver.getByteCode(support)
        return [base_code | (support.reg<<2) | (support.regr)]

class TripleByteCodeBuilder(ByteCodeBuilder):
    def __init__(self, basebyte_resolver):
        self.basebyte_resolver = basebyte_resolver

    def build_bytecode(self, support: SupportOperation) -> [int]:
        print(f"build_bytecode")
        base_code = self.basebyte_resolver.getByteCode(support_data)
        return [base_code]  + support.data.getData()


@dataclass
class BuildOperation:
    build: str
    bytecode: int = None
    bytecode_builder: ByteCodeBuilder = None

codeBuilder2 = {
    'mov' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0x90)),
    'movwi' : TripleByteCodeBuilder(LookupByteCodeResolver({'sp':0x1c,'r0':0x1c, 'r2':0x1c})),    # set SP/R0R1/R2R3 to address -  instruction
}

codeBuilder = {
    'mov' : BuildOperation(build = 'doubleRegSingleByteBuilder', bytecode = 0x90),
    'movi' : BuildOperation(build = 'singleRegDoubleByteBuilder', bytecode = 0x40),
    'movwi' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x1c),    # set SP to address -  instruction

    # Load/Store from/to Memory
    'ld' : BuildOperation(build = 'singleRegTripleByteBuilder', bytecode = 0x14),
    'st' : BuildOperation(build = 'singleRegTripleByteBuilder', bytecode = 0x18),

    'out' : BuildOperation(build = 'singleRegSingleByteBuilder' , bytecode = 0x10),
    'inc' : BuildOperation(build = 'singleRegSingleByteBuilder', bytecode = 0x88),
    'dec' : BuildOperation(build = 'singleRegSingleByteBuilder' , bytecode = 0x8c),
    'decsp' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x1e),
    'incsp' : BuildOperation(build = 'singleByteBuilder', bytecode = 0x1d),

    'pushr0' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x1f),
    'pushr2' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x20),
    'pushall' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x21),
    'popr0' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x22),
    'popr2' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x23),
    'popall' : BuildOperation(build = 'singleByteBuilder', bytecode = 0x24),

    'shr' : BuildOperation(build = 'singleRegSingleByteBuilder' , bytecode = 0x80),
    'shl' : BuildOperation(build = 'singleRegSingleByteBuilder' , bytecode = 0x84),

    'add' : BuildOperation(build = 'doubleRegSingleByteBuilder', bytecode = 0xa0),
    'sub' : BuildOperation(build = 'doubleRegSingleByteBuilder', bytecode = 0xb0),
    'and' : BuildOperation(build = 'doubleRegSingleByteBuilder', bytecode = 0xc0),
    'or' : BuildOperation(build = 'doubleRegSingleByteBuilder', bytecode = 0xd0),
    'xor' : BuildOperation(build = 'doubleRegSingleByteBuilder', bytecode = 0xe0),

    'addi' : BuildOperation(build = 'singleRegDoubleByteBuilder', bytecode = 0x50),
    'subi' : BuildOperation(build = 'singleRegDoubleByteBuilder', bytecode = 0x54),
    'andi' : BuildOperation(build = 'singleRegDoubleByteBuilder', bytecode = 0x58),
    'ori' : BuildOperation(build = 'singleRegDoubleByteBuilder', bytecode = 0x5c),
    'xori' : BuildOperation(build = 'singleRegDoubleByteBuilder', bytecode = 0x44),


    'djnz' : BuildOperation(build = 'singleRegTripleByteBuilder', bytecode = 0x60),
    'jpz' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x64),
    'jpnz' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x65),
    'jpc' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x66),
    'jpnc' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x67),

    'jps' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x68),
    'jpns' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x69),
    'jpo' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x6a),
    'jpno' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x6b),
    'jmp' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x6c),

    'call' : BuildOperation(build = 'threeByteBuilder', bytecode = 0x6e),
    'ret' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x6f),

    'clc' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x01),
    'setc' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x02),

    'nop' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x00),
    'exx' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0x25),
    'hlt' : BuildOperation(build = 'singleByteBuilder' , bytecode = 0xff),


    'org' : BuildOperation(build = 'nullBuilder'),
    'symbol' : BuildOperation(build = 'nullBuilder'),
    'comment' : BuildOperation(build = 'nullBuilder'),

    'db' : BuildOperation(build = 'dataBuilder'),
    'dw' : BuildOperation(build = 'dataBuilder'),
    'ds' : BuildOperation(build = 'dataBuilder'),
    'dt' : BuildOperation(build = 'stringBuilder'),
    'end' : BuildOperation(build = 'nullBuilder'),
}


@dataclass
class AssemblerOperation:
    operation : str = None
    pc : int = None
    size : int = None
    data : str = None
    reg : int = None
    regr : int = None


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

    def opCodeBuilder(self, op: AssemblerOperation) -> [int]:
        nm = op.operation
        print("opCodeBuilder!!!!")
        if (nm in codeBuilder2):
            builder = codeBuilder2[nm]
            so = op
            print(f"{db.build_bytecode(so)}")



    def opCodeBuilder2(self, op: AssemblerOperation) -> [int]:

        nm = op.operation
        if (nm in codeBuilder):
            builderfnc = codeBuilder[nm].build
            try:
                return getattr(self,builderfnc)(op, codeBuilder[nm])
            except KeyError as e:
                self.warning(f"FAILED TO FIND INFO FOR OPCODE {nm}: {e}",nm)
                return  self.initByteArray(op)
            except AttributeError as e:
                self.warning(f"FAILED TO FIND BUILDER FOR OPCODE {nm} {e}",nm)
                return  self.initByteArray(op)
        self.warning("BUILDER NOT FOUND FOR ",nm)
        return  self.initByteArray(op)

    def stringBuilder(self, op: AssemblerOperation, buildinfo: BuildOperation) -> [int]:
        self.info("stringbuilder",op)
        return [ord(_x) for _x in (list(op.data) + [chr(0)])]



    def dataBuilder(self, op: AssemblerOperation, buildinfo: BuildOperation) -> [int]:
        self.info("databuilder",op)
        bincode = self.initByteArray(op)
        nm = op.operation
        if (nm == 'db'):
            bincode[0] = op.data & 0xff
        if (nm == 'dw'):
            bincode[0] = op.data & 0xff
            bincode[1] = op.data>>8 & 0xff
        return bincode

    def singleByteBuilder(self, op: AssemblerOperation, buildinfo: BuildOperation) -> [int]:
        self.info("singleByteBuilder", op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo.bytecode
        return bincode

    def singleRegSingleByteBuilder(self, op: AssemblerOperation, buildinfo: BuildOperation) -> [int]:
        self.info("singleRegSingleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo.bytecode | op.reg
        return bincode


    def singleRegDoubleByteBuilder(self, op: AssemblerOperation, buildinfo) -> [int]:
        self.info("singleRegDoubleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo.bytecode | op.reg
        bincode[1] = op.data
        return bincode


    def singleRegTripleByteBuilder(self, op: AssemblerOperation, buildinfo: BuildOperation) -> [int]:
        self.info("singleRegTripleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo.bytecode | op.reg

        # check if data is a 'symbol' - look up if needed
        # SMELLY
        dValue = op.data if isinstance(op.data,int) else self.symtable[op.data]

        bincode[1] = (dValue) & 0xff
        bincode[2] = (dValue>>8) & 0xff
        #print("singleRegTripleByteBuilder",op,bincode)
        return bincode


    def doubleRegSingleByteBuilder(self, op: AssemblerOperation, buildinfo: BuildOperation) -> [int]:
        self.info("doubleRegSingleByteBuilder",op)
        bincode = self.initByteArray(op)
        bincode[0] = buildinfo.bytecode | (op.reg<<2) | (op.regr<<0)
        #print(f"{bincode[0]:02x}")
        return bincode


#   This probably needs to be rewritten - it's here just to handle
#   movwi sp,_16bitaddress instruction
    def threeByteBuilder(self, op: AssemblerOperation, buildinfo: BuildOperation) -> [int]:
        self.info("threeByteBuilder",op)

        bincode = self.initByteArray(op)
        bincode[0] = buildinfo.bytecode

        #SMELLY
        dValue = op.data if isinstance(op.data,int) else self.symtable[op.data]

        bincode[1] = (dValue) & 0xff
        bincode[2] = (dValue>>8) & 0xff

        #print("threeByteBuilder",op,bincode)
        return bincode


    def nullBuilder(self, op: AssemblerOperation, buildinfo: BuildOperation) -> [int]:
        return [0] * 0

    def initByteArray(self, op: AssemblerOperation) -> [int]:
        return [0] *  op.size


class ParseError(Exception):
        def __init__(self,msg):
            self.msg = msg

        def __str__(self):
            return f"**ParseError**: <{self.msg}>"

class ParserDefinitionError(Exception):
        def __init__(self,msg):
            self.msg = msg

        def __str__(self):
            return f"**ParserDefinitionError**: {self.msg}"

class ParserException(Exception):
        def __init__(self,msg):
            self.msg = msg

        def __str__(self):
            return f"**ParserException**: {self.msg}"

class BaseParser(ABC):

    def __init__(self):
        self._cache = dict()

    def __str__(self):
        return f"<{self.text}> pos:{self.pos} out of {self.len} current <{self.text[self.pos:]}>"

    def init(self,text) -> None:
        self.text = text
        self.pos = 0
        self.len = len(text)

    @abstractmethod
    def start(self) -> None:
        raise ParserDefinitionError("Abstract Function 'start' needs to overrriden")

    @abstractmethod
    def parse(self) -> None:
        raise ParserDefinitionError("Abstract Function 'parse' needs to overrriden")

    def current(self) -> str:
        return self.text[self.pos:]

    def gobblewhitespace(self) -> None:
        while self.pos < self.len and self.text[self.pos] in WSPACE:
            self.pos += 1

    def eof(self) -> bool:
        return self.pos == self.len

    def next(self) -> str:
        chars = []
        self.gobblewhitespace()
        while self.pos < self.len and self.text[self.pos] not in WSPACE :
            chars.append(self.text[self.pos])
            self.pos += 1
        return ''.join(chars)

    def match(self, wantedtok: str) -> str:
        lentoken = len(wantedtok)
        nxt = self.text[self.pos:(self.pos + lentoken)]
        if (nxt != wantedtok):
            raise ParseError('COULD NOT MATCH')
        self.pos = self.pos + lentoken
        return nxt


    def wanted(self, wantedtok: str) -> str:
        try:
            return self.match(wantedtok)
        except ParseError as e:
            return None

    def trymatch(self,*wantedtoks) -> str:
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


    def produce_chars_pattern(self, pattern: str) -> str:

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

    def peek_chars(self, pattern: str) -> str:

        try:
            return self.chars(pattern)
        except ParserException as e:
            # We have not found a char match - so go back and check other rules/token matches
            return None
        except IndexError as e:
            # Arrived here from 'chars' function - 'ch = self.text[self.pos]'
            # -  exhausted parsing our current line of text
            return None

    def chars(self, pattern: str, bump: bool = True) -> str:

        if (pattern not in self._cache):
            self._cache[pattern] = self.produce_chars_pattern(pattern)
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
                print(f"tryrules:Tring Rule {rule}")
                rv = getattr(self, rule)()
                if (rv is not None):
                    print(f"FOUND ONE - RULE  {rule}-- Returning {rv}")
                    return rv
            except ParserException as e:
                pass




class AssemblerParser(BaseParser):
    def __init__(self):
        super().__init__()


    def parse(self, text):

        super().init(text)
        self.start()
        allops = []

        while (self.pos < self.len):

            rv = self.tryrules('comment','symbol','directive','instruction')
            if (rv is None):
                raise ParserException(f"Can not parse {self.text}")
            print(f"***Adding*** {rv} to list")
            allops.append(rv)

        return allops


    def start(self):
        # Set up anything else to do with parsing our syntax -
        # We don't need to do anything here - as code generation is very simple.
        # Symbols are handled by walking through our code operations - twice
        pass

    # Top rules

    def comment(self) -> AssemblerOperation:
        """If we spot a comment TOKEN - then save text up to EOL and finish off parsing the line"""
        if self.peek_chars(';#'):
            data = StringData(self.text[self.pos:])
            self.pos = self.len + 1
            return AssemblerOperation(operation = 'comment',data = data , size = 0)


    def symbol(self) -> AssemblerOperation:
        print("<><><><><><><><<>CHECKING FOR SYMBOL")
        if (self.peek_chars(":")):
            print("Symbol FOUND <><><>><><><><><>")

            str = self.symbolstr()
            return AssemblerOperation(operation = 'symbol', data = str,  size = 0)

    def directive(self) -> AssemblerOperation:
        if (self.peek_chars(".")):
            return self.tryrules('org','end','db','dw','ds','dt')



    def instruction(self) -> AssemblerOperation:
        return self.tryrules('movwi','intermediate8','reg8','ld',\
                            'call','singlebyte','singleop','out','pushpop','djnz')



    # Directive operations


    def org(self) -> AssemblerOperation:
        if (self.trymatch('org')):
            return AssemblerOperation(operation ='org', data = self.number(), size = 0)

    def end(self) -> AssemblerOperation:
        if (self.trymatch('end')):
            return AssemblerOperation(operation ='end', size = 0)

    def dw(self) -> AssemblerOperation:
        if (self.trymatch('dw')):
            return AssemblerOperation(operation = 'dw', data = self.number(), size = 2)

    def db(self) -> AssemblerOperation:
        if (self.trymatch('db')):
            return AssemblerOperation(operation = 'db', data = self.number8(), size = 1)

    def ds(self) -> AssemblerOperation:
        if (self.trymatch('ds')):
            return AssemblerOperation(operation = 'ds', data =  0, size = self.number())

    def dt(self) -> AssemblerOperation:
        if (self.trymatch('dt')):
            strmatch = 'A-Za-z0-9_@().!//-+# '
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
            return AssemblerOperation(operation = 'dt', data = StringData(fstr), size = len(fstr) + 1)


    # Instruction operations

    def movwi(self) -> AssemblerOperation:
        op = self.trymatch('movwi')
        if (op is not None):
            regl = self.tryrules('registers16')
            self.chars(',')
            print("GOT PASS COMMA")
            data = self.tryrules('number','symbolstr')
            print("DATA ",data)
            ao =  AssemblerOperation(operation = op, reg = regl, data = data, size = 3)
            print("GOT PASS DATA - AssemblerOperation = ",ao,self)

        return None


    def intermediate8(self) -> AssemblerOperation:
        m = self.trymatch('movi','addi','subi','andi','ori','xori')
        if (m):
            return self.intermediate(m)
        return None

    def reg8(self) -> AssemblerOperation:
        m = self.trymatch('mov','add','sub','and','or','xor')
        if (m):
            return self.regreginstruction(m)
        return None

    def ld(self) -> AssemblerOperation:
        op = self.trymatch('ld','st')
        if (op is not None):
            regl = self.tryrules('registers')
            self.chars(',')
            data = self.tryrules('number','symbolstr')
            return AssemblerOperation(operation = op, reg =  regl, data = data, size = 3)
        return None

    def call(self) -> AssemblerOperation:
        op = self.trymatch('call','jmp','jpz','jpnz','jpc',\
                            'jpnc','jps','jpns','jpo','jpno')
        if (op is not None):
            data = self.tryrules('number','symbolstr')
            return AssemblerOperation(operation = op, data = data, size = 3)
        return None


    def singlebyte(self) -> AssemblerOperation:
        op = self.trymatch('inc','dec')
        if (op is not None):
            reg = self.tryrules('registers','registers16')
            #SMELLY
            return AssemblerOperation(operation = op if isinstance(reg,int) else op+reg, reg = reg, size = 1)
        return None

    def singleop(self) -> AssemblerOperation:
        op = self.trymatch('exx','pushall','popall','ret',\
                            'nop','hlt','clc','setc')
        if (op is not None):
            return AssemblerOperation (operation = op, size = 1)
        return None

    def out(self) -> AssemblerOperation:
        op = self.trymatch('out','shl','shr')
        if (op is not None):
            reg = self.tryrules('registers')
            return AssemblerOperation(operation = op, reg = reg, size = 1)
        return None

    def pushpop(self) -> AssemblerOperation:
        op = self.trymatch('pop','push')
        if (op is not None):
            reg = self.tryrules('registers')
            return AssemblerOperation(operation = op+'r'+str(reg), reg = reg,  size = 1)
        return None



    def djnz(self) -> AssemblerOperation:
        op = self.trymatch('djnz')
        if (op is not None):
            reg = self.registers()
            self.chars(',')
            data = self.tryrules('number','symbolstr')
            return AssemblerOperation(operation =  op, reg = reg, data = data, size = 3)
        return None


    # Support functions
    def intermediate(self, opcode: str) -> AssemblerOperation:
        rx = self.registers()
        self.chars(',')
        value = self.number()
        return AssemblerOperation(operation= opcode, reg = rx, data = value, size = 2)

    def regreginstruction(self, opcode: str) -> AssemblerOperation:
        rx = self.registers()
        self.chars(',')
        ry = self.registers()
        return AssemblerOperation(operation= opcode, reg = rx, regr = ry, size = 1)


    def registers16(self) -> str:
            return self.trymatch('sp','r0','r2')

#    def registers16(self) -> str:
#            return self.trymatch('sp')

    def registers(self) -> int:
        r = self.chars('rR')
        reg = self.chars('0-3')
        return int(reg)

    def symbolstr(self) -> Data:
        symbol = []
        ch = self.chars('A-Za-z0-9_')
        symbol.append(ch)

        while True:
            ch = self.peek_chars('A-Za-z0-9_')
            if (ch is None):
                break
            symbol.append(ch)

        return ''.join(symbol)
#        return SymbolWordData(''.join(symbol),{})

    def number8(self) -> Data:
        num = self.tryrules('binarynumber','hexnumber','octalnumber','decnumber')
        return ByteData(num)

    def number(self) -> Data:
        print("<---in number--->")
        num = self.tryrules('binarynumber','hexnumber','octalnumber','decnumber')
        return num


    def octalnumber(self) -> int:
        chars = []

        if (self.trymatch('0o')):
            chars += '0o'
            chars.append(self.chars('0-7'))

            while True:
                char = self.peek_chars('0-7')
                if char is None:
                    break
                chars.append(char)
            return int(''.join(chars),8)


    def binarynumber(self) -> int:
        chars = []
        #v = self.trymatch('0b')
        if (self.trymatch('0b')):
            chars += '0b'
            chars.append(self.chars('0-1'))
            while True:
                char = self.peek_chars('0-1')
                if char is None:
                    break
                chars.append(char)
            return int(''.join(chars),2)


    def hexnumber(self) -> int:
        chars = []

        if (self.trymatch('0x')):
            chars += '0x'
            chars.append(self.chars('0-9A-Fa-f'))

            while True:
                char = self.peek_chars('0-9A-Fa-f')
                if char is None:
                    break
                chars.append(char)
            return int(''.join(chars),16)



    def decnumber(self) -> int:

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




if __name__ == '__main__':

    class SyntaxError(Exception):
        def __init__(self, msg, pos):
            self.msg = msg
            self.pos = pos

        def __str__(self):
            return f'{self.msg} at line {self.pos}'

    def produceBinFile(binName: str, ops: [AssemblerOperation]) -> int:
        combinarray = []

        file = open(binName, "wb")

        for op in ops:
            binarray = builder.build(op)
            combinarray += binarray

        file.write(bytes(combinarray))
        file.close()
        return len(combinarray)



    def produceV2HexFile(binName: str, ops) -> int:

        file = open(binName, "w+")
        file.write("v2.0 raw\n")
        totalsize = 0
        bcnt = 0

        for op in ops:
            if op.size > 0:
                binarray = builder.build(op)
                totalsize += len(binarray)
                for index, bytecode in enumerate(binarray):
                    file.write(f"{bytecode:02x} ")
                    if (bcnt % 8 == 7):
                        file.write("\n")
                    bcnt += 1

        file.write("\n")
        file.close()
        return totalsize


    def produceV3HexFile(binName: str, ops, addrOffset: int  = 0x8000) -> int:

        file = open(binName, "w+")
        file.write("v3.0 hex words addressed\n")

        address = 0
        lastaddr = -1
        totalsize = 0
        bytecount = 0
        lastaddrfromORG = -1
        bytecountfromORG = 0

        for opindex,op in enumerate(ops):
            binarray = builder.build(op)
            sz = len(binarray)
            totalsize += sz

            address = op.pc

            if (address != lastaddrfromORG) and \
                (op.operation == 'org' or (lastaddrfromORG == -1 and sz > 0)):

                bytecountfromORG = 0
                lastaddrfromORG = address
                if (addrOffset > address):
                    print("***WARNING*** address mismatch on assembling. Please check ORG directives - if assembling for RAM. Ignoring base address offset..")
                file.write(f"\n{ address - (addrOffset if addrOffset <= address else 0):04x}: ")

            if (sz > 0):
                for index,byteopcode in enumerate(binarray):
                    if (bytecountfromORG % 32 == 31):
                        file.write(f"\n{(address  + index - addrOffset if addrOffset <= address else 0):04x}: ")
                    file.write(f"{byteopcode:02x} ")
                    bytecountfromORG += 1


        file.write("\n")
        file.close()
        return totalsize


    def produceDummyOuput(ops) -> int:
        totalsize = 0
        for opindex,op in enumerate(ops):
            binarray = builder.build(op)
            sz = len(binarray)
            totalsize += sz
        return totalsize


    def processLabels(ops: AssemblerOperation, labels: dict) -> None:
        if (ops.operation == 'symbol'):
            labelnm = ops.data.getRawData()
            addr = ops.pc
            if (labelnm in labels):
                raise SyntaxError(f"Replicated label '{labelnm}'",ops.line)
            labels[labelnm] = addr

    def info(str,end=None) -> None:
        print(str,end='')


    def buildHelpText() -> str:
        return "\n\nExample: ./assembler.py example.asm [options]\n\n -v verbose\n -d debug\n -q quiet\n -s symbol table\n -3 [default] V3 addressed hex output\n -2 raw hex output\n -b binary output\n -n no output\n -r ROM address offset on V3 Hex output\n"


    def handleCommandArgs(argv: [str]) -> ([str],str,str):
        """Command line options have NO parameters so just record them"""

        options=set()
        file = None

        for index,arg in enumerate(argv):
            if (arg.startswith('-') and len(arg) > 1):
                options.add(arg[1:])
            else:
                if (index > 0):
                    file = arg
                else:
                    assembler = arg

        return options,file,assembler



    # ** Main Process Starts here ***
#    'mov' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0x90)),

#class SupportOperation:
#    data : str = None
#    reg : int = None
#    regr : int = None

#    so = SupportOperation(reg = 0, regr = 1)
#    db = DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0x90))
#    print(f"{db.build_bytecode(so)}")

#    db = TripleByteCodeBuilder(LookupByteCodeResolver({'sp':0x1d,'r0':0x1f, 'r2':0x1e}))
#    so = SupportOperation(reg = 'sp', data = SymbolWordData('pigscanfly',{'zombie':22, 'pigscanfly': 0xaaab}))
#    print(f"{db.build_bytecode(so)}")
#    sys.exit(-1)

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

    pc = 0
    line = 0
    code = []
    labels = {}
    errors = 0
    parser = AssemblerParser(labels)

    verbose ='v' in options
    debug = 'd' in options
    quiet = 'q' in options
    symtable = 's' in options
    help = 'h' in options
    nooutput = 'n' in options
    rom = 'r' in options

    outType  = OutputType.BINARY if 'b' in options\
                else OutputType.RAWHEX if '2' in options\
                else OutputType.ADDRESSEDHEX

    if (help):
        print(buildHelpText())
        sys.exit(0);

    if (not quiet):
        print(f"Trying to assemble '{sourceFilename}' \
ROMMODE:{rom}' \
verbose:{verbose} \
quiet:{quiet} \
debug:{debug} \
symtable:{symtable}\n")

    asm = open(sourceFilename, "r")
    completed = False

    while not completed:
        try:

            text = asm.readline()
            if len(text) == 0:
                break
            line = line + 1
            ops = None
            try:
                ops = parser.parse(text.strip())
            except Exception as e:
                print(f"Assembler **FAILED** on Line {line} {e}")
            # ops is an array of operation instructions - (in the case of 'label' followed by opcode instruction)
            if (ops is not None):
                for op in ops:
                    if (op is not None):
#                        op['line'] = line
                        op.line = line
                        if (debug):
                            print(op)
                        code.append(op)
                        if (op.operation == 'end'):
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
            if (op.operation == 'org'):
                pc = 0  #@TODO op.data.getData()
            op.pc = pc
            pc += op.size
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
        if (not nooutput):
            if (not quiet):
                print(f"Producing LogiSym output file '{binName}'")

            if (outType == OutputType.BINARY):
                size = produceBinFile(binName, code)
            elif (outType == OutputType.RAWHEX):
                size = produceV2HexFile(binName, code)
            elif (outType == OutputType.ADDRESSEDHEX):
                size = produceV3HexFile(binName, code, 0 if rom else RAMADDRESS)
            else:
                raise Exception('Output type is not defined')
        else:
            size = produceDummyOuput(code)

        if (not quiet):
            print(f"\nSize: {size} bytes")
            print("complete.\n")

        sys.exit(0)
    except (SyntaxError) as e:
        print(f"Syntax Error {e}")
