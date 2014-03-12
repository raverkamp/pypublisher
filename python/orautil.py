#! /usr/bin/python
# coding=latin-1

import cx_Oracle

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
        va = cur.var(cx_Oracle.STRING,32768)
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
