#!/usr/bin/env python3
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
    'pushall' : {'build':'singleByteBuilder','bytecode':0x21},
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
    'label' : {'build':'nullBuilder'},
    'db' : {'build':'dataBuilder','size':1},
    'dw' : {'build':'dataBuilder','size':2},
    'ds' : {'build':'dataBuilder','size':-1},
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
    def __init__(self, pos, msg, *args):
        self.pos = pos
        self.msg = msg
        self.args = args

    def __str__(self):
        return '%s at position %s' % (self.msg % self.args, self.pos)

class Parser:
    def __init__(self):
        self.cache = {}

    def parse(self, text):
        self.text = text
        self.pos = -1
        self.len = len(text) - 1
        if (self.len > 0):
            rv = self.start()
            self.eat_comment()
            self.assert_end()
            return rv
        return None

    def assert_end(self):
        if self.pos < self.len:
            raise ParseError(
                self.pos + 1,
                'Expected end of string but got %s',
                self.text[self.pos + 1]
            )
    def eat_comment(self):
       if ( self.pos < self.len and self.text[self.pos + 1] in ";#"):
            self.pos = self.len


    def eat_whitespace(self):
        while self.pos < self.len and self.text[self.pos + 1] in " \f\v\r\t\n":
            self.pos += 1

    def split_char_ranges(self, chars):
        try:
            return self.cache[chars]
        except KeyError:
            pass

        rv = []
        index = 0
        length = len(chars)

        while index < length:
            if index + 2 < length and chars[index + 1] == '-':
                if chars[index] >= chars[index + 2]:
                    raise ValueError('Bad character range')

                rv.append(chars[index:index + 3])
                index += 3
            else:
                rv.append(chars[index])
                index += 1

        self.cache[chars] = rv
        return rv

    def char(self, chars=None):
        if self.pos >= self.len:
            raise ParseError(
                self.pos + 1,
                'Expected %s but got end of string',
                'character' if chars is None else '[%s]' % chars
            )

        next_char = self.text[self.pos + 1]
        if chars == None:
            self.pos += 1
            return next_char

        for char_range in self.split_char_ranges(chars):
            if len(char_range) == 1:
                if next_char == char_range:
                    self.pos += 1
                    return next_char
            elif char_range[0] <= next_char <= char_range[2]:
                self.pos += 1
                return next_char

        raise ParseError(
            self.pos + 1,
            'Expected %s but got %s',
            'character' if chars is None else '[%s]' % chars,
            next_char
        )

    def keyword(self, *keywords):
        self.eat_whitespace()
        if self.pos >= self.len:
            raise ParseError(
                self.pos + 1,
                'Expected %s but got end of string',
                ','.join(keywords)
            )

        for keyword in keywords:
            low = self.pos + 1
            high = low + len(keyword)

            if self.text[low:high] == keyword:
                self.pos += len(keyword)
                self.eat_whitespace()
                return keyword

        raise ParseError(
            self.pos + 1,
            'Expected %s but got %s',
            ','.join(keywords),
            self.text[self.pos + 1],
        )

    def match(self, *rules):
        self.eat_whitespace()
        last_error_pos = -1
        last_exception = None
        last_error_rules = []

        for rule in rules:
            initial_pos = self.pos
            try:
                rv = getattr(self, rule)()
                self.eat_whitespace()
                return rv
            except ParseError as e:
                self.pos = initial_pos

                if e.pos > last_error_pos:
                    last_exception = e
                    last_error_pos = e.pos
                    last_error_rules.clear()
                    last_error_rules.append(rule)
                elif e.pos == last_error_pos:
                    last_error_rules.append(rule)

        if len(last_error_rules) == 1:
            raise last_exception
        else:
            raise ParseError(
                last_error_pos,
                'Expected %s but got %s',
                ','.join(last_error_rules),
                self.text[last_error_pos]
            )

    def maybe_char(self, chars=None):
        try:
            return self.char(chars)
        except ParseError:
            return None

    def maybe_match(self, *rules):
        try:
            return self.match(*rules)
        except ParseError:
            return None

    def maybe_keyword(self, *keywords):
        try:
            return self.keyword(*keywords)
        except ParseError:
            return None

class AssemblerParser(Parser):

    def start(self):
        #print("start")
        ###print(self.text)
        ##print(self.pos)
        #print(self.len)

        return self.testme()

    def testme(self):
        rv = self.match('instruction','label','metaop')
        return rv

    def instruction(self):
        return self.match('alu','movwi','movi','mov','ld','call','singlebyte','singleop','out','djnz')

    def singleop(self):
        op = self.keyword('exx','pushall','popall','ret','nop','hlt','clc','setc')
        if (op is not None):
            return {'op': op, 'size':1}
        return None

    def out(self):
        op = self.keyword('out','push','shl','shr')
        if (op is not None):
            reg = self.match('registers')
            return {'op': op, 'reg':reg, 'size':1}
        return None

    def singlebyte(self):
        op = self.keyword('inc','dec')
        if (op is not None):
            reg = self.match('registers','registers16')
            return {'op': op if isinstance(reg,int) else op+reg, 'reg':reg, 'size':1}
        return None


    def djnz(self):
        op = self.keyword('djnz')
        if (op is not None):
            reg = self.match('registers')
            self.char(',')
            data = self.match('number','labelstr')
            return {'op': op, 'reg': reg,'data':data, 'size':3}
        return None

    def call(self):
        op = self.keyword('call','jmp','jpz','jpnz','jpc','jpnc','jps','jpns','jpo','jpno')
        if (op is not None):
            data = self.match('number','labelstr')
            return {'op': op, 'data':data, 'size':3}
        return None

    def ld(self):
        op = self.keyword('ld','st')
        if (op is not None):
            regl = self.match('registers')
            self.char(',')
            data = self.match('number','labelstr')
            return {'op': op, 'reg': regl, 'data':data, 'size':3}
        return None

    def movwi(self):
        op = self.keyword('movwi',)
        if (op is not None):
            regl = self.match('registers16')
            self.char(',')
            data = self.match('number','labelstr')
            return {'op': op, 'reg': regl, 'data':data, 'size':3}
        return None

    def alu(self):

        logic = self.maybe_keyword('andi','ori','xori','addi','subi')
        if (logic is not None):
            regl = self.match('registers')
            self.char(',')
            data = self.match('number','label')
            return {'op': logic, 'reg': regl, 'data':data, 'size':2}

        logic = self.keyword('and','or','xor','add','sub')
        if (logic is not None):
            regl = self.match('registers')
            self.char(',')
            regr = self.match('registers')
            return {'op': logic, 'reg': regl, 'regr':regr, 'size':1}




        return None


    def  mov(self):
        if (self.keyword('mov') is not None):
                regl = self.match('registers')
                self.char(',')
                regr = self.match('registers')
                return {'op': 'mov', 'reg':regl, 'regr': regr,'size':1}
        return None

    def registers(self):
            self.char('r')
            return int(self.char('0-3'))

    def registers16(self):
            return self.keyword('sp')

    def  movi(self):
        if (self.keyword('movi') is not None):
                regl = self.match('registers')
                self.char(',')
                data = self.match('number')
                return {'op':'movi','reg':regl, 'data': data,'size':2}
        return None

    def labelstr(self):
        chars=[]
        chars.append(self.char('A-Za-z0-9_'))
        while True:
            char = self.maybe_char('A-Za-z0-9_')
            if char is None:
                    break
            chars.append(char)

        return ''.join(chars)

    def label(self):
        self.char(':')
        return {'op':'label', 'data': self.labelstr(), 'size' : 0}



    def metaop(self):
        op = self.maybe_char('.')
        if (op is not None):
            return self.match('definedata','origin','end')
        return None

    def number(self):
        rv = self.match('binarynumber','hexnumber','octalnumber','decnumber')
        return rv


    def definedata(self):
        op = self.match('db','dw','ds')
        if (op is not None):
            v = self.match('number')
            return {'data': v,'op':op, 'size': 1 if op == 'db' else 2 if op == 'dw' else v}
        return None

    def ds(self):
        return self.keyword('ds')

    def db(self):
        return self.keyword('db')

    def dw(self):
        return self.keyword('dw')

    def origin(self):
        op = self.keyword('org')
        if (op is not None):
            return {'op':'org', 'data':self.match('number'), 'size':0}
        return None


    def end(self):
        op = self.keyword('end')
        if (op is not None):
            return {'op':'end', 'size':0}
        return None



    def octalnumber(self):
        chars = []
        chars.append(self.char('0'))
        chars.append(self.char('o'))
        chars.append(self.char('0-7'))

        while True:
            char = self.maybe_char('0-7')
            if char is None:
                    break
            chars.append(char)

        return int(''.join(chars),8)

    def binarynumber(self):
        chars = []

        chars.append(self.char('0'))
        chars.append(self.char('b'))
        chars.append(self.char('0-1'))

        while True:
            char = self.maybe_char('0-1')
            if char is None:
                    break
            chars.append(char)

        return int(''.join(chars),2)



    def hexnumber(self):
        chars = []
        chars.append(self.char('0'))
        chars.append(self.char('x'))
        chars.append(self.char('0-9A-Fa-f'))

        while True:
            char = self.maybe_char('0-9A-Fa-f')
            if char is None:
                    break
            chars.append(char)


        return int(''.join(chars),16)


    def decnumber(self):
        chars = []
        sign = self.maybe_keyword('+', '-')
        if sign is not None:
            chars.append(sign)

        chars.append(self.char('0-9'))

        while True:
            char = self.maybe_char('0-9')
            if char is None:
                break

            chars.append(char)


        rv = int(''.join(chars))
        return rv


if __name__ == '__main__':

    class SyntaxError(Exception):
        def __init__(self, msg, pos):
            self.msg = msg
            self.pos = pos

        def __str__(self):
            return f'{self.msg} at line {self.pos}'


    def processlabels(ops,labels):
        if (op['op'] == 'label'):
            labelnm = op['data']
            addr = op['pc']
            if (labelnm in labels):
                raise SyntaxError('Replicated label',op['line'])
            labels[labelnm] = addr


    def info(str,end=None):
        print(str,end='')

    # ** Main Process Starts here ***
    parser = AssemblerParser()
    pc = 0
    line = 0
    code = []
    labels = {}

    asm = open("test.asm", "r")
    while True:
        try:

            text = asm.readline()
            if len(text) == 0:
                break
            line = line + 1
            op = parser.parse(text.strip())
            if (op is not None):
                op['line'] = line
                code.append(op)
                if (op['op'] == 'end'):
                    break
        except KeyboardInterrupt:
            pass
        except (EOFError, SystemExit):
            break
        except IndexError as e:
            print(f'Error: {e} Line {line}')
        except (ParseError, ZeroDivisionError) as e:
            print(f'Error: {e} Line {line}')


    # Parsing complete

    try:

        # Pre-process build a symbol address table
        for op in code:
            if (op['op'] == 'org'):
                pc = op['data']
            op['pc'] = pc
            pc += op['size']
#info(op,"\n")
            processlabels(op,labels)

        for lbl in labels:
            info(f"'{lbl}': 0x{labels[lbl]:04x}\n")

        # now build up binary version of our code
        builder = Builder(labels)
        binarray = []
        for op in code:
            bytearray = builder.build(op)
            binarray+=bytearray

        for index,op in enumerate(binarray):
            info(f"{op:02x}",end='')
            if (index % 8 == 7):
                info("\n")
        info("\n")

        info(f"final size {len(binarray)} bytes\n")

    except (SyntaxError) as e:
        print(f"{e}")
