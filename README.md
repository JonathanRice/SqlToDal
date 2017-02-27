#SqlToDal
Parse SQL statements into an abstract syntax tree (AST), then generate corresponding data abstration language (DAL) code.

##Example execution
~~~~
./sqltodal.py --sql="select user_master.login_user_id from user_master order by user_master.login_user_id desc for update"
~~~~
###Example output
~~~~
DALSelect select(*(trans->getDALTransaction()));
DALTable tableUserMaster(DALTables::UserMaster);
RWTString stUserMasterLoginUserId;
DALHostVar hvUserMasterLoginUserId(stUserMasterLoginUserId);
select.addSelect(tableUserMaster[DbUserMaster::LoginUserId], hvUserMasterLoginUserId);
select.addOrderBy(tableUserMaster[DbUserMaster::LoginUserId], DAL_SORTDESCENDING);
select.where(cond);
select.withLock(TRUE);
select.execute();
while(select.next())
{
//Do something with the output host variables here
// ie use the values of stTableColumn
}
~~~~

##Querks and usage warnings
This program is _NOT_ perfect please read the following warnings!
1. All SQL references to column names _MUST_ be qualified with their table name.  Another words tableName.columnName must be used instead of just columnName.
2. The select statement's having clause is not yet supported.
3. "In place" SQL mathematics is yet not supported. i.e. you cannot use table.column + table.diffcolumn, or (table.column * 3).
4. Do _not_ end the SQL statement with a ';' or '/'.
5. If you manage to break this with a valid SQL statement please send Jonathan Rice an email.
6. This program cannot handle stored proc calls.  select, update, delete, and insert only.
7. YACC will output to STDERR, so you may want to redirect the STDERR

##Example Working SQLs

SELECT person.person_id, person.first_name, person.last_name FROM person WHERE person.person_id IN ( SELECT employee.employee_id FROM employee WHERE employee.hire_date IS NOT NULL AND employee.employee_id ='JR070101' AND employee.type <>'Y' AND employee.region_id NOT IN(SELECT region.region_id FROM region where region.country_code='US' AND region.state_code='GA'))

insert into address (address.addr_id, address.addr_line_1, address.city, address.state, address.zip, address.cntry) values ('4565', '42 Foo St.', 'Bar Town', 'GA', '30309', 'US')

update person set person.gender = 'M', person.age = 40 where person.person_id in (select employee_id.employee_id from employee where type = 'SILTL21')

delete from person where person.first_name = 'Jonathan'

## Library usage
This program uses [ply](http://www.dabeaz.com/ply/) you should check it out.