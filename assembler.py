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
RAM_ADDRESS = 0x8000
ROM_ADDRESS = 0x0000

@dataclass
class AssemblerOperation:
    operation : str = None
    pc : int = None
    size : int = 0
    data : str = None
    reg : int = None
    regr : int = None
    source_file:str = None
    source_line:int = None



class Dissassembler:

        class BaseDissassembler(ABC):

            @abstractmethod
            def dissassemble(self,op:AssemblerOperation) -> str:
                pass

        class DissImmediate(BaseDissassembler):

                def dissassemble(self,op: AssemblerOperation) -> str:
                    return op.operation +'\t'+ 'r' + str(op.reg) + ',' + f'{op.data.getData()[0]:02x}'

        class DissImmediate16(BaseDissassembler):

                def dissassemble(self,op: AssemblerOperation) -> str:
                    return op.operation +'\t' + f'{op.data.getData()[1]<<8 | op.data.getData()[0]:04x}'

        class DissRegImmediate16(BaseDissassembler):

                def dissassemble(self,op: AssemblerOperation) -> str:
                    return op.operation +'\t' + 'r' + str(op.reg) + ',' +f'{op.data.getData()[1]<<8 | op.data.getData()[0]:04x}'

        class DissSingleReg(BaseDissassembler):

                def dissassemble(self,op: AssemblerOperation) -> str:
                    return op.operation +'\t'+ 'r' + str(op.reg)

        class DissRegReg(BaseDissassembler):

                def dissassemble(self,op: AssemblerOperation) -> str:
                    return op.operation +'\t'+ 'r' + str(op.reg) + ',' + 'r' + str(op.regr)

        class DissSingleByteOpCode(BaseDissassembler):

                def dissassemble(self,op: AssemblerOperation) -> str:
                    return op.operation

        class DissSingleByteIndirectOpCode(BaseDissassembler):

                def dissassemble(self,op: AssemblerOperation) -> str:
                    return op.operation[1:] + '\t'+ f"r{op.reg},({op.regr})"

        class DissData(BaseDissassembler):

                def dissassemble(self,op: AssemblerOperation) -> str:
                    data = ''.join([f'{_x:02X}' for _i,_x in enumerate(op.data.getData())])
                    return op.operation +'\t'+ f'{data}'


        def dissassemble(self,op:AssemblerOperation) -> str:
            disactions = {
                        'movwi'   : self.DissRegImmediate16(),
                        'ld'   : self.DissRegImmediate16(),
                        'st'   : self.DissRegImmediate16(),
                        'djnz'   : self.DissRegImmediate16(),

                        'shl'  : self.DissSingleReg(),
                        'shr'  : self.DissSingleReg(),

                        'out'  : self.DissSingleReg(),
                        'inc'  : self.DissSingleReg(),
                        'dec'  : self.DissSingleReg(),

                        'call' : self.DissImmediate16(),
                        'jmp' : self.DissImmediate16(),
                        'jpz' : self.DissImmediate16(),
                        'jpnz' : self.DissImmediate16(),
                        'jpc' : self.DissImmediate16(),
                        'jpnc' : self.DissImmediate16(),
                        'jps' : self.DissImmediate16(),
                        'jpns' : self.DissImmediate16(),
                        'jpo' : self.DissImmediate16(),
                        'jpno' : self.DissImmediate16(),
                        'jpv' : self.DissImmediate16(),
                        'jpnv' : self.DissImmediate16(),

                        'movi' : self.DissImmediate(),
                        'addi' : self.DissImmediate(),
                        'subi' : self.DissImmediate(),
                        'andi' : self.DissImmediate(),
                        'ori' :  self.DissImmediate(),
                        'xori' : self.DissImmediate(),

                        'mov' : self.DissRegReg(),
                        'add' : self.DissRegReg(),
                        'sub' : self.DissRegReg(),
                        'and' : self.DissRegReg(),
                        'or' : self.DissRegReg(),
                        'xor' : self.DissRegReg(),
                        'swp' : self.DissRegReg(),

                        'hlt' : self.DissSingleByteOpCode(),
                        'nop' : self.DissSingleByteOpCode(),
                        'ret' : self.DissSingleByteOpCode(),
                        'clc' : self.DissSingleByteOpCode(),
                        'setc' : self.DissSingleByteOpCode(),
                        'exx' : self.DissSingleByteOpCode(),

                        'db' : self.DissData(),
                        'dw' : self.DissData(),
                        'dt' : self.DissData(),

                        'ist' : self.DissSingleByteIndirectOpCode(),
                        'ild' : self.DissSingleByteIndirectOpCode(),

                    }
            return f'{ "?"+op.operation if op.operation not in disactions else disactions[op.operation].dissassemble(op)}'


class OperationNotSupported(Exception):
    def __init__(self, operation, message="Operation not currently supported"):
        self.operation = operation
        self.message = f"{message}: {operation}"
        super().__init__(self.message)

class Data(ABC):
    def __init__(self,data):
        self.data = data

    def getRawData(self):
        return self.data

    @abstractmethod
    def getData(self):
        pass

    def __str__(self):
        return f"Raw data <{self.data}>"

    def __repr__(self):
        return f"Raw data: <{self.data}>"


class FunctionData(Data):
    # Useful for 8-bit data instructions -(movi,addi,subi etc)
    # movi r0,@LOW(somesymbolname)
    # movi r1,@HIGH(somesymbolname)
    # or
    # movi r0,@LOW(0x2fff)
    # movi r1,@HIGH(0x2fff)

    def __init__(self, fnc, data):
        super().__init__(data)
        self.fnc = fnc

    def getData(self):
        return [self.data.getData()[0]] if self.fnc == 'LOW' or self.fnc == '>' else \
                [self.data.getData()[1]]

    def __str__(self):
        return f"FunctionData: fnc:{self.fnc} {super().__str__()}"
    def __repr__(self):
        return f"FunctionData: fnc:{self.fnc} {super().__str__()}"

class SymbolWordData(Data):

    def __init__(self, data, lookup):
        super().__init__(data)
        self.lut = lookup

    def getData(self):
        value = self.lut[self.data]
        return [value & 0xff, value>>8 & 0xff]

    def __str__(self):
        return f"SymbolWordData: {super().__str__()}"
    def __repr__(self):
        return f"SymbolWordData: {super().__str__()}"

class WordData(Data):

    def __init__(self, data):
        super().__init__(data)

    def getData(self):
        value = self.data
        return [value & 0xff, value>>8 & 0xff]

    def __str__(self):
        return f"WordData: {super().__str__()}"
    def __repr__(self):
        return f"WordData: {super().__str__()}"

class ByteData(Data):

    def __init__(self, data):
        super().__init__(data & 0xff)

    def getData(self):
        value = self.data
        return [value]

    def __str__(self):
        return f"ByteData: {super().__str__()}"
    def __repr__(self):
        return f"ByteData: {super().__str__()}"

class StringData(Data):

    def __init__(self, data):
        #print(f"StringData: {data}")
        super().__init__(data)

    def getData(self):
        return [ord(_x) for _x in (list(self.getRawData()) + [chr(0)])]

    def __str__(self):
        return f"StringData: {super().__str__()}"
    def __repr__(self):
        return f"StringData: {super().__str__()}"

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



class LookupByOperandByteCodeResolver(ByteCodeResolver):
    def __init__(self, table):
        self.lut = table

    def getByteCode(self,support: SupportOperation) -> int:
        return self.lut[support.reg]



class ByteCodeBuilder(ABC):

    @abstractmethod
    def build_bytecode(self, support_data: SupportOperation) -> [int]:
        pass

class SingleByteCodeBuilder(ByteCodeBuilder):
    def __init__(self, basebyte_resolver):
        self.basebyte_resolver = basebyte_resolver

    def build_bytecode(self, support: SupportOperation) -> [int]:
        base_code = self.basebyte_resolver.getByteCode(support)
        return [base_code]


class SingleRegByteCodeBuilder(ByteCodeBuilder):
    def __init__(self, basebyte_resolver):
        self.basebyte_resolver = basebyte_resolver

    def build_bytecode(self, support: SupportOperation) -> [int]:
        base_code = self.basebyte_resolver.getByteCode(support)
        return [base_code | (support.reg)] + ([] if support.data is None else support.data.getData())



class DoubleRegByteCodeBuilder(ByteCodeBuilder):
    def __init__(self, basebyte_resolver):
        self.basebyte_resolver = basebyte_resolver

    def build_bytecode(self, support: SupportOperation) -> [int]:
        base_code = self.basebyte_resolver.getByteCode(support)
        return [base_code | (support.reg<<2) | (support.regr)]



class TripleByteCodeBuilder(ByteCodeBuilder):
    def __init__(self, basebyte_resolver):
        self.basebyte_resolver = basebyte_resolver

    def build_bytecode(self, support: SupportOperation) -> [int]:
        base_code = self.basebyte_resolver.getByteCode(support)
        return [base_code]  + support.data.getData()

class NullByteCodeBuilder(ByteCodeBuilder):

    def build_bytecode(self, support: SupportOperation) -> [int]:
        return []


class IndirectByteCodeBuilder(ByteCodeBuilder):

    def build_bytecode(self, support: SupportOperation) -> [int]:
        #print(f"IndirectByteCodeBuilder: BUILD INDIRECT {support}")
        try:
            #print(f"opcode: '{support.operation}' r{support.reg}, ({support.regr})'")

            lookup = f'{support.reg}{support.regr}'
            # Match current buildcontrolrom.py as of 14/10/24

            opcode_table = {
            'ild':{

                #'0r2': 0x00,
                #'0r3': 0x00,

                #'1r2': 0x00,
                #'1r3': 0x00,

                '2r0': 0x4e,
                '2r1': 0x4e,

                '3r0': 0x4f,
                '3r1': 0x4f,
                },
            'ist':{

                #'0r2': 0x00,
                #'0r3': 0x00,

                #'1r2': 0x00,
                #'1r3': 0x00,

                '2r0': 0x4a,
                '2r1': 0x4a,

                '3r0': 0x4b,
                '3r1': 0x4b,
                }
            }
            try:
                bytecode = opcode_table[support.operation][lookup]
                return [bytecode]
            except Exception as e:
                print(f"Exception in lookup {e}")
                raise OperationNotSupported(f"opcode: '{support.operation}' r{support.reg}, ({support.regr})'")
        except OperationNotSupported as e:
            print(f"{e}")
        return []

class DataByteCodeBuilder(ByteCodeBuilder):

    def build_bytecode(self, support: SupportOperation) -> [int]:
        return support.data.getData()


class ReserveSpaceByteCodeBuilder(ByteCodeBuilder):

    def build_bytecode(self, support: SupportOperation) -> [int]:
        return [0]*support.size


class OutputType(Enum):
    BINARY = auto()
    RAWHEX = auto()
    ADDRESSEDHEX = auto()

@dataclass
class BuildOperation:
    build : str
    bytecode : int = None

codeBuilder= {
    'mov' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0x90)),
    'movi' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x40)),
    'movwi' : TripleByteCodeBuilder(LookupByOperandByteCodeResolver({'sp':0x1c,'r0':0x28, 'r1':0x28, 'r2':0x2a, 'r3': 0x2a})),    # set SP/R0R1/R2R3 with a 16-bit address

    'csp' : SingleByteCodeBuilder(LookupByOperandByteCodeResolver({0:0x48, 1:0x48, 2:0x49, 3: 0x49})),

    'ld' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x14)),
    'st' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x18)),

    'out' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x10)),
    'inc' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x88)),
    'dec' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x8c)),

    'decsp' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x1e)),
    'incsp' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x1d)),

    'pushr0' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x1f)),
    'pushr2' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x20)),
    'pushall' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x21)),
    'popr0' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x22)),
    'popr2' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x23)),
    'popall' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x24)),

    'shr' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x80)),
    'shl' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x84)),

    'add' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0xa0)),
    'sub' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0xb0)),
    'and' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0xc0)),
    'or' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0xd0)),
    'xor' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0xe0)),
    'swp' : DoubleRegByteCodeBuilder(SimpleByteCodeResolver(0x30)),


    'addi' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x50)),
    'subi' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x54)),
    'andi' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x58)),
    'ori' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x5c)),
    'xori' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x44)),

    'djnz' : SingleRegByteCodeBuilder(SimpleByteCodeResolver(0x60)),

    'jpz' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x64)),
    'jpnz' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x65)),

    'jpc' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x66)),
    'jpnc' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x67)),

    'jps' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x68)),
    'jpns' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x69)),

    'jpv' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x6a)),
    'jpnv' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x6b)),

    'jmp' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x6c)),
    'call' : TripleByteCodeBuilder(SimpleByteCodeResolver(0x6e)),

    'ret' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x6f)),

    'clc' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x01)),
    'setc' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x02)),
    'nop' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x00)),
    'exx' : SingleByteCodeBuilder(SimpleByteCodeResolver(0x25)),
    'hlt' : SingleByteCodeBuilder(SimpleByteCodeResolver(0xff)),

    # Indirect addressing
    'ist':IndirectByteCodeBuilder(),
    'ild':IndirectByteCodeBuilder(),

    'cppline' : NullByteCodeBuilder(),
    'cppbuiltin' : NullByteCodeBuilder(),

    'org' : NullByteCodeBuilder(),
    'symbol' : NullByteCodeBuilder(),
    'comment' : NullByteCodeBuilder(),

    'db' : DataByteCodeBuilder(),
    'dw' : DataByteCodeBuilder(),
    'ds' : ReserveSpaceByteCodeBuilder(),
    'dt' : DataByteCodeBuilder(),

    'end' : NullByteCodeBuilder(),
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

    def opCodeBuilder(self, op: AssemblerOperation) -> [int]:
        nm = op.operation
        if (nm in codeBuilder):
            try:
                builder = codeBuilder[nm]
                so = op
                binarray = builder.build_bytecode(so)
                return binarray
            except KeyError as e:
                print(f"SymbolTable Error {e}")
                return []
        else:
            print("Can not find opCode builder for ",op)
            return []


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

    def trymatch(self,*wantedtoks,**opts) -> str:
        self.gobblewhitespace()
        z = list(wantedtoks)
        z.sort(key = lambda e: len(e),reverse=True)
        #print(z)
        for tok in z:
            caughttok = self.wanted(tok)
            if (caughttok != None):
                if 'whitespace' in opts:
                    if opts['whitespace']:
                        ch = self.text[self.pos]
                        if not (ch == ' ' or ch == '\t'):
                            print(f"Parser Error. Expected whitespace but got <{ch}>")
                            return None

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

    def peek_chars(self, pattern: str, dont_gobble:bool=False) -> str:

        try:
            return self.chars(pattern, dont_gobble = dont_gobble)
        except ParserException as e:
            # We have not found a char match - so go back and check other rules/token matches
            return None
        except IndexError as e:
            # Arrived here from 'chars' function - 'ch = self.text[self.pos]'
            # -  exhausted parsing our current line of text
            return None

    def chars(self, pattern: str, bump: bool = True, dont_gobble:bool=False) -> str:
        if (not dont_gobble):
            self.gobblewhitespace()

        if (pattern not in self._cache):
            self._cache[pattern] = self.produce_chars_pattern(pattern)
        ch = self.text[self.pos]
        if ch in self._cache[pattern]:
            if (bump):
                self.pos += 1
            return ch
        raise ParserException(f"Parser.chars Expected {pattern} but got <{ch}>")


    # Perhaps - get rid of this - and replace with 'try_function_rules'
    # Using the 'getattr' function to find the actual function -
    # just saves us having to preindex names with 'self.'

    def try_rules(self,*rules):
        self.gobblewhitespace()

        for rule in rules:
            try:
                rv = getattr(self, rule)()
                if (rv is not None):
                    return rv
            except ParserException as e:
                pass

    def try_function_rules(self,*rules):
        self.gobblewhitespace()

        for rule in rules:
            try:
                rv = rule()
                if (rv is not None):
                    return rv
            except ParserException as e:
                pass

    def finish_parsing(self):
        self.pos = self.len + 1


class AssemblerParser(BaseParser):
    def __init__(self, symbolTable):
        super().__init__()
        self.symbolTable = symbolTable


    def parse(self, text):

        super().init(text)
        self.start()
        allops = []

        while (self.pos < self.len):

            rv = self.try_rules('cpp_directive','comment', 'symbol', 'directive', 'instruction')

            if (rv is None):
                raise ParserException(f"Can not parse {self.text}")

            allops.append(rv)

        return allops


    def start(self):
        # Set up anything else to do with parsing our syntax -
        # We don't need to do anything here - as code generation is very simple.
        # Symbols are handled by walking through our code operations - twice
        pass

    # Top rules
    # CPP directive - allows us to use the generic C preprocessor - such as cpp
    def cpp_directive(self) -> AssemblerOperation:
        if self.peek_chars('#'):
            #print("cpp_directive",self)
            data = self.text[self.pos:]
            number = self.try_rules('decnumber')
            if (number is not None):
                # try and extract file source name or cpp function
                self.gobblewhitespace()
                if (self.chars('"')):
                    fName = self.cpp_str()  #At this point we've either read in a file name
                                            # or a CPP function type
                    self.chars('"')
                    # ignore everything else - after the trailing quote
                    self.finish_parsing()
                    # check to see if this is not some built-in definition.
                    if (not fName.startswith("<")):
                        return AssemblerOperation(operation = 'cppline', data = data, source_file = fName, source_line = number - 1 , size = 0)

                #self.finish_parsing()
                return AssemblerOperation(operation = 'cppbuiltin',size = 0, data=data)

            self.finish_parsing()
            return AssemblerOperation(operation = 'comment',data = data , size = 0)


    def comment(self) -> AssemblerOperation:
        """If we spot a comment TOKEN - then save text up to EOL and finish off parsing the line"""
        if self.peek_chars(';'):
            data = self.text[self.pos:]
            self.pos = self.len + 1
            return AssemblerOperation(operation = 'comment',data = data , size = 0)


    def symbol(self) -> AssemblerOperation:
        if (self.peek_chars(":")):
            str = self.symbolstr()
            return AssemblerOperation(operation = 'symbol', data = str,  size = 0)

    def directive(self) -> AssemblerOperation:
        if (self.peek_chars(".")):
            return self.try_rules('org','end','db','dw','ds','dt')



    def instruction(self) -> AssemblerOperation:
        return self.try_rules('movwi','intermediate8','reg8','ld',\
                            'call','singlebyte','singleop','out','pushpop','djnz')


    # Directive operations

    def org(self) -> AssemblerOperation:
        if (self.trymatch('org')):
            return AssemblerOperation(operation ='org', data = self.number16bit(), size = 0)

    def end(self) -> AssemblerOperation:
        if (self.trymatch('end')):
            return AssemblerOperation(operation ='end', size = 0)

    def dw(self) -> AssemblerOperation:
        if (self.trymatch('dw')):
            return AssemblerOperation(operation = 'dw', data = self.number16bit(), size = 2)

    def db(self) -> AssemblerOperation:
        if (self.trymatch('db')):
            return AssemblerOperation(operation = 'db', data = self.number8bit(), size = 1)

    def ds(self) -> AssemblerOperation:
        if (self.trymatch('ds')):
            return AssemblerOperation(operation = 'ds', data =  0, size = self.number16bit().getRawData())

    def dt(self) -> AssemblerOperation:
        if (self.trymatch('dt')):
            strmatch = 'A-Za-z0-9_@().!*[]//-+# '
            astr = []
            self.chars("'")

            ch = self.chars(strmatch, dont_gobble = True)
            astr.append(ch)

            while True:
                ch = self.peek_chars(strmatch, dont_gobble = True)
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
            regl = self.try_rules('registers16')
            self.chars(',')
            data = self.try_rules('number16bit','symbolstr')
            return AssemblerOperation(operation = op, reg = regl, data = data, size = 3)
        return None


    def intermediate8(self) -> AssemblerOperation:
        m = self.trymatch('movi','addi','subi','andi','ori','xori')
        if (m):
            return self.intermediate(m)
        return None

    def reg8(self) -> AssemblerOperation:
        m = self.trymatch('mov','add','sub','and','or','xor','swp')
        if (m):
            return self.regreginstruction(m)
        return None

    def ld(self) -> AssemblerOperation:
        op = self.trymatch('ld','st')
        if (op is not None):
            regl = self.try_rules('registers')
            self.chars(',')
            if (self.peek_chars('(')):
                regp = self.try_rules('registers16')
                self.chars(')')
                # SMELLY!
                return AssemblerOperation(operation = "i" + op, reg =  regl, regr = regp, size = 1)
            else:
                data = self.try_rules('number16bit','symbolstr')
                return AssemblerOperation(operation = op, reg =  regl, data = data, size = 3)
        return None


    def call(self) -> AssemblerOperation:
        op = self.trymatch('call','jmp','jpz','jpnz','jpc',\
                            'jpnc','jps','jpns','jpv','jpnv',whitespace=True)
        if (op is not None):
            data = self.try_rules('number16bit','symbolstr')
            return AssemblerOperation(operation = op, data = data, size = 3)
        return None


    def singlebyte(self) -> AssemblerOperation:
        op = self.trymatch('inc','dec')
        if (op is not None):
            reg = self.try_rules('registers','registers16')
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
        op = self.trymatch('out','shl','shr','csp')
        if (op is not None):
            reg = self.try_rules('registers')
            return AssemblerOperation(operation = op, reg = reg, size = 1)
        return None

    def pushpop(self) -> AssemblerOperation:
        op = self.trymatch('pop','push')
        if (op is not None):
            reg = self.try_rules('registers')
            return AssemblerOperation(operation = op+'r'+str(reg), reg = reg,  size = 1)
        return None



    def djnz(self) -> AssemblerOperation:
        op = self.trymatch('djnz')
        if (op is not None):
            reg = self.registers()
            self.chars(',')
            data = self.try_rules('number16bit','symbolstr')
            return AssemblerOperation(operation =  op, reg = reg, data = data, size = 3)
        return None


    # Added support functions @LOW and @HIGH to be able to calculate
    # an 8-bit value from a data or symbol address which is 16-bit
    # eg. movi r0, @LOW(0x8100)  - movi r0, @LOW(lookuptable) movi r1,@HIGH(lookuptable)

    def intermediate(self, opcode: str) -> AssemblerOperation:
        rx = self.registers()
        self.chars(',')
        fnc = self.peek_chars('<>')
        if (fnc):
            dvalue = self.try_rules('number16bit','symbolstr')
            if (dvalue is None):
                return None
            value = FunctionData(fnc,dvalue)
            return AssemblerOperation(operation= opcode, reg = rx, data = value, size = 2)

        value = self.number8bit()
        return AssemblerOperation(operation= opcode, reg = rx, data = value, size = 2)


    # def intermediateOLD(self, opcode: str) -> AssemblerOperation:
    #     rx = self.registers()
    #     self.chars(',')
    #     if (self.peek_chars('@')):
    #         fnc = self.trymatch('LOW','HIGH')
    #         #if (fnc := self.trymatch('LOW','HIGH')):  #3.8!
    #         if (fnc):
    #             self.chars('(')
    #             dvalue = self.try_rules('number16bit','symbolstr')
    #             if (dvalue is None):
    #                 return None
    #             self.chars(')')
    #             value = FunctionData(fnc,dvalue)
    #             return AssemblerOperation(operation= opcode, reg = rx, data = value, size = 2)
    #         # SHOULD NOT ARRIVE HERE! DO SOMETHING
    #         return None
    #     value = self.number8bit()
    #     return AssemblerOperation(operation= opcode, reg = rx, data = value, size = 2)

    def regreginstruction(self, opcode: str) -> AssemblerOperation:
        rx = self.registers()
        self.chars(',')
        ry = self.registers()
        return AssemblerOperation(operation= opcode, reg = rx, regr = ry, size = 1)


    def registers16(self) -> str:
            return self.trymatch('sp','r0','r2')

    def registers(self) -> int:
        r = self.chars('rR')
        reg = self.chars('0-3')
        return int(reg)

    def cpp_str(self) -> str:
        str_value = []
        ch = self.chars('A-Za-z0-9_.<>//- ///')
        str_value.append(ch)

        while True:
            ch = self.peek_chars('A-Za-z0-9_.<>//- ///')
            if (ch is None):
                break
            str_value.append(ch)

        return ''.join(str_value)

    def symbolstr(self) -> str:
        symbol = []
        ch = self.chars('A-Za-z0-9_')
        symbol.append(ch)
        while True:
            ch = self.peek_chars('A-Za-z0-9_',dont_gobble=True)
            if (ch is None):
                break

            symbol.append(ch)

        return SymbolWordData(''.join(symbol),self.symbolTable)


    def number16bit(self) -> int:
        num = self.try_rules('binarynumber','hexnumber','octalnumber','decnumber')
        if (num is not None):
            return WordData(num)


    def number8bit(self) -> int:
        num = self.try_rules('binarynumber','hexnumber','octalnumber','decnumber')
        if (num is not None):
            return ByteData(num)


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


    def produceCodeOuput(ops) -> int:
        totalsize = 0

        dissassembler = Dissassembler()

        for opindex,op in enumerate(ops):
            binarray = builder.build(op)
            sz = len(binarray)
            if (sz > 0):
                print(f'{op.pc:04X}\t',end='')
                bc = ''.join([f'{_x:02X}' for _i,_x in enumerate(binarray) if _i < 128])
                print(f'{bc}',end='')
                print(f'\t{dissassembler.dissassemble(op)}')
            totalsize += sz
        return totalsize

    def processLabel(ops: AssemblerOperation, labels: dict) -> None:

        labelnm = ops.data.getRawData()
        addr = ops.pc
        if (labelnm in labels):
            raise SyntaxError(f"Replicated label '{labelnm}'",ops.line)
        labels[labelnm] = addr


    def info(str,end=None) -> None:
        print(str,end='')

    def print_if_true(check, str,*args,**kwargs):
        if (check):
            print(str,*args,**kwargs)

    def buildHelpText() -> str:
        return "\n\nExample: ./assembler.py example.asm [options]\n\n -v verbose\n -d debug\n -q quiet\n -s symbol table\n -3 [default] V3 addressed hex output\n -2 raw hex output\n -b binary output\n -n no output [-c dissassembled code]\n -r ROM address offset on V3 Hex output\n"


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



    """ Main Process Starts here """

    #print(sys.version_info)
    #if not (sys.version_info.major == 3 and sys.version_info.minor == 8 ):
    #    sys.exit(-1)

    # Command Line options and check if source exists
    options,sourceFilename,assembler = handleCommandArgs(sys.argv)

    try:

        if (sourceFilename is None):
            hText = buildHelpText()
            raise Exception(f"Source file is needed to assemble!\n{hText}")

        if (not os.path.isfile(sourceFilename)):
            raise IOError(f"Sourcefile '{sourceFilename}' does not exist.")

    except IOError as e:
        print(e)
        sys.exit(-1)



    verbose_option ='v' in options
    debug_option = 'd' in options
    quiet_option = 'q' in options
    symtable_option = 's' in options
    help_option = 'h' in options
    nooutput_option = 'n' in options
    dissassembled_code_option ='c' in options

    rom_option = 'r' in options
    ram_address = RAM_ADDRESS  #Perhaps offer this as an option?

    outType  = OutputType.BINARY if 'b' in options\
                else OutputType.RAWHEX if '2' in options\
                else OutputType.ADDRESSEDHEX

    if (help_option):
        print(buildHelpText())
        sys.exit(0);

    print_if_true(not quiet_option,f"Trying to assemble '{sourceFilename}' \
ROMMODE:{rom_option}' \
verbose:{verbose_option} \
quiet:{quiet_option} \
debug:{debug_option} \
symtable:{symtable_option}\n")


    labels = {}
    parser = AssemblerParser(labels)        #Assembler Operations need a reference to the
                                            #actual Symbol table ('labels') for the code generation - part -
                                            #to resolve symbol names (addresses).

                                            # There are no preprocessor symbols/constants (eg.'#DEFINE NUMBEROFLOOPS 0x22')
                                            # handled by the parser as this can easily be
                                            # implemented using a decent preprocessor
                                            # such as 'cpp' or 'm4'

                                            # The only thing we may need is something to handle
                                            # finding bytes of an address -
                                            #  such as movi r0,@LOW(16bitaddress/symbol)


    asm = open(sourceFilename, "r")

    completed = False
    assembler_errors = 0
    code = []
    line = 0
    current_filename = sourceFilename

    while not completed:
        try:
            text = asm.readline()
            if len(text) == 0:
                completed = True
                break

            line = line + 1
            try:
                # Parse a line and build up code operations (a single line could have multiple operations)
                operations = parser.parse(text.strip())
                for op in operations:

                     if (op is not None):
                        # Check for any CPP directives which would tell is the source file.
                        # and line number
                        if (op.operation == 'cppline'):
                            line = op.source_line
                            current_filename = op.source_file

                        op.source_line = line          # Fill operator with line number
                        op.source_file = current_filename

                        #if (debug_option):
                        print_if_true(debug_option, op)
                        code.append(op)         # Place this in an ordered array for our builder

                        if (op.operation == 'end'):
                            completed = True

            except Exception as e:
                print(f"Assembler **FAILED** on Line {line} '{current_filename}' {e}")

        except KeyboardInterrupt:
            pass
        except (EOFError, SystemExit):
            break
        except IndexError as e:
            print(f'Index Error: {e} Line {line}')
            #break
        except (ParseError, ZeroDivisionError) as e:
            print(f'Parse Error: {e} Line {line} {text}')
            assembler_errors += 1

    # Parsing complete
    if (assembler_errors > 0):
        print_if_true(not quiet_option, f"Build Failed! {assembler_errors} assembler errors. See a Code Doctor. Quick!")
        sys.exit(-1)

    try:

        program_counter = 0
        # Pre-process build a symbol address table
        for op in code:

            if (op.operation == 'org'):
                program_counter = op.data.getRawData() # SMELLY

            op.pc = program_counter
            program_counter += op.size

            if (op.operation == 'symbol'):
                processLabel(op,labels)

            print_if_true(verbose_option, op)



        if (not quiet_option and symtable_option):
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
        if (not nooutput_option):

            print_if_true(not quiet_option, f"Producing LogiSym output file '{binName}'")

            if (outType == OutputType.BINARY):
                size = produceBinFile(binName, code)
            elif (outType == OutputType.RAWHEX):
                size = produceV2HexFile(binName, code)
            elif (outType == OutputType.ADDRESSEDHEX):
                size = produceV3HexFile(binName, code, ROM_ADDRESS if rom_option else ram_address)
            else:
                raise Exception('Output type is not defined')
        else:
            size = produceCodeOuput(code) if dissassembled_code_option else produceDummyOuput(code)


        print_if_true(not quiet_option, f"\nSize: {size} bytes\ncomplete.\n")

        sys.exit(0)
    except (SyntaxError) as e:
        print(f"Syntax Error {e}")
