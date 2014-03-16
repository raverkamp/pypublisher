#! /usr/bin/python
# coding=latin-1

import cx_Oracle


"""
dbms_output supports lines with maximum length of 32767 
and unlimited internal size
testing reveals, that 1000000 is the maximum internal buffers size
and retrieving lines of length greater than ?, or maybe this 
is a problem when retrieving data
writing that long lines is not a problem
error in "SYS.DBMS_OUTPUT", line 151 
the buffer in the call dbms_output.get_line has length 32767
"""

def dbms_output_enable(con,size):
    cur = con.cursor()
    cur.callproc("dbms_output.enable",[size])
    cur.close()

def dbms_output_disable(con):
    cur = con.cursor()
    cur.callproc("dbms_output.disable",[])
    cur.close()

def dbms_output_get_lines(con): 
    l = []
    cur = con.cursor()
    try :
        va = cur.var(cx_Oracle.STRING,32767)
        while True:
            (line,stat) = cur.callproc("dbms_output.get_line",(va,None))
            stat = int(stat)
            if stat>0 : 
                break
            else :
                l.append(line)
    finally :
        cur.close()
    return l
