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