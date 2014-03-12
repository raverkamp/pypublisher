#! /usr/bin/python
# coding=latin-1

import unittest
import cx_Oracle
from py_pack1 import test_pypub1_aas,test_pypub1_r1,test_pypub1_r2,procedures

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
        print("Start " + repr(type(self)))
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

        r2 = test_pypub1_aas()
        r2.a = 2
        r2.b = "xyz"

        res = self.pack.p1([r1,r2])
        for a in res :
            print (a)

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
       # print [x1,x2]
       # print res
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
        print (res)

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
        #orautil.dbms_output_enable(self.con,100000)

        t2 = self.pack.p_timestamping(t)
        #print(orautil.dbms_output_get_lines(self.con))
        self.assertTrue(t==t2)

    def test_timestamping2(self) :
        t3 = self.pack.p_timestamping(None)
        self.assertTrue(t3 is None)


# testing dbms_output
class TestDbmsOutput(Gen_TestCase) :

    def test1(self) :
        import orautil
        orautil.dbms_output_enable(self.con,10000)
        cur = self.con.cursor()
        for i in range(10) :
            cur.callproc("dbms_output.put_line",["line " +repr(i)])
        cur.close()
        l = orautil.dbms_output_get_lines(self.con)
        print(l)


if __name__ == '__main__':
    unittest.main()
