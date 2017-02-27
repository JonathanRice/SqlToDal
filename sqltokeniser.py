"""sqltokeniser.py
Author Jonathan Rice

This tokenises a SQL select, update, delete, or insert statement
"""

import ply.lex as lex

keywords = {
   'distinct' : 'DISTINCT', 'count' : 'COUNT',      'sum' : 'SUM',          'min' : 'MIN',
   'max' : 'MAX',           'avg' : 'AVG',          'substr' : 'SUBSTR',    'greatest' : 'GREATEST',
   'decode' : 'DECODE',     'concat' : 'CONCAT',    'select' : 'SELECT',    'update' : 'UPDATE',
   'insert' : 'INSERT',     'delete' : 'DELETE',    'from' : 'FROM',        'where' : 'WHERE',
   'having' : 'HAVING',     'by' : 'BY',            'order' : 'ORDER',      'for' : 'FOR',
   'asc' : 'ASC',           'desc' : 'DESC',        'and' : 'AND',          'or' : 'OR',
   'into' : 'INTO',         'values' : 'VALUES',    'set' : 'SET',          'is' : 'IS',
   'null' : 'NULL',         'not' : 'NOT',          'like' : 'LIKE',        'left' : 'LEFT',
   'right' : 'RIGHT',       'on' : 'ON',            'in' : 'IN',			'join' : 'JOIN'
}

# List of token names.
tokens = [
   'NUMBER',    'PLUS',     'MINUS',    'TIMES',    'DIVIDE',   'LPAREN',   'RPAREN',   'SQUOTEDSTR',
   'FUNCTION',  'SQLBEGIN', 'WORD',     'DOT',      'EQUAL',    'NOTEQUAL', 'LTHAN',    'GTHAN',
   'COMMA',     'GTHANEQ',  'LTHANEQ'
] + keywords.values()
# Regular expression rules for simple tokens
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_SQUOTEDSTR= r"'[^']*'"
t_DOT       = r'\.'
t_EQUAL     = r'='
t_NOTEQUAL  = r'<>'
t_LTHAN     = r'<'
t_GTHAN     = r'>'
t_GTHANEQ   = r'>='
t_LTHANEQ   = r'<='
t_COMMA     = r','

precedence = (
    ('left', 'FUNCTION'),
    ('left', 'WORD'),
    ('left', 'COMMA'),
)

def t_WORD(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keywords.get(t.value, 'WORD')
    return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    try:
         t.value = int(t.value)    
    except ValueError:
         print "Line %d: Number %s is too large!" % (t.lineno,t.value)
         t.value = 0
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule TODO change this to abort when it is called
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

def SetSQL(sql):
    lex.input(sql)

def GetToken():
    return lex.token()


lex.lex(nowarn=True)
#Un comment out to test

# Test it out
data = """
select foo.rock from foo where rock = '' % foo
"""

# Give the lexer some input
#lex.input(data)

# Tokenize
#while 1:
#    tok = lex.token()
#    if not tok: break      # No more input
#    print tok
