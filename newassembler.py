#!/usr/bin/env python3
import sys
import os.path
from enum import Enum
WSPACE = "\f\v\r\t\n "

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

    def __init__(self,text):
        print("BaseParser __init__")
        self.text = text
        self.pos = 0
        self.len = len(text)
        self._cache = dict()


    def __str__(self):
        return f"<{self.text}> pos:{self.pos} out of {self.len} current <{self.text[self.pos:]}>"

    def start(self):
        raise ParserException('Abstract Function needs to overrriden')

    def parse(self):
        raise ParserException('Abstract Function needs to overrriden')

    def current(self):
        return self.text[self.pos:]

    def gobblewhitespace(self):
        while self.text[self.pos] in WSPACE:
            self.pos += 1
        #print("gooble ended at ",self.pos,self.text[self.pos:])


    def position(self):
        print(self.pos, "out of ",self.len, "text", self.text)

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
        #print("tryrules",rules,self)
        for rule in rules:
            print("trying Rule ", rule)
            try:
                rv = getattr(self, rule)()
                if (rv is not None):
                    return rv
            except Exception as e:
                print(f"EXCEPTION {e}")


class MyParser(BaseParser):
    def __init__(self,text):
        super().__init__(text)

    def start(self):
        print("Start ")

    def parse(self):
        print("Parse ")
        while (self.pos < self.len):
            rv = self.tryrules('comment','symbol','directive','instruction')
            print("**Built Operation**",rv)

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
            return {'data': str,'size':0}

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
        return self.tryrules('intermediate8','reg8','ld','call','singlebyte','singleop','out','pushpop','djnz','movwi')



    def registers(self):
        r = self.chars('rR')
        reg = self.chars('0-3')
        return reg


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
            print("Matching SO FAR - HEX",self)
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




#p = MyParser("movi r0,0b10101 mov r2,0xfe")
#p = MyParser(".org 0x100 :start movi r2,-127 ; hang on to your hats!")
p = MyParser(".dt 'Hello' ; xxx")

#print(p)
p.parse()


#print(p.chars("0"))

#raise ParserDefinitionError("Some Parserdefintion Error")
#print(peekahead_chars('0-9'))
