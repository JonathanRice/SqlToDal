"""SqlParser.py 
Author Jonathan Rice

This parses a SQL select, update, delete, or insert statement
"""
import sys
import ply.lex as lex
import ply.yacc as yacc

from SqlTokeniser import *
from SqlAbstractSyntaxTree import *

# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input! " + str(p)
    print """You have managed to break the program, if you are using
a valid SQL statement please send the statement to
Jonathan Rice, sorry for the trouble."""
    sys.exit(1)
    
def p_statement(p):
    """statement : insertstatement
                 | deletestatement
                 | updatestatement
                 | selectstatement"""
    p[0] = p[1]
#Main insert statement
def p_insert(p):
    'insertstatement : INSERT INTO WORD LPAREN columnlist RPAREN VALUES LPAREN valuelist RPAREN'
    p[0] = InsertStatement(p[3], p[5], p[9])

def p_columnlist(p):
    'columnlist : qualcolumn opcolumn'
    p[0] = InsertColumnList('columnlist', [p[1], p[2]])
    
def p_opcolumn(p):
    """opcolumn : COMMA columnlist
                | empty"""
    if len(p) >= 3:
        p[0] = p[2] #this will be a columnlist
    else:
        p[0] = p[1] # this will be null 
def p_valuelist(p):
    """valuelist : NUMBER opvalue
                 | SQUOTEDSTR opvalue"""
    p[0] = InsertValueList('columnlist', [p[1], p[2]])
    
def p_opvalue(p):
    """opvalue : COMMA valuelist
               | empty"""
    if len(p) >= 3:
        p[0] = p[2] #this will be a columnlist
    else:
        p[0] = p[1] # this will be null
#Main delete statement
def p_delete(p):
    'deletestatement : DELETE FROM WORD whereclause'
    p[0] = DeleteStatement(p[3], p[4])
# Main update statement
def p_update(p):
    'updatestatement : UPDATE WORD setclause whereclause'
    p[0] = UpdateStatement(p[2], p[3], p[4])
    
def p_setclause(p):
    'setclause : SET assignlist'
    p[0] = p[2]
    
def p_assign_list(p):
    'assignlist : assign opassignlist'
    p[0] = UpdateAssignList('assignlist', [p[1], p[2]])

def p_opassign_list(p):
    """opassignlist : COMMA assignlist
                    | empty"""
    if len(p) >= 3: 
        p[0] = p[2] #this will be the assignlist
    else:
        p[0] = p[1] # this will be null  
    
def p_assign(p):
    """assign : qualcolumn EQUAL SQUOTEDSTR
              | qualcolumn EQUAL NUMBER"""
    p[0] = Assign('assign', [p[1], p[3]])
# Main select statment
def p_select(p):
    'selectstatement : SELECT selectlist FROM fromlist whereclause orderby forupdate'
    p[0] = SelectStatement(p[2], p[4], p[5], p[6], p[7])
#
# fromlist Section
#
def p_from_list(p):
    "fromlist : WORD opfrom"
    p[0] = FromList('fromlist', [p[1], p[2]])
    
def p_opfrom(p):
    """opfrom : COMMA fromlist
              | empty"""
    if len(p) >= 3:
        p[0] = p[2] #this will be the fromlist
    else:
        p[0] = p[1] # this will be null    
#
# END fromlist section
#
def p_qual_column(p):
    """qualcolumn : WORD DOT WORD"""
    p[0] = QualColumn('qualcolumn', [p[1], p[3]])
    
def p_select_list(p):
    """selectlist :  singleselect opselect"""
    p[0] = SelectList('selectlist', [p[1], p[2]])

def p_opselect(p):
    """opselect : COMMA selectlist
                | empty"""
    if len(p) >= 3:
        p[0] = p[2] #this will be a selectlist
    else:
        p[0] = p[1] # this will be null 
def p_single_select(p):
    """singleselect : qualcolumn
                    | function"""
    p[0] = p[1]

def p_function(p):
    """function : functionname LPAREN singleselect RPAREN
                | functionname LPAREN WORD RPAREN
                | functionname LPAREN NUMBER RPAREN"""
    p[0] = FunctionNode('function', [p[1], p[3]])

def p_function_name(p):
    """functionname : DISTINCT
                    | COUNT
                    | SUM
                    | MIN
                    | MAX
                    | AVG
                    | SUBSTR
                    | GREATEST
                    | DECODE
                    | CONCAT"""
    p[0] = p[1]
def p_optional_where(p):
    """whereclause : WHERE conditionlist
             | empty"""
    if len(p) == 2: # the where option was not used
        p[0] = p[1]
    else:
        p[0] = p[2] # return the condition

def p_condition_group(p):
    """conditionlist : LPAREN conditionlist RPAREN"""
    p[0] = ConditionGroup(p[2])
            
def p_condition_list(p):
    """conditionlist : condition opcondition"""
    p[1].ChildNode = p[2]
    p[0] = p[1]

def p_opcondition(p):
    """opcondition : AND conditionlist
                   | OR conditionlist
                   | empty"""
    if len(p) >= 3: # we have a condition set the join type accordingly
        p[2].JoinType = p[1]
        p[0] = p[2]
    else:
        p[0] = p[1] # we have a null
    
def p_condition(p):
    """condition : operand EQUAL operand
                 | operand NOTEQUAL operand
                 | operand GTHAN operand
                 | operand LTHAN operand
                 | operand GTHANEQ operand
                 | operand LTHANEQ operand
                 | operand LIKE operand
    """
    p[0] = Condition(p[1], p[2], p[3])
    
def p_condition_in(p):
    """condition : operand IN LPAREN selectstatement RPAREN"""
    p[0] = Condition(p[1], p[2], p[4])
def p_condition_not_in(p):
    """condition : operand NOT IN LPAREN selectstatement RPAREN"""
    p[0] = Condition(p[1], p[2] + p[3], p[5])
    
def p_condition_is_null(p):
    """condition : operand IS NULL"""
    p[0] = Condition(p[1], p[2], True)
    
def p_condition_is_not_null(p):
    """condition : operand IS NOT NULL"""
    p[0] = Condition(p[1], p[2], False)

def p_operand_qual_column(p):
    """operand : qualcolumn"""
    p[0] = p[1]
def p_operand_number(p):
    """operand : NUMBER"""
    p[0] = InputVariable(p[1])
def p_operand_quoted(p):
    """operand : SQUOTEDSTR"""
    unQuotedStr = p[1]
    unQuotedStr = unQuotedStr[1:]
    unQuotedStr = unQuotedStr[0:len(unQuotedStr) - 1]
    p[0] = InputVariable(unQuotedStr) #p[0] = p[1] #TODO add support for DALInputHostVar

def p_optional_for_update(p):
    """forupdate : FOR UPDATE
             | empty"""
    if len(p) >= 3: # the for update option is used
        p[0] = True
    else:
        p[0] = False # do not use for update
        
def p_optional_orderby(p):
    """orderby : ORDER BY orderbylist
             | empty"""
    if len(p) >= 3: # the where option was not used
        p[0] = p[3]
    else:
        p[0] = p[1] # return empty

def p_orderby_list(p):
    """orderbylist : qualcolumn oporderbylist"""
    p[0] = OrderByList('asc', [p[1], p[2]])
def p_orderby_list_asc(p):
    """orderbylist : qualcolumn ASC oporderbylist"""
    p[0] = OrderByList('asc', [p[1], p[3]])
def p_orderby_list_desc(p):
    """orderbylist : qualcolumn DESC oporderbylist"""
    p[0] = OrderByList('desc', [p[1], p[3]])
def p_oporderby_list(p):
    """oporderbylist : COMMA orderbylist
                    | empty"""
    if len(p) >= 3:
        p[0] = p[2] #this will be a selectlist
    else:
        p[0] = p[1] # this will be null 
                    
def p_empty(p):
    "empty :"
    pass
# Build the lexer
yacc.yacc()

def makeSQLLower(sql):
    """For simplicity of parsing the sql should be made lower case.  However entries in 's should retain there case"""
    firstPos = sql.find("'")
    if firstPos < 0: #There are no quoted strings just make the whole thing lower case
        return sql.lower()
    before = sql[:firstPos] #this is everythin before the initial quote
    secondPos = sql.find("'", firstPos + 1)
    if secondPos < 0: #there was not a second quote this will become an error just lower everythin
        return sql.lower()
    return before.lower() + sql[firstPos:secondPos + 1] + makeSQLLower(sql[secondPos + 1:])

def GetASTFromSql(sql):
    return yacc.parse(makeSQLLower(sql))
#blah = yacc.parse("select sum(distinct(boo.boo)), foo.foo, avg(rar.rar) from dual, user_master, foo where boo.boo is not null and foo.foo = 'fooya' and boo.boo = foo.foo and foo.foo in (select moo.moo from boo) order by foo.foo")
#blah = yacc.parse("update tablename set foo.boo = 'foo', moo.moo = 300, arg.marg = 'large.farge' where boo.boo = foo.foo")
#blah = yacc.parse("delete from boo where boo.boo = foo.foo")
#blah = yacc.parse("insert into table (table.boo, table.moo, table.goo) values ('1020232', 3340, '102320')")

#print blah.AssignList.GetArrayFromList()[1].GetAssignmentValue()
#print blah.children[1].type
#print blah.children[3].GetFromList()
#print blah.children[1].GetArrayFromList()
#print blah.children[4].GetConditionJoinArray()