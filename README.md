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
from generation import (Record,Table,Procedure,Argument,Date,Number,Varchar2,generate_all)

rx = Record("example1.r",
           [("a",Varchar2(2000)),
            ("b",Number()),
            ("c",Date())])

r_array = Table("example1.r_array",rx)

print(r_array)

proc = Procedure("example1.proc","example1_proc",
        [Argument("x","in",r_array),
         Argument("y","out",r_array)])

import os
dblogin = os.environ['pypub_login'] # login for test schema


generate_all([proc],"example1module",".",
             "wrap_example1",".",dblogin)

```

a Python Module is created which contains a definition for a class corresponding 
to the PL/SQL record `pypublisher_demo.r` and and a class which contains the method 
which wraps `pypublisher_demo.proc`. Assume is con is a `cx_Oracle.connection` object: 

```
import cx_Oracle
import example1module

import os
dblogin = os.environ['pypub_login'] # login for test schema

def test(n) :
   con = cx_Oracle.connect(dblogin)
   try :
       p = example1module.procedures(con)
       l=list()
       for i in range(n) :
           r = example1module.example1_r()
           r.a = "Row "+str(i)
           r.b = i
           r.c = None
           l.append(r)
       res = p.example1_proc(l)
       print(res)
   finally :
       con.close()

test(10)
```