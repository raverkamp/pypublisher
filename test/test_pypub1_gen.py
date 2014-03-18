# -*- coding: latin-1 -*-

import unittest
import sys

from generation import ( Record,Table, Number, Varchar2,Generation,
  Procedure,Argument, Date, Integer,Guid,timestamp,PLSQLTableI,PLSQLTableV,gen_sqlplus,
  generate_all,Object)

import cx_Oracle

import importlib
import decimal
import datetime
import uuid
import imp
import os

thefile = __file__

pack_bla = None
pack = None

dblogin = os.environ['pypub_login'] # login for test schema

def main():
    testdir = os.path.dirname(os.path.abspath(thefile)) 
    generate_all(get_procs(),"py_pack1",testdir,"test_pypub1_wrapper",testdir,dblogin)

all_tab_columns_rec = Record("test_pypub1.all_tab_columns",
    [("owner" ,        Varchar2(20)),
     ("table_name" ,   Varchar2(30)),
     ("column_name"  ,   Varchar2(30)),
     ("data_type"     ,  Varchar2(106)),
     ("data_type_mod" ,  Varchar2(3)),
    ("data_type_owner", Varchar2(30)),
    ("data_length"  ,   Integer()),
    ("data_precision" , Integer()),
    ("data_scale" ,     Integer()),
    ("nullable"    ,    Varchar2(1)),
    ("column_id"    ,   Integer()),
    ("default_length" ,  Integer()),
   #data_default  ,       long          ,                                         
    ("num_distinct"    ,    Integer()),
    #low_value        ,    raw(32),
    #high_value        ,   raw(32),
    ("density"            ,  Number()),
    ("num_nulls" ,           Number()),
    ("num_buckets",          Number()),
    ("last_analyzed",        Date()),
    ("sample_size"   ,       Integer()),
    ("character_set_name" ,  Varchar2(44)),
    ("char_col_decl_length" ,Number()),
    ("global_stats" ,        Varchar2(3)),
    ("user_stats"    ,       Varchar2(3)),
    ("avg_col_len"    ,      Number()),
    ("char_length"     ,     Number()),
    ("char_used"        ,    Varchar2(1)),
    ("v80_fmt_image"     ,   Varchar2(3)),
    ("data_upgraded"      ,  Varchar2(3)),
    ("histogram"         ,   Varchar2(15))])
              

def get_procs () :
    p0= Procedure("test_pypub1.p0","p0",
                [("a","in",Number()),
                 ("b","in",Varchar2(32000)),
                 ("c","in",Date()),
                 ("d","in",Guid()),
                 
                 ("oa","out",Number()),
                 ("ob","out",Varchar2(32000)),
                 ("oc","out",Date()),
                 ("od","out",Guid())])
                 
        
    a = Record("test_pypub1.aas",[("A",Number()),("B",Varchar2(56)),("C",Date())])
    b = Table("test_pypub1.table_",a)
    p1 =  Procedure("test_pypub1.p1","p1",[("x","in",b),("z","out",b)])

    r1 = Record("test_pypub1.r1",[("A",Number()),("B",Integer()),("C", Varchar2(56)),("D", Date())])
    t1 = Table("test_pypub1.t1",r1)
    r2 = Record("test_pypub1.r2",[("A",r1),("B",t1)])
    # procedure p2(x r1, y r2, z out r2);
    p2 = Procedure("test_pypub1.p2","p2",[("x","in",r1),
                                  ("y","in",r2),
                                  ("z","out",r2)])

    #procedure p2b(a out r2) ;
    p2b = Procedure("test_pypub1.p2b","p2b",[("a","out",r2)])
   
    #procedure p2b(a in r2,b out r2);
    p2c = Procedure("test_pypub1.p2c","p2c",[("a","in",r2),
                                     ("b","out",r2)])

    p3 = Procedure("test_pypub1.p3","p3",[("a","in",Varchar2(32000)),("b","out",Varchar2(32000))])

    p4 = Procedure("test_pypub1.p4","p4",
          [("a","in",Number()),("b","in",Integer()),("c","in",Date()),
           ("x","out",Number()),("y","out",Integer()),("z","out",Date())])

    p5 = Procedure("test_pypub1.p5","p5",
          [("x","out",t1),("y","in",t1)])

    p6 = Procedure("test_pypub1.p6","p6",
             [("a","in",Varchar2(2000)),("y","out",Varchar2(2000))])

    number_array = Table("number_array",Number())
    string_array = Table("string_array",Varchar2(2000))

    p7 = Procedure("test_pypub1.p7","p7",[("a","in",number_array),("b","in",string_array)])
    p8 = Procedure("test_pypub1.p8","p8",[("a","out",number_array),("b","out",string_array)])

    p9 = Procedure("test_pypub1.p9","p9",[("a","in",Guid()),("b","out",Guid())])

    p10 = Procedure("test_pypub1.p10","p10_xyz",[("a","in",Varchar2(2000)),("b","out",Varchar2(2000))])

    t1_ident = Procedure("test_pypub1.t1_ident","t1_ident",[("x","in",t1),("y","out",t1)])

    """
    DBMS_PROFILER.START_PROFILER(
      run_comment   IN VARCHAR2 := sysdate,
      run_comment1  IN VARCHAR2 :='',
      run_number    OUT BINARY_INTEGER); """
    start_profiler = Procedure("DBMS_PROFILER.START_PROFILER","start_profiler",
                      [("run_comment","in",Varchar2(2000)),
                       ("run_comment1","in",Varchar2(2000)),
                       ("run_number","out",Integer())])
    
    "DBMS_PROFILER.STOP_PROFILER; "
    stop_profiler = Procedure("DBMS_PROFILER.STOP_PROFILER","stop_profiler",[])

    all_tab_columns_arr = Table("test_pypub1.all_tab_columns_array",all_tab_columns_rec)
    get_all_tab_columns = Procedure("test_pypub1.get_all_tab_columns","get_all_tab_columns",
                         [("no","in",Integer()),
                          ("cols","out",all_tab_columns_arr)])
    
    tab_columns_ident = Procedure("test_pypub1.tab_columns_ident","tab_columns_ident",
                      [("rein","in",all_tab_columns_arr),
                       ("raus","out",all_tab_columns_arr)])

    """                             
    type tabi_r1 is table of r1 index by binary_integer;
    type tabv_r1 is table of r1 index by varchar2(200);
  
    procedure p_tabi(x in tabi_r1,y out tabi_r1);
    procedure p_tabv(x in tabv_r1,y out tabv_r1);
    """
    tabi_r1 = PLSQLTableI("test_pypub1.tabi_r1",r1)
    tabv_r1 = PLSQLTableV("test_pypub1.tabv_r1",r1)
    
    p_tabi = Procedure("test_pypub1.p_tabi_r1","p_tabi",
         [("x","in",tabi_r1),
          ("y","out",tabi_r1)])

    p_tabv = Procedure("test_pypub1.p_tabv_r1","p_tabv",
         [("x","in",tabv_r1),
          ("y","out",tabv_r1)])


    obla = Object("test_object",3,
        [("x",Varchar2(200)),
         ("y",Number()),
         ("z",Date())])
          
    p_o1 = Procedure("test_pypub1.o1","p_o1",
        [("x","in",obla),
         ("y","out",obla)])

    p_testuni1 = Procedure("test_pypub1.testuni1","p_testuni1",
                           [("x","out",Varchar2(2000)),
                            ("y","out",Integer())])

    p_timestamping = Procedure("test_pypub1.timestamping","p_timestamping",
                               [("x","in",timestamp),
                                ("y","out",timestamp)])

    p_large_string = Procedure("test_pypub1.large_string","p_large_string",
                               [("x","in",Varchar2(32767)),
                                ("y","out",Varchar2(32767))])

    
    
    return [p0,p1,p2,p2b,p2c,p3,p4,p5,p6,p7,p8,p9,p10,t1_ident,
            start_profiler,
            stop_profiler,
            get_all_tab_columns,
            tab_columns_ident,
            p_tabi,
            p_tabv,
            p_o1,
            p_testuni1,
            p_timestamping,
            p_large_string
        ]


if __name__ == '__main__':
    main()
