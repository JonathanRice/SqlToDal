#SqlToDal
Parse SQL statements into an abstract syntax tree (AST), then generate corresponding data abstration language (DAL) code.

:>SqlToDal.py

This will show you the options and a list of issue to watch out for

Example SQLs:

SELECT person.person_id, person.first_name, person.last_name FROM person WHERE person.person_id IN ( SELECT employee.employee_id FROM employee WHERE employee.hire_date IS NOT NULL AND employee.employee_id ='JR070101' AND employee.type <>'Y' AND employee.region_id NOT IN(SELECT region.region_id FROM region where region.country_code='US' AND region.state_code='GA'))

insert into address (address.addr_id, address.addr_line_1, address.city, address.state, address.zip, address.cntry) values ('4565', '42 Foo St.', 'Bar Town', 'GA', '30309', 'US')

update person set person.gender = 'M', person.age = 40 where person.person_id in (select employee_id.employee_id from employee where type = 'SILTL21')

delete from person where person.first_name = 'Jonathan'

