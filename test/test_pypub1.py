#! /usr/bin/python
# coding=latin-1

import unittest
import cx_Oracle
from py_pack1 import test_pypub1_aas,test_pypub1_r1,test_pypub1_r2,procedures,test_object

import datetime
import decimal
import uuid
import sys
import os
import time

from plsqlpack import PLSQLException,PackException

dblogin = os.environ['pypub_login'] # login for test schema

class  Gen_TestCase(unittest.TestCase):
  
    def setUp(self):
        #print("Start " + repr(type(self)))
        self.con = cx_Oracle.connect(dblogin)
        self.pack = procedures(self.con)

    def tearDown(self) :
        self.con.close()

class Tests1(Gen_TestCase) :
    def test_comp(self) :
        r1 = test_pypub1_aas()
        r1.a = 1
        r1.b = "abc"

        r2 = test_pypub1_aas()
        r2.a = 1
        r2.b = "abc"
        self.assertTrue(r1==r2)

        r2.a=2
        self.assertTrue(r1!=r2)


    def test_p1_p2(self) :
        r1 = test_pypub1_aas()
        r1.a = 1
        r1.b = "abc"
        r1.c = datetime.datetime(2012,12,3)

        r2 = test_pypub1_aas()
        r2.a = 2
        r2.b = "xyz"
        r2.c =  datetime.datetime(2019,11,12)
 
        res = self.pack.p1([r1,r2])
        [a,b] = res
        self.assertTrue(a.a == -r1.a)
        self.assertTrue(a.b == "abcd-" + r1.b)
        self.assertTrue(a.c == r1.c+datetime.timedelta(1))

        self.assertTrue(b.a == -r2.a)
        self.assertTrue(b.b == "abcd-" + r2.b)
        self.assertTrue(b.c == r2.c+datetime.timedelta(2))


    def test_p3(self) :
        x = self.pack.p3("abcd")
        self.assertTrue(x=="qbcr")

        a=""";\;gfd.\\\;;;\;\\\;x"""
        a=a+a
        a=a+a
        x = self.pack.p3(a)
        a2 = "q" + x[1:len(x)-1] +"r"
        self.assertTrue(x==a2)

        a=[]
        for i in range(8000) :
            a.append(""";\\""")
        a= "".join(a)
        x = self.pack.p3(a)
        a2 = "q" + x[1:len(x)-1] +"r"
        self.assertTrue(x==a2)

        # and an error if string is larger than 16000
        with self.assertRaises(PackException):
             a = self.pack.p3(a+"1")

    def test_p4(self) :
        (x1,y1,z1) = self.pack.p4(None,None,None)

        self.assertTrue(x1==None and y1==None and z1==None )

        d =  datetime.datetime(2010,4,9,14,56,17)
        (x,y,z) = self.pack.p4(decimal.Decimal("12.8"),13,d)
        d2 = d + datetime.timedelta(1)

        self.assertTrue(x==decimal.Decimal("13.8") and y==14 and z==d2)

    def test_p4b(self) :
        a= decimal.Decimal("1")
        b = 12
        c =  datetime.datetime(2010,4,9,14,56,17)
        func = lambda a,b,c :  self.pack.p4(a,b,c)
        self.assertRaises(PackException, func, "1",b,c)
        self.assertRaises(PackException, func, c,b,c)

        self.assertRaises(PackException, func, a,a,c)
        self.assertRaises(PackException, func, a,"s",c)
        self.assertRaises(PackException, func, a,c,c)

        self.assertRaises(PackException, func, a,b,1)
        self.assertRaises(PackException, func, a,b,"2")
        self.assertRaises(PackException, func, a,b,a)


   #   procedure p5(x out t1,y in t1) is
    def test_p5(self) :
        x = self.pack.p5([])
        self.assertEqual(x, [], "msg")
# type r1 is record(
#    a number,
#    b integer,
#    c varchar2(200),
#    d date);

        x1 = test_pypub1_r1()
        x1.a = decimal.Decimal("12")
        x1.b = -15
        x1.c = "asgfdhgafdhagfdhgafdha"
        x1.d = datetime.datetime(2001,1,3)

        x2 = test_pypub1_r1()
        x2.a = decimal.Decimal("121221.656")
        x2.b = -15
        x2.c = "ztruztruzttuztrutrutr"
        x2.d = datetime.datetime(2002,1,3)

        res = self.pack.p5([x1,x2])
        self.assertEqual(res[0].a,x2.a,"aua")
        
        self.assertRaises(Exception, lambda v : self.pack.p5([v]),None)

    def test_p5b(self) :
        a=[]
        for i in range(10000) :
            x1 = test_pypub1_r1()
            x1.a = decimal.Decimal("12") * decimal.Decimal("121.121221")
            x1.b = -765865
            x1.c = u"asgfdhgafdhagfdhgafdhafdsgfdsgfdsgdsgfdsgfdsgfdsgfdsgfdsgfdsgfdsgfd"
            x1.d = datetime.datetime(2001,1,3) +datetime.timedelta(i)
            a.append(x1)
        res = self.pack.p5(a)
        res = self.pack.p5(res)
        self.assertTrue(a == res, 'aua')

    #unicode umlaute
    def test_p6 (self) :
        res = self.pack.p6(u"xäöüß")
        self.assertEqual("xäöüßäöüß", res, 'aua')

    def test_p7_p8(self) :
        self.pack.p7([],[])
        res = self.pack.p8()
        self.assertEqual(([],[]),res)


        self.pack.p7(None,None)
        res = self.pack.p8()
        self.assertEqual((None,None),res)

        sa =[]
        na=[]
        for i in range(100) :
            na.append(decimal.Decimal(str(i*12.12)))
            sa.append(("nlas-" +str(i))*20)
        self.pack.p7(na,sa)

        res = self.pack.p8()
        self.assertEqual((na,sa),res)

    def test_p9(self) :
        g1 = uuid.uuid4()
        g2= self.pack.p9(g1)
        self.assertTrue(g1==g2)

        g3 = self.pack.p9(None)
        self.assertTrue(g3==None)

    def test_p10(self ):
        with self.assertRaises(PLSQLException):
           a = self.pack.p10_xyz("bla")

class Tests2(Gen_TestCase) :        
    def test_timestamping(self) :
        import orautil
        # 123456 are microseconds
        t = datetime.datetime(2012,3,4,23,34,12,123456)
        t2 = self.pack.p_timestamping(t)
        self.assertTrue(t==t2)

    def test_timestamping2(self) :
        t3 = self.pack.p_timestamping(None)
        self.assertTrue(t3 is None)

    def swap(self,s) :
        l = int(len(s)/2)
        return (s[l:])+  (s[0:l])

    def test_p_large_string(self) :
        (a) = self.pack.p_large_string("1234")
        self.assertTrue(a == self.swap("1234"))

        # a string less than 10000 chars works
        s = "1234567890"*999
        (a) = self.pack.p_large_string(s)
        self.assertTrue(a == self.swap(s))

    def test_tabi(self) :
        l = {}
        for i in range(30) :
            x1 = test_pypub1_r1()
            x1.a = decimal.Decimal(repr(12*i))
            x1.b = i*30+5
            x1.c = "asgfdhgafdhagfdhgafdha"
            x1.d = datetime.datetime(2001,int(i/3)+1,int(i/2)+1)
            l[i*8] = x1
        res = self.pack.p_tabi(l)
        self.assertTrue(l==res)
            
    def test_tabi2(self) :
        l = {}
        res = self.pack.p_tabi(l)
        self.assertTrue(l==res)
            
    def test_tabi3(self) :
        l = {}
        l[-123] = test_pypub1_r1()
        res = self.pack.p_tabi(l)
        self.assertTrue(l==res)

    def test_tabi4(self) :
        l = {}
        l[None] = test_pypub1_r1()
        func = lambda x : self.pack.p_tabi(x)
        self.assertRaises(PackException, func,l)

    def test_tabv(self) :
        l = {}
        for i in range(30) :
            x1 = test_pypub1_r1()
            x1.a = decimal.Decimal(repr(12*i))
            x1.b = i*30+5
            x1.c = "asgfdhgafdhagfdhgafdha"
            x1.d = datetime.datetime(2001,int(i/3)+1,int(i/2)+1)
            l["a" + repr(i*8234)] = x1
        res = self.pack.p_tabv(l)
        self.assertTrue(l==res)
            
    def test_tabv2(self) :
        l = {}
        res = self.pack.p_tabv(l)
        self.assertTrue(l==res)

    def test_tabv3(self) :
        l = {}
        l["nix"] = test_pypub1_r1()
        res = self.pack.p_tabv(l)
        self.assertTrue(l==res)

    def test_tabv4(self) :
        l = {}
        l[""] = test_pypub1_r1()
        func = lambda x : self.pack.p_tabv(x)
        self.assertRaises(PackException, func,l)
 
    def test_tabv5(self) :
        l = {}
        l[None] = test_pypub1_r1()
        func = lambda x : self.pack.p_tabv(x)
        self.assertRaises(PackException, func,l)

    def test_o1_1(self) :
        res = None
        self.assertTrue(res is None)
    
    def test_o2(self) :
        a = test_object()
        res = self.pack.p_o1(a)
        self.assertTrue(res == a)

# testing dbms_output
# note : dbms_output supports lines with maximum length of 32767 
#        and unlimited internal size
#        testing reveals, that 1000000 is the maximum internal buffers size
#        and retrieving lines of length greater than ?, or maybe this 
#        is a problem when retrieving data
#        writing that long lines is not a problem
#        error in "SYS.DBMS_OUTPUT", line 151 
#        the buffer in the call dbms_output.get_line has length 32767
class TestDbmsOutput(Gen_TestCase) :

    def test1(self) :
        import orautil
        orautil.dbms_output_enable(self.con,1000000)
        cur = self.con.cursor()
        lin = []
        for i in range(100) :
            lin.append("line " +("x"* (i*10)) + repr(i))
        for x in lin : 
            cur.callproc("dbms_output.put_line",[x])
        cur.close()
        lout = orautil.dbms_output_get_lines(self.con)
        self.assertTrue(lin==lout)



if __name__ == '__main__':
    unittest.main()
