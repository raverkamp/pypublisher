create or replace type test_object as object
(

  x varchar2(2000),
  y number,
  z date
 
) not final
/

create or replace type number_array as table of number;
/

create or replace type string_array as table of varchar2(2000);
/

create or replace type test_object2  under test_object
(
  v varchar2(200)
)
/
