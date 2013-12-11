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
