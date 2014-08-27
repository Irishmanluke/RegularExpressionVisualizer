import sys

######   LEXER   ###############################

from ply import lex

tokens = (
    'BAR',
    'LPAREN',
    'RPAREN',
    'STAR',
    'SYMBOL'
)

t_BAR = r'\|'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_STAR = r'\*'
t_SYMBOL = r'.'

def t_error( t ):
  print "Illegal character '%s' on line %d" % ( t.value[0], t.lexer.lineno )
  return t
lex.lex()

######   LEXER (end)   ###############################


######   YACC   #####################################
from FSM import FSM
from ply import yacc

def p_expr( p ) :
    '''expr : term BAR expr
            | term'''

    if len(p) == 4:
        p[1].unionize(p[3])
    p[0] = p[1]

def p_term( p ) :
    '''term : factor term
            | '''
    if len(p) == 3:
        p[1].concatenate(p[2])
        p[0] = p[1]
    else:
        p[0] = FSM("")

def p_factor( p ) :
    '''factor :  atom closure_list
               | atom'''
    if len(p) == 3:
        p[1].close()
    p[0] = p[1]

def p_closure_list( p ) :
    '''closure_list : STAR closure_list 
                    | STAR'''

def p_atom( p ) :
    '''atom : LPAREN expr RPAREN
            | SYMBOL'''

    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = FSM(p[1])

# Error rule for syntax errors
def p_error( p ):
    raise ValueError

yacc.yacc()

def parse(s):
    return yacc.parse(s)
