#!/usr/bin/env python
"""SqlToDal.py 
Author Jonathan Rice

This will turn a generic sql into a c++ DAL statement
"""
import os
import sys
import getopt
import SqlParser
    
def SqlToDal(sql, outputFileName = 'main.cpp'):
    """Main point of interest pass this function a sql and it return the correcponding c++ DAL code"""
    output = ''
    ast = SqlParser.GetASTFromSql(sql) #Now we have an abstract syntax tree
    code = ast.GetSQL()
    print code
    methodCode = """void SqlToDal(const PkTransactionPtr& trans)
{
""" + code + "\n}"
    outFile = open(outputFileName, 'w')
    outFile.write(methodCode)
    outFile.close()

def usage():
    """Print usage"""
    print """SqlToDal v.1alpha written by Jonathan Rice aka Haxorius Maximus
This program will turn a generic sql into a c++ DAL statement.
This program is _NOT_ perfect please read the following warnings!
1) All SQL references to column names _MUST_ be qualified with
    their table name.  Another words tableName.columnName must
    be used instead of just columnName.
2) The select statement's having clause is not yet supported.
3) "In place" SQL mathematics is yet not supported. i.e. you cannot use
    table.column + table.diffcolumn, or (table.column * 3).
4) Do _not_ end the SQL statement with a ';' or '/'.
5) If you manage to break this with a valid SQL statement
    please send Jonathan Rice an email.
6) This program does not validate against the DALTableKeys,
    so it is possible to enter a sql the DAL cannot handle.
7) This program cannot handle stored proc calls.  select, update,
    delete, and insert only.
Usage:
    -h --help  Displays this screen
    -s --sql="sqlstatement"  The quotes are important
Example:
    SqlToDal.py --sql="select user_master.login_user_id from user_master order by user_master.login_user_id desc for update"
     """

def main(argv):
    """Main starting point"""
    try:
        opts, args = getopt.getopt(argv, "hs:", ["help", "sql="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    sql = None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-s", "--sql"):
            sql = arg
    if sql == None:
        usage()
        sys.exit(0)
    SqlToDal(sql)
    
if __name__ == "__main__":
    main(sys.argv[1:]) 
