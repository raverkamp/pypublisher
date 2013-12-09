#PyPublisher

##Abstract

PyPublisher is a Python system to create wrappers for Oracle stored procedures with complex arguments. 
The atomic datatypes varchar2, date,raw and number ares upported as well as records and tables (normal and associative). 
PyPublisher depends on cx_Oracle. 

##Example

A small example, given the PL/SQL Package

```
create or replace package pypublisher_demo as
   type r is record(a varchar2(2000),
                    b number,
                    c date);

   type r_array is table of r;

   procedure proc(x r_array, y out r_array) ;
end;
```

and a configuration in Python 
```
from pypublisher import (Record,Table,Procedure,Date,Number,Varchar2)

r = Record("pypublisher_demo.r","r_record",
           [("a",Varchar2(2000)),
            ("b",Number()),
            ("c",Date())])

type r_array = Table("pypublisher_demo.r_array",r)

proc = Procedure("pypublisher_demo.proc","pypublisher_demo_proc",
        [Argument("x","in",r_array),
         Argument("y","out",r_array)])

generate_all([proc],"pypublisher_demo","some directory",
    "name of a wrapper package","some dir","sqlplus login",testdir,dblogin)
```

a Python Module is created which contains a definition for a class corresponding 
to the PL/SQL record `pypublisher_demo.r` and and a class which contains the method 
which wraps `pypublisher_demo.proc`. Assume is con is a `cx_Oracle.connection` object: 

```
import pypublisher_demo
import decimal
import datetime

p = pypublisher_demo.pypublisher_demo(con)
a = pypublisher_demo.r_record()
a.a ="some text"
a.b = decimal.Decimal("123.45")
c.d = datetime.datetime(2007,3,8,10,4,5)

res = p.([a])
print(res)
```