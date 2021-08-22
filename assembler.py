#!/usr/bin/env python3

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
        rv = self.start()
        self.assert_end()
        return rv

    def assert_end(self):
        if self.pos < self.len:
            raise ParseError(
                self.pos + 1,
                'Expected end of string but got %s',
                self.text[self.pos + 1]
            )

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
        return self.testme()

    def testme(self):
        rv = self.match('instruction','label','metaop')
        return rv

    def instruction(self):
        return self.match('alu','movi','mov','ldi','call','singlebyte','singleop','out','djnz')

    def singleop(self):
        op = self.keyword('exx','pushall','popall','ret')
        if (op is not None):
            return {'op': op, 'size':1, 'code': [0]}
        return None

    def out(self):
        op = self.keyword('out','push','shl','shr')
        if (op is not None):
            reg = self.match('registers')
            return {'op': op, 'reg':reg, 'size':1, 'code': [0]}
        return None

    def singlebyte(self):
        op = self.keyword('inc','dec')
        if (op is not None):
            reg = self.match('registers','registers16')
            return {'op': op, 'reg':reg, 'size':1, 'code': [0]}
        return None


    def djnz(self):
        op = self.keyword('djnz')
        if (op is not None):
            reg = self.match('registers')
            self.char(',')
            data = self.match('number','labelstr')
            return {'op': op, 'reg': reg,'addr':data, 'size':3, 'code': [0]}
        return None

    def call(self):
        op = self.keyword('call','jmp','jpz','jpnz','jpc','jpnc')
        if (op is not None):
            data = self.match('number','labelstr')
            return {'op': op, 'addr':data, 'size':3, 'code': [0]}
        return None


    def ldi(self):
        op = self.keyword('ldi','st')
        if (op is not None):
            regl = self.match('registers','registers16')
            self.char(',')
            data = self.match('number','labelstr')
            return {'op': op, 'regl': regl, 'data':data, 'size':3, 'code': [0]}
        return None


    def alu(self):

        logic = self.keyword('andi','ori','xori','addi','subi')
        if (logic is not None):
            regl = self.match('registers')
            self.char(',')
            data = self.match('number','label')
            return {'op': logic, 'regl': regl, 'data':data, 'size':2, 'code': [0]}

        logic = self.keyword('and','or','xor','add','sub')
        if (logic is not None):
            regl = self.match('registers')
            self.char(',')
            regr = self.match('registers')
            return {'op': logic, 'regl': regl, 'regr':regr, 'size':1, 'code': [0]}


        return None


    def  mov(self):
        if (self.keyword('mov') is not None):
                regl = self.match('registers')
                self.char(',')
                regr = self.match('registers')
                return {'op': 'mov', 'data': {'rl':regl, 'rr': regr},'size':1,'code':[0]}
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
                return {'op':'movi','date':{'rl':regl, 'data': data},'size':2,'code':[0]}
        return None

    def labelstr(self):
        chars=[]
        chars.append(self.char('A-Za-z'))
        while True:
            char = self.maybe_char('A-Za-z_')
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
        op = self.match('db','dw')
        if (op is not None):
            return {'data': self.match('number'),'op':op, 'size': 1 if op == 'db' else 2}
        return None

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
        self.char('o')

        while True:
            char = self.maybe_char('0-7')
            if char is None:
                    break
            chars.append(char)

        return int(''.join(chars),8)

    def binarynumber(self):
        chars = []
        self.char('b')

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
    parser = AssemblerParser()
    pc = 0
    code = []
    asm = open("test.asm", "r")

    while True:
        try:
            text = asm.readline()
            #print("<<<<",text)
            op = parser.parse(text)
            #op = parser.parse(input('> '))
            code.append(op)
            op['pc'] = pc
            pc += op['size']
            if (op['op'] == 'end'):
                # completed  - resolve labels
                for op in code:
                    print(op)
                break

        except KeyboardInterrupt:
            pass
        except (EOFError, SystemExit):
            break
        except (ParseError, ZeroDivisionError, IndexError) as e:
            #print('Error: %s' % e)
            pass
