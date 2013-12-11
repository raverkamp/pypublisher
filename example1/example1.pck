create or replace package example1 as
   type r is record(a varchar2(2000),
                    b number,
                    c date);

   type r_array is table of r;

   procedure proc(x r_array, y out r_array) ;
end;
/
create or replace package body example1 as
   procedure proc(x r_array, y out r_array) is
     res r_array;
   begin
     if x is null then
       y:=null;
     elsif x.count=0 then
       y:= r_array();
     else
       y:= r_array();
       for i in x.first .. x.last loop
         y.extend();
         y(i):= x(x.last -i+1);
       end loop;
     end if;
   end;
end;
/
