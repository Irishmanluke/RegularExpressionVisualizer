from FSM import FSM

def parse(s):
    rgp = RegExParser(s)
    fsm = rgp.parse()

    return fsm

class RegExParser:
    def __init__(self, s):
        self.i=0;
        self.s = s

    def next(self):
        self.i += 1

    def token(self):
        if self.i < len(self.s):
            return self.s[self.i]
        else:
            return None

    def parse(self):
        fsm = self.expr()
        if self.token():
            raise ValueError
        return fsm

    def expr(self):
        fsm = self.term()
    
        while self.token() == "|": 
            self.next()
            fsm.unionize(self.term())
    
        return fsm
    
    def term(self):
        if self.token() not in {"|",")",None}:
            fsm = self.factor()
        else:
            fsm = FSM("")
 
        while self.token() not in {"|",")",None}:
            fsm.concatenate(self.factor())
    
        return fsm
    
    def factor(self):
        fsm = self.atom()
        if self.token() == "*":
            fsm.close()
            while self.token() == "*":
                self.next()
    
        return fsm

    def atom(self):
        if self.token() == "(":
            self.next()
            fsm = self.expr()
            if self.token() == ")":
                self.next()
            else:
                raise ValueError

        elif self.token() not in {")","|","*"}:
            fsm = FSM(self.token())
            self.next()
        else:
            raise ValueError

        return fsm
