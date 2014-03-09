import decimal
import datetime
import time
import cx_Oracle
import uuid
import sys

# from six 
# Useful for very coarse version differentiation.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

#function escape(v varchar2) return varchar2 is
#begin
# return replace(replace(v,esc,esc||esc_repl),sep,esc||sep_repl);
#end;

#function descape(v varchar2) return varchar2 is
#begin
#  return replace(replace(v,esc||sep_repl,sep),esc||esc_repl,esc);
#end;

esc = "\\"
sep = ";"
esc_repl = "a"
sep_repl = "b"

def escape (s) :
    return s.replace(esc,esc+esc_repl).replace(sep,esc +sep_repl)

def descape (s):
    return s.replace(esc+sep_repl,sep).replace(esc+esc_repl,esc)

# used to throw the excpetion which was riased in the original PL/SQL Code
class PLSQLException (BaseException) :
    def __init__(self,value) :
        self.value=value
    def __repr__(self) :
        return "PLSQLException(" + repr(self.value) +")"

# raised in packing or unpacking
class PackException (BaseException) :
    def __init__(self,value) :
        self.value = value
    def __repr__(self) :
        return "PackException(" + repr(self.value) +")"

class Packing (object) :

    max_string_size = 16000

    def __init__(self,encoding) :
        self.set_output()
        self.encoding = encoding

    def set_input(self,l) :
        self.inputs = l # a list with the input
        self.inpos = 0

    def set_output(self) :
        self.outputs = []
        self.outpos = 0

    def get_output(self) :
        return self.outputs

    def get(self) :
        self.inpos = self.inpos + 1
        return self.inputs[self.inpos-1]

    def put(self,v) :
        if v==None :
            self.outputs.append("")
        else :
            #if isinstance(v,unicode) :
            #    v=v.encode(self.encoding)
            if isinstance(v,str) or isinstance(v,unicode) :
                if len(v) > self.max_string_size :
                    raise PackException("string is to large")
                self.outputs.append(v)
            else :
                raise PackException("input must be a string")

    def get_int(self) :
        s = self.get()
        if s=="" :
            return None
        else :
            return int(s)

    def put_int(self,x) :
        if x==None :
            self.put("")
        else :
            if isinstance(x,int) or (PY2 and isinstance(x,long)):
                s = str(x)
                if len(s) <= 37 :
                  self.put(s)
                else :
                  raise PackException("int or long is to large")
            else :
                raise PackException("int or long expected")

    def get_dec (self) :
        x=self.get()
        if x==None or x=="" :
            None
        else :
            return decimal.Decimal(x)

    def put_dec (self,x) :
        if x==None :
            self.put("")
        else :
            if (isinstance(x,int) or isinstance(x,decimal.Decimal) 
                or (PY2 and isinstance(x,long)) or isinstance(x,float)) :
                s = str(x)
                if len(s)<=40 :
                  self.put(s)
                else :
                  raise PackException("number is to long: " +s)
            else :
                raise PackException("dec or int expected")

    def get_datetime(self):
        v = self.get()
        if v == None or v=="" :
            return None
        else :
            structTime = time.strptime(v,"%Y-%m-%d %H:%M:%S")
            return datetime.datetime(*structTime[:6])

    def put_datetime(self,x) :
        if x==None :
            self.put("")
        else :
            if isinstance(x,datetime.datetime) :
                self.put(x.strftime("%Y-%m-%d %H:%M:%S"))
            else :
               raise PackException("datetime expected")

    def get_guid(self) :
        v = self.get()
        if v == None or v=="" :
            return None
        else :
            return uuid.UUID(v)

    def put_guid(self,x) :
        if x==None :
            self.put("")
        else :
            if isinstance(x,uuid.UUID) :
                #self.put(x.bytes.encode('hex'))
                self.put(x.hex)
            else :
               raise PackException("UUID expected")

    def put_array(self,putter,ar) :
        if ar==None :
            #print "put null array"
            self.put("")
        else :
            #print "put array size" +str(len(ar))
            if isinstance(ar,list) :
                self.put_int(len(ar))
                for x in ar :
                    putter(self,x)
            else :
                raise PackException("list expected")

    def get_array(self,getter) :
        si = self.get_int()
        if si == None :
            return None
        else :
            res = []
            for i in range( si) :
               v = getter(self)
               res.append(v)
            return res

    def put_plsqltableI(self,putter,tab) :
        if tab==None :
            raise PackException("PLSQL table must not be null")
        else :
          if isinstance(tab,dict) :
             self.put_int(len(tab))
             #print(tab)
             if PY2 :
                items = tab.iteritems()
             else :
                items = tab.items()
             for (k,v) in items : # tab.iteritems() :
                self.put_int(k)
                #print ("+"+str(k)+"/"+str(v))
                putter(self,v)
          else :
              raise PackException("expecting a dict not a " + type(tab))

    def put_plsqltableV(self,putter,tab) :
        if tab==None :
            raise PackException("PLSQL table must not be null")
        else :
          if isinstance(tab,dict) :
             self.put_int(len(tab))
             for (k,v) in tab.iteritems() :
                self.put(k)
                putter(self,v)
          else :
              raise PackException("expecting a dict not a " + type(tab))
    
    def get_plsqltableI(self,getter) :
        si = self.get_int()
        if si == None :
            raisePackException("returned PLSQL table must not be null")
        else :
            res = dict()
            for i in range( si) :
               k = self.get_int()
               v = getter(self)
               res[k]=v
            return res

    def get_plsqltableV(self,getter) :
        si = self.get_int()
        if si == None :
            raisePackException("returned PLSQL table must not be null")
        else :
            res = dict()
            for i in range( si) :
               k = self.get()
               v = getter(self)
               res[k]=v
            return res

    def cur_to_list(self,cur) :
        a = []
        for (v,) in cur.fetchall() :
            a.append(v)
        return a
    
    def get_data(self,con) :
        cur = con.cursor()
        cur.execute('select column_value from table(packing.get_data)')
        a = self.cur_to_list(cur)
        cur.close()
        b = "".join(a).split(";")
        o=[]
        for f in b :
            o.append(descape(f))
        self.set_input(o)
        
    def call_proc2(self,con,proc) :
        a = []
        # print "in outputs: " + str(len(self.outputs))
        for x in self.outputs :
            a.append(escape(x))
        buf = (";".join(a)) +";"
        cur = con.cursor()
        v = cur.var(cx_Oracle.STRING)
        i=0
        cur.callproc("packing.clear")
        n = 4000 # this seems to be the limit
        # fixme : what about unicode?
        while i< len(buf) :
            #print " " + str(i)
            s = buf[i:i+n]
            v.setvalue(0,s)
            i=i+n
            cur.callproc("packing.store",[v])
        cur.callproc(proc)
        cur.close()

    def call_proc(self,con,proc) :
        #print "start "+proc +": " + str(time.clock())
        a = []
        # print "in outputs: " + str(len(self.outputs))
        for x in self.outputs :
            a.append(escape(x))
        buf = (";".join(a)) +";"
        cur = con.cursor()

        vs = []
        for i in range(10) :
            vs.append(cur.var(cx_Oracle.STRING))
            #vs.append(cur.var(cx_Oracle.UNICODE))
        i=0
        cur.callproc("packing.clear")
        n = 4000 # this seems to be the limit
        # fixme : what about unicode?
        while i< len(buf) :
            #print " " + str(i)
            for j in range(10) :
                s = buf[i+j*n : i+j*n+n]
                vs[j].setvalue(0,s)
            cur.callproc("packing.store10",vs)
            i = i + 10*n
        #print "stored "+proc +": " + str(time.clock())
        erc = cur.var(cx_Oracle.STRING) # no floating point please
        erm = cur.var(cx_Oracle.STRING)
        cstack = cur.var(cx_Oracle.STRING)
        estack= cur.var(cx_Oracle.STRING)
        cur.callproc(proc,[erc,erm,cstack,estack])
        if erc.getvalue() == None :
            #print "done " + proc +": " + str(time.clock())
            cur.close()
            return None
        else :
            cur.close()
            return ((int(erc.getvalue()),erm.getvalue(),cstack.getvalue(),estack.getvalue()))
