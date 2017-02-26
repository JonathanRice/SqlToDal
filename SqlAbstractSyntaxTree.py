"""SqlAbstractSyntaxTree.py 
Author Jonathan Rice

This will define the classes and structures that will make up a SQL abstract syntax tree"""

class Node:
    """This is the fundamental unit of the abstract syntax tree."""
    def __init__(self,type = 'NoType' ,children=None,leaf=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]
         self.leaf = leaf

class LinkedList(Node):
    """This assumes the nodes are arranged in the fashion of a linked list."""
    def GetArrayFromList(self):
        arr = []
        arr.append(self.children[0])
        if self.children[1] != None:
            arr += self.children[1].GetArrayFromList()
        return arr
    def ensureChild(self):
        return len(self.children) >= 2 and self.children[1] != None
class FromList(LinkedList):
    def GetFromList(self):
        return self.GetArrayFromList()
class InputVariable:
    """This represent a constant SQL input variable.  It has function for declaring itself and maintaining unique names"""
    currentId = 0
    def __init__(self, value):
        InputVariable.currentId += 1
        self.Value = value
        self.VarName = 'replace' + str(value) + str(InputVariable.currentId)
        self.HVVarName = 'HV' + self.VarName
        if isinstance(self.Value, str): 
            self.VarType = 'RWTString'
        else:
            self.VarType = 'float '
    def GetInputAssignmentCode(self):
        code = self.VarType + ' ' + self.VarName + ' = '
        if self.VarType == 'RWTString':
            code = code + 'TEXT("' + self.Value + '");\n'
        else:
            code = code + str(self.Value) + ';\n'
        code = code + 'DALInputHostVar ' + self.HVVarName + '(' + self.VarName + ');\n'
        return code 
class InsertColumnList(LinkedList):
    """A Naming convention for the column list in an insert statement"""
    pass
class InsertValueList(LinkedList):
    """A Naming convention for the values in an insert statement"""
    pass
class FunctionNode(LinkedList):
    """This represents a select or conditional SQL function statement"""
    def GetTableColumnName(self):
        if not self.ensureChild():
            return "ErrorNoColumnDefined"
        return self.children[1].GetTableColumnName()
    def GetSelectCode(self):
        if not self.ensureChild():
            return "ErrorNoColumnDefined"
        return 'DAL::' + self.children[0] + '(' + self.children[1].GetSelectCode() + ')'
class QualColumn(LinkedList):
    """Represents a table.column qualified SQL column"""
    def GetTable(self):
        return self.children[0]
    def GetColumn(self):
        return self.children[1]
    def GetDalName(self):
        table = ToDalTableName(self.GetTable())
        dalName = 'Db' + table + '::'
        column = ToDalTableName(self.GetColumn())
        dalName = dalName + column
        return dalName
    def GetTableColumnName(self):
        return ToDalTableName(self.GetTable()) + ToDalTableName(self.GetColumn())
    def GetSelectCode(self):
        return ToDalTableVarName(self.GetTable()) + '[' + self.GetDalName() + ']'
    def GetSubQueryName(self):
        return self.SubQueryName
    def GetSubQuerySelectCode(self, prefix = 'sq'):
        return prefix + self.GetSelectCode()
    def GetInputAssignmentCode(self):
        return ''
    def SetSubQueryName(self, subQueryName):
        self.SubQueryName = subQueryName
class SelectList(LinkedList):
    pass
class OrderByList(LinkedList):
    def GetSelectCode(self, statementVarName = 'statement'):
        dalSort = 'DAL_SORTDESCENDING'
        qualCol = self.children[0]
        if self.type == 'asc':
            dalSort = 'DAL_SORTASCENDING'
        code = statementVarName + '.addOrderBy(' + ToDalTableVarName(qualCol.GetTable()) + '[' + qualCol.GetDalName() + '], ' + dalSort + ');\n'
        if self.ensureChild():
            code = code + self.children[1].GetSelectCode()
        return code
class Assign(LinkedList):
    def GetTableName(self):
        return self.children[0].children[0]
    def GetColumnName(self):
        return self.children[0].children[1]
    def GetAssignmentValue(self):
        return self.children[1]
    def GetDalTableColumnName(self):
        """This will return DbCartonDtl::InvnType if that is the column to be assigned"""
        table = ToDalTableName(self.GetTableName())
        dalName = 'Db' + table + '::'
        column = ToDalTableName(self.GetColumnName())
        dalName = dalName + column
        return dalName
class UpdateAssignList(LinkedList):
    pass

class Condition:
    def __init__(self, left, operator, right, childNode = None, joinType = None):
        self.Left = left
        self.Operator = operator
        self.Right = right
        self.JoinType = joinType
        self.ChildNode = childNode
        self.VarPrefix = ''
        self.SubQueryVarName = ''
        self.Owner = None
    def GetConditionJoinArray(self):
        arr = []
        arr.append(self)
        if self.ChildNode != None:
            arr.append(self.ChildNode.JoinType)
            arr += self.ChildNode.GetConditionJoinArray()
        return arr
    def GetConditionCode(self, owningStatement = None, subQueryVarName = '', varPrefix = '', condVarName = 'cond'):
        self.VarPrefix = varPrefix
        self.SubQueryVarName = subQueryVarName
        code = self.writeSubQuery(owningStatement)
        code = code + self.writeInputVarDecl()
        code = code + 'DALCondition ' + varPrefix + condVarName + '(\n'
        code = code + self.writeConditionCode(self.SubQueryVarName, self.VarPrefix)
        code = code + '\n);\n'
        return code
    def writeInputVarDecl(self):
        code = ''
        if hasattr(self.Left, "GetInputAssignmentCode"):
            code = code + self.Left.GetInputAssignmentCode()
        if hasattr(self.Right, "GetInputAssignmentCode"):
            code = code + self.Right.GetInputAssignmentCode()
        if self.ChildNode != None:
            code = code + self.ChildNode.writeInputVarDecl()
        return code
    def writeSubQuery(self, owner):
        code = ''
        if self.Operator.lower() in ('in', 'notin'):
            code = code + self.Right.GetSubQueryCode(owner.GetStatementVarName())
            self.Left.SetSubQueryName(self.Right.SubQueryVarName)
        if self.ChildNode != None:
            code = code + self.ChildNode.writeSubQuery(owner)
        return code
    def writeConditionCode(self, subQueryVarName = '', varPrefix = ''):
        """Main recursive conditional code should return
        table[foo::foo] == DALINputHostVar('fjdksjfl') &&
        more of above if it is their"""
        self.SubQueryVarName = subQueryVarName
        self.VarPrefix = varPrefix
        code = ''
        if self.Operator.lower() == 'like':
            code = code + self.__writeLike()
        elif self.Operator.lower() == 'is':
            code = code + self.__writeIs()
        elif self.Operator.lower() == 'in':
            code = code + self.__writeIn()
        elif self.Operator.lower() == 'notin':
            code = code + self.__writeNotIn()
        else:
            code = code + self.__writeOperand(self.Left)
            code = code + self.__writeOperator(self.Operator)
            code = code + self.__writeOperand(self.Right)
        if self.ChildNode != None:
            code = code + self.__writeCondJoin(self.ChildNode.JoinType)
            code = code + self.ChildNode.writeConditionCode(self.SubQueryVarName, self.VarPrefix)
        return code
    def __writeOperand(self, operand):
        code = ''
        if operand == None: return code
        if isinstance(operand, QualColumn):
            code = self.VarPrefix + ToDalTableVarName(operand.GetTable()) + '[' + operand.GetDalName() + ']'
        else:
            code = operand.HVVarName
        return code
    def __writeLike(self):
        code = self.__writeOperand(self.Left)
        code = code + '.like(' + self.Right + ')'
        return code
    def __writeIs(self):
        code = self.__writeOperand(self.Left)
        if self.Right:
            code = code + '.isNull()'
        else:
            code = code + '.isNotNull()'
        return code
    def __writeIn(self):
        return self.__writeOperand(self.Left) + '.in(' + self.Left.GetSubQueryName() + ')'
    def __writeNotIn(self):
        return self.__writeOperand(self.Left) + '.notIn(' + self.Left.GetSubQueryName() + ')'
    def __writeOperator(self, operator):
        code = ''
        operator = operator.lower()
        if operator == None: return code
        if operator == '=':
            code = ' == '
        elif operator == '<>':
            code = ' != '
        else:
            code = ' ' + operator + ' '
        return code
    def __writeCondJoin(self, joinType):
        code = ''
        if joinType == None: return code
        joinType = joinType.lower()
        if joinType == 'or':
            code = ' ||\n'
        elif joinType == 'and':
            code = ' &&\n'
        return code
    
class ConditionGroup(Condition):
    def __init__(self, cond):
        Condition.__init__(self, cond.Left, cond.Operator, cond.Right, cond.ChildNode, cond.JoinType)
    def writeConditionCode(self, subQueryVarName = '', varPrefix = ''):
        return ' ( \n' + Condition.writeConditionCode(self, subQueryVarName, varPrefix) + '\n ) '
        
class Statement:
    def GetSQL(self):
        pass
    def GetStatementVarName(self):
        return 'statement'
class SelectStatement(Statement):
    SubQueryId = 0
    def __init__(self, selectList, tableList, whereCondition = None, orderBy = None, forUpdate = False):
        self.SelectList = selectList
        self.TableList = tableList
        self.WhereCondition = whereCondition
        self.OrderBy = orderBy
        self.ForUpdate = forUpdate
        self.id = 0    
        self.SubQueryVarName = ''    
    def GetSQL(self):
        self.code = self.__createObjectAndTable()
        self.code = self.code + self.__addSelects()
        self.code = self.code + self.__createConditionCode()
        self.code = self.code + self.__addOrderBy()
        self.code = self.code + self.__finalizeCode()
        return self.code
    def __createObjectAndTable(self):
        """This will create the DALUpdate variable assign the trans to it, and create the needed table"""
        code = "DALSelect " + self.GetStatementVarName() + "(*(trans->getDALTransaction()));\n"
        tableArr = self.TableList.GetArrayFromList()
        for table in tableArr:
            code = code + 'DALTable ' + ToDalTableVarName(table) + '(DALTables::' + ToDalTableName(table) + ');\n'
        return code
    def __createConditionCode(self):
        if self.WhereCondition == None:
            return ''
        return self.WhereCondition.GetConditionCode(self)
    def __addSelects(self):
        code = ''
        selectArr = self.SelectList.GetArrayFromList()
        for select in selectArr:
            code = code + self.__addIndividualSelect(select)
        return code
    def __addIndividualSelect(self, select):
        outVarName = select.GetTableColumnName()
        hvName = 'hv' + outVarName
        rwtName = 'st' + outVarName
        code = 'RWTString ' + rwtName + ';\n'
        code = code + 'DALHostVar ' + hvName + '(' + rwtName + ');\n'
        code = code + self.GetStatementVarName() + '.addSelect(' + select.GetSelectCode() + ', ' + hvName + ');\n'
        return code
    def __addOrderBy(self):
        if self.OrderBy == None:
            return ''
        return self.OrderBy.GetSelectCode(self.GetStatementVarName())
    def __finalizeCode(self):
        code = self.GetStatementVarName() + '.where(cond);\n'
        if self.ForUpdate:
            code = code + self.GetStatementVarName() + '.withLock(TRUE);\n'
        code = code + self.GetStatementVarName() + '.execute();\n'
        code = code + "while(" + self.GetStatementVarName() + """.next())
{
//Do something with the output host variables here
// ie use the values of stTableColumn
}"""
        return code
    def GetSubQueryCode(self, statmentVarName = 'statement'):
        selectArr = self.SelectList.GetArrayFromList()
        varPrefix = 'sq' + str(SelectStatement.SubQueryId)
        self.SubQueryVarName = varPrefix + 'SubQuery' + selectArr[0].GetTableColumnName() #Change the way we do this so it is not infinetely recursive
        table = self.TableList.GetArrayFromList()[0]
        subQueryCondName = 'sqCond' + self.SubQueryVarName
        SelectStatement.SubQueryId += 1
        code = ''
        code = code + 'DALTable ' + varPrefix + ToDalTableVarName(table) + '(DALTables::' + ToDalTableName(table) + ');\n'
        code = code + 'DALSubquery ' + self.SubQueryVarName + '(' + statmentVarName + '.newSubquery());\n'
        code = code + self.SubQueryVarName + '.add_select(' + selectArr[0].GetSubQuerySelectCode(varPrefix) + ');\n'
        code = code + self.WhereCondition.GetConditionCode(self, self.SubQueryVarName, varPrefix, subQueryCondName)
        code = code + self.SubQueryVarName + '.where(' + varPrefix + subQueryCondName + ');\n'
        return code
    def GetInputAssignmentCode(self):
        return ''
    def GetStatementVarName(self):
        return 'select'
class UpdateStatement(Statement):
    def __init__(self, updateTable, assignList, whereCondition = None):
        self.Table = updateTable
        self.AssignList = assignList
        self.WhereCondition = whereCondition
    def GetSQL(self):
        """The Main function for updatestatement this will return the DAL c++ code"""
        self.code = self.__createObjectAndTable()
        self.code = self.code + self.__createAssign()
        self.code = self.code + self.__createConditionCode()
        self.code = self.code + self.__finalizeCode()
        return self.code
    def __createObjectAndTable(self):
        """This will create the DALUpdate variable assign the trans to it, and create the needed table"""
        code = "DALUpdate " + self.GetStatementVarName() + """(*(trans->getDALTransaction()));
DALTable """ + ToDalTableVarName(self.Table) + "(DALTables::"
        code = code + ToDalTableName(self.Table) + ');\n\n'
        return code
    def __createAssign(self):
        """This will iterate through the assign statemnet and generate code for them"""
        code = ''
        assignArr = self.AssignList.GetArrayFromList()  # This will give us an array of class Assign
        times = 0
        for assign in assignArr:
            times = times + 1 # keep track so we can give the replace variables a unique name
            code = code + self.__createSingleAssign(assign, times)
        return code
    def __createSingleAssign(self, assign, id = 0):
        """Given a signle assign and an id this will write corresponding code for it"""
        dataVariable = 'replace' + str(id)
        assignValue = str(assign.GetAssignmentValue())
        if assignValue.find("'") == 0: # if the string is quoted chop it off
            assignValue = assignValue[1:]
            assignValue = assignValue[0:len(assignValue) - 1]
        code = 'RWTString ' + dataVariable + ' = "' + assignValue + '";\n'
        code = code + self.GetStatementVarName() + '.addAssignment(DALAssignment(' + ToDalTableVarName(self.Table) +'[' + assign.GetDalTableColumnName() + '],DALHostVar(' + dataVariable + ')));\n' 
        return code
    def __createConditionCode(self):
        if self.WhereCondition == None:
            return ''
        return self.WhereCondition.GetConditionCode(self) + self.GetStatementVarName() + '.set_criteria(cond);\n'
    def __finalizeCode(self):
        return self.GetStatementVarName() + ".execute();"
    def GetStatementVarName(self):
        return 'update'
class InsertStatement(Statement):
    def __init__(self, insertTable, columnList, valueList):
        self.Table = insertTable
        self.ColumnList = columnList
        self.ValueList = valueList
    def GetSQL(self):
        self.code = self.__createObjectAndTable()
        self.code = self.code + self.__createAssignList()
        self.code = self.code + self.__finalizeCode()
        return self.code
    def __createObjectAndTable(self):
        """This will create the DALDelete variable assign the trans to it, and create the needed table"""
        code = "DALInsert " + self.GetStatementVarName() + "(*(trans->getDALTransaction()));\n"
        code = code + 'DALTableList table;\n'
        code = code + 'DALColumnList columns;\n'
        code = code + 'DALVarList values;\n'
        code = code + 'DALTable ' + ToDalTableVarName(self.Table) + '(DALTables::' + ToDalTableName(self.Table) + ');\n\n'
        return code
    def __createAssignList(self):
        code = ''
        columns = self.ColumnList.GetArrayFromList()
        values = self.ValueList.GetArrayFromList()
        times = 0
        if len(columns) != len(values):
            print 'Error Insert Column list is not the same size as the value list'
            return 'Error Insert Column list is not the same size as the value list'
        for i in range(0, len(columns)):
            times += 1 #increment the unique variable maker
            dataVariable = 'replace' + str(times)
            assignValue = str(values[i])
            if assignValue.find("'") == 0: # if the string is quoted chop it off
                assignValue = assignValue[1:]
                assignValue = assignValue[0:len(assignValue) - 1]
            inputHostVarName = ToDalVarName(columns[i].GetColumn()) + str(times)
            code = code + 'RWTString ' + dataVariable + ' = TEXT("' + assignValue + '");\n'
            code = code + 'DALInputHostVar ' + inputHostVarName + '(' + dataVariable + ');\n'
            code = code + 'DALColumn ' + ToDalColumnVarName(columns[i].GetColumn()) + ' = ' + ToDalTableVarName(self.Table) + '[' + columns[i].GetDalName() + '];\n'
            code = code + 'columns.append(&' + ToDalColumnVarName(columns[i].GetColumn()) + ');\n'
            code = code + 'values.append(&' + inputHostVarName + ');\n\n'
        return code
    def __finalizeCode(self):
        code = self.GetStatementVarName() + '.set_columns(columns);\n'
        code = code + self.GetStatementVarName() + '.set_values(values);\n'
        code = code + self.GetStatementVarName() + '.execute();\n'
        code = code + self.GetStatementVarName() + '.reset();\n'
        return code
    def GetStatementVarName(self):
        return 'insert'
class DeleteStatement:
    def __init__(self, deleteTable, whereCondition):
        self.Table = deleteTable
        self.WhereCondition = whereCondition
    def GetSQL(self):
        self.code = self.__createObjectAndTable()
        self.code = self.code + self.__createConditionCode()
        self.code = self.code + self.GetStatementVarName() + '.set_criteria(cond);\n'
        self.code = self.code + self.GetStatementVarName() + '.execute();'
        return self.code
    def __createObjectAndTable(self):
        """This will create the DALDelete variable assign the trans to it, and create the needed table"""
        code = "DALDelete " + self.GetStatementVarName() + """(*(trans->getDALTransaction()));
DALTable """ + ToDalTableVarName(self.Table) + "(DALTables::"
        code = code + ToDalTableName(self.Table) + ');\n'
        code = code + 'DALTableList tableList;\n'
        code = code + 'tableList.insert(&' + ToDalTableVarName(self.Table) + ');\n'
        code = code + self.GetStatementVarName() + '.set_table(tableList);\n\n'
        return code
    def __createConditionCode(self):
        if self.WhereCondition == None:
            return ''
        return self.WhereCondition.GetConditionCode(self)
    def GetStatementVarName(self):
        return 'del'
def ToDalVarName(column):
    return 'v' + ToDalTableName(column)    
def ToDalColumnVarName(column):
    return 'c' + ToDalTableName(column)
def ToDalTableVarName(table):
    return 'table' + ToDalTableName(table)     
def ToDalTableName(table):
    """This will turn carton_dtl into CartonDtl, and foo_boo_moo into FooBooMoo"""
    if table == None: return None
    underscorePos = table.find('_')
    if underscorePos == -1: #not found
        return table[0].upper() + table[1:]
    else:
        firstWord = table[0:underscorePos]
        theRest = table[(underscorePos + 1):]
        firstWord = firstWord[0].upper() + firstWord[1:]
        return firstWord + ToDalTableName(theRest)
    