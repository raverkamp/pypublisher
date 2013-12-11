
import datetime

class GenerationException (Exception) :
    def __init__(self,value) :
        self.value = value

class PLSQLType (object) :
    def __init__(self,name):
        skip

class Record (PLSQLType):
    def __init__(self,name, fields,python_name=None):
        self.fields = fields
        self.name = name.upper()
        if python_name == None :
            self.python_name = name.lower().replace(".","_")
        else :
            self.python_name  = python_name
        
    def __repr__ (self) :
        return "Record(" + (self.name) +"," + repr(self.fields) +")"

class Object(PLSQLType) :
    def __init__(self,name,no_of_constructor_args,fields,python_name=None):
        self.name = name.upper()
        self.fields = fields
        #self.super = super
        self.no_of_constructor_args = no_of_constructor_args
        if python_name ==None :
            self.python_name = name.lower().replace(".","_")
        else :
            self.python_name  = python_name

    # this was needed for inheritance
    def slots(self) :
        return self.fields

    def __repr__ (self) :
        return "Object(" + (self.name) +"," + repr(self.fields) +")"


class Table (PLSQLType):
    def __init__(self,name,type):
        self.name=name.upper()
        self.type = type
    def __repr__(self):
        return "Table(" + self.name +", " + repr(self.type) +")"

class PLSQLTableI(PLSQLType) :
    def __init__(self,name,type) :
        self.name = name.upper()
        self.type = type
    def __repr__(self):
        return "PLSQLTableI(" + self.name +", " + repr(self.type) +")"

class PLSQLTableV(PLSQLType) :
    def __init__(self,name,type) :
        self.name = name.upper()
        self.type = type
    def __repr__(self):
        return "PLSQLTableV(" + self.name +", " + repr(self.type) +")"


class Varchar2 (PLSQLType):
    def __init__ (self,size) :
        self.size = size
        self.name = "VARCHAR2"

    def __repr__ (self) :
        return "varchar2("+ repr(self.size) + ")"

class Number(PLSQLType):
    def __init__ (self) :
        self.name = "NUMBER"

    def __repr__ (self) :
        return "number()"

class Integer(PLSQLType):
    def __init__ (self) :
        self.name = "INTEGER"

    def __repr__ (self) :
        return "integer()"

class Date(PLSQLType) :
    def __init__ (self) :
        self.name = "DATE"
        
    def __repr__ (self) :
         return "date()"
     
class Guid(PLSQLType) :
    def __init__ (self) :
        self.name = "GUID"
        
    def __repr__ (self) :
         return "guid()"

# the singletons
varchar2 = Varchar2(None)
number=Number()
integer=Integer()
date=Date()
guid=Guid()


def var_type_name(ty) :
    if isinstance(ty,Varchar2) :
        return "varchar2(32767)"
    elif isinstance(ty,Guid) :
        return "raw(16)"
    else :
        return ty.name

def arg_type_name(ty) :
    if isinstance(ty,Guid) :
        return "raw"
    else :
        return ty.name

class Argument(object):
    def __init__(self,name,direction,plsqltype):
        if not (isinstance(name,str) 
                and isinstance(direction,str) 
                and isinstance(plsqltype,PLSQLType)) :
           raise Exception("Wrong type")
        dir = direction.lower()
        if not (dir=="in" or dir=="out" or dir == "inout") :
            raise GenerationException("Wrong direction: " + dir)
        self.name = name.upper()
        self.direction = dir
        self.plsqltype = plsqltype

    def __repr__(self) :
        return "Argument(" + repr((self.name,self.direction,self.plsqltype)) +")"


def checkIsArg(x) :
    if isinstance(x,tuple) and len(x)==3 :
        (name,direction,plsqltype) = x
        if (not (isinstance(name,str) 
                 and isinstance(direction,str) 
                 and isinstance(plsqltype,PLSQLType))) :
           raise Exception("Wrong type")
        dir = direction.lower()
        if not (dir=="in" or dir=="out" or dir == "inout") :
            raise GenerationException("Wrong direction: " + dir)
    else :
        raise GenerationException("argument has to be a tuple of length 3: " + str(x))

def upgradeArg(x) :
    if isinstance(x,Argument) :
        return x
    if checkIsArg(x) :
        return Argument(x[0],x[1],x[2])
    
class Procedure :
    def __init__ (self,name,pyname,args) :
        self.name = name.upper()
        # in Python3 map returns an iterable , so turn t into a list
        self.args = list(map(upgradeArg,args))
        self.pname = pyname

    def __repr__(self) :
        return "Procedure(" + repr((self.name,self.pname,self.args)) +")"

class Function :
    def __init__ (self,name,pyname,return_type,args) :
        self.name = name.upper()
        self.return_type = return_type
        self.args = args
        self.pname = pyname

    def __repr__(self) :
        return "Function(" + repr((self.name,self.pname,self.return_type,self.args)) +")"

class _Task(object) :
    def __init__ (self,packagename,classname,procedures) :
        self.packagename = packagename
        self.classname = classname
        self.procedures = procedures

# generate a task
# the call will be store data
# maybe several procedure calls
# begin
#   store_data(string1,string2, ...)
#   exec_procedure
#   get_data(out size,string1,string2,string3)
# end;

# for each type generate put und get
# typen werden ueber ihren namen identifiziert.
# for each pl/sql type generate a corresponding python class
# record => class, but what name ?


class Templates :
    table_put_get =  """
procedure put(t $tab_type) is
  begin
    if t is null then
      packing.putn(null);
    else
      -- assumption the thing is dense, no delete allowed
      -- first index must be 1
      packing.putn(t.count);
      if t.count <> nvl(t.last, 0) or nvl(t.first, 1) <> 1 then
        raise_application_error(-20001, 'table must be dense');
      end if;
      for i in 1 .. t.count loop
        $item_put(t(i));
      end loop;
    end if;
  end;

  procedure get(t in out nocopy $tab_type) is
    size_ number;
  begin
    packing.getn(size_);
    if size_ is null then
      t := null;
    else
      t := new $tab_type();
      for i in 1 .. size_ loop
        t.extend();
        $item_get(t(i));
      end loop;
    end if;
  end;
"""

    plsql_tablei_put_get = """
procedure put(t $tab_type) is
  i integer;
  begin
     if t.first is null then
        packing.putn(0);
        return;
     end if;
     packing.putn(t.count);
     i:= t.first;
     loop
        exit when i is null;
        packing.putn(i);
        $item_put(t(i));
        i := t.next(i);
     end loop;
  end;


  procedure get(t in out nocopy $tab_type) is
    size_ number;
    k integer;
    r $elem_type;
  begin
    packing.getn(size_);
    if size_ is null then
      raise_application_error(-20001,'plsql table must not be null');
    end if;
    packing.putn(t.count);
    for i in 1 .. size_ loop
        packing.getn(k);
        $item_get(r);
        t(k):=r;
    end loop;
  end;
"""
    plsql_tablev_put_get = """
procedure put(t $tab_type) is
  i integer;
  begin
     if t.first is null then
        packing.putn(0);
        return;
     end if;
     i:= t.first;
     loop
        exit when i is null;
        packing.putv(i);
        $item_put(t(i));
        i := t.next(i);
     end loop;
  end;


  procedure get(t in out nocopy $tab_type) is
    size_ number;
    k integer;
    r $elem_type;
  begin
    packing.getn(size_);
    if size_ is null then
      raise_application_error(-20001,'plsql table must not be null');
    end if;
    for i in 1 .. size_ loop
        packing.getv(k);        
        $item_get(r);
        t(k) :=r;
    end loop;
  end;
"""

def base_type_dic () :
    d = dict()
    d["NUMBER"] = ("packing.putn","packing.getn","put_number","get_number")
    d["VARCHAR2"] =("packing.putv","packing.getv","put_varchar2","get_varchar2")
    d["DATE"] = ("packing.putd","packing.getd","put_date","get_date")
    d["INTEGER"] = ("packing.putn","packing.getn","put_integer","get_integer")
    d["GUID"] =("packing.putg","packing.getg","put_guid","get_guid")
    return d

def default_putters () : return ("""
    def put_number(self,n) :
        self.packing.put_dec(n)
    def get_number(self) :
        return self.packing.get_dec()

    def put_integer(self,n) :
        self.packing.put_int(n)
    def get_integer(self) :
        return self.packing.get_int()

    def put_varchar2(self,v) :
        self.packing.put(v)
    def get_varchar2(self) :
        s = self.packing.get()
        if s=="" :
            return None
        else :
            return s

    def put_date(self,d) :
        self.packing.put_datetime(d)
    def get_date(self):
        return self.packing.get_datetime()

    def put_guid(self,d) :
        self.packing.put_guid(d)
    def get_guid(self):
        return self.packing.get_guid()
  """)

def checktype(va,ty) :
    if isinstance(va,ty) :
        pass
    else :
        raise Exception("Wrong type " + str(va) + " - " + str(ty))

# create unique names for pl/sql code
# simply append numbers
# the original name is simplified and cut off at 20
# then a number is appended
#  it should be posible to replace this with guid strings
class Unifier (object) :
    def __init__ (self) :
        self.names = dict()
    
    def simplify(self,name) :
        name = name.upper()
        name = name.replace(".","_")
        return name[0:20]

    def unify(self,name) :
        checktype(name,str)
        name = self.simplify(name)
        if name in self.names :
            n = self.names[name]
            ln = len(name + str(n+1))
            res = name + ("_"*(30-n)) +str(n+1)
            self.names[name] = n+1
            return res
        else :
             self.names[name] = 0
             ln = len(name + str(0))
             return name +  ("_"*(30-ln)) + str(0)



class Generation (object):
    def __init__(self,packname,python_name) :
        self.saccu = [] # SpecACCUmulator
        self.baccu = [] # BodyACCUmulator
        self.paccu = [] # PythonACCUmulator
        self.caccu = [] # pythonClassACCUmulator, 
                        # for the generated python classes
        self.type_dict = base_type_dic()
        self.packname = packname
        self.python_name = python_name
        self.proc_unifier = Unifier()
        self.generated_methods = dict()
        self.generated_classes = dict()
        #self.defined_plsql = dict()

    def intern(self,type,tu) :
        checktype(type,PLSQLType)
        self.type_dict[type.name] = tu

    def proc_for_type(self,type):
        checktype(type,PLSQLType)
        return self.type_dict[type.name]

    def gen_class_for_record(self,rtype) :
        python_name = rtype.python_name
        if python_name in self.generated_classes :
            raise GenerationException("class name used twice: " + rtype)
        else :
            self.generated_classes[python_name]=True
            
        acc = []
        rl=[]
        acc.append("class " + python_name + "(object ):" )
        acc.append("    def __init__(self):")
        for (fname,ftype) in rtype.fields :
            acc.append ("        self." + fname.lower() + "=None")
            rl.append( " self."+ fname.lower())

        self.caccu.append( "\n" +("\n".join(acc)) +"\n")
        self.caccu.append("    def __repr__ (self) :")
        self.caccu.append("        return '#" + rtype.python_name + "'+ repr((" + ",".join(rl) +"))")
        self.caccu.append("    __hash__ = None")
        self.caccu.append("")
        self.caccu.append("    def __eq__(self,x) :")
        self.caccu.append("        return (isinstance(x," + python_name +")")
        for (fname,ftype) in rtype.fields :
            self.caccu.append("            and self."+fname.lower() + "== x." + fname.lower())
        self.caccu.append("        )")
        self.caccu.append("    def __ne__(self,x) :")
        self.caccu.append("        return not (self==x)")

    def gen_class_for_object(self,otype) :
        python_name = otype.python_name
        if python_name in self.generated_classes :
            raise GenerationException("class name used twice: " + rtype)
        else :
            self.generated_classes[python_name]=True
        acc = []
        rl=[]
        acc.append("class " + python_name + "(object ):" )
        acc.append("    def __init__(self):")
        # fixme, what about super?
        for (fname,ftype) in otype.slots() :
            acc.append ("        self." + fname.lower() + "=None")
            rl.append( " self."+ fname.lower())
        self.caccu.append( "\n" +("\n".join(acc)) +"\n")
        self.caccu.append("    def __repr__ (self) :")
        self.caccu.append("        return '#" + otype.python_name + "'+ repr((" + ",".join(rl) +"))")
        self.caccu.append("")
        self.caccu.append("    __hash__ = None")
        self.caccu.append("")
        self.caccu.append("    def __eq__(self,x) :")
        self.caccu.append("        return (isinstance(x," + python_name +")")
        for (fname,ftype) in otype.slots() :
            self.caccu.append("            and self."+fname.lower() + "== x." + fname.lower())
        self.caccu.append("        )")
        self.caccu.append("    def __ne__(self,x) :")
        self.caccu.append("        return not (self==x)")

    def gen_record(self,rtype):
        pf = ("procedure put(v " + rtype.name +") is\n"
             + "begin")
        gf = ("procedure get(v in out nocopy " + rtype.name + ") is \n"
              + "begin")
        
        for field in rtype.fields :
            (fname,ftype) = field
            self.gen_type(ftype)
            (p,g,x,y) = self.proc_for_type(ftype)
            pf = pf + "\n" + p +"(v." + fname +");"
            gf = gf + "\n" + g +"(v." + fname +");"

        pf = pf + "\nend;"
        gf = gf + "\nend;"
        self.baccu.append(pf)
        self.baccu.append(gf)
      
        # generate put

        self.gen_class_for_record(rtype)
        py_put = "put_" + rtype.python_name
        py_get = "get_" + rtype.python_name

        self.paccu.append("    def " + py_put +"(self,v):")
        self.paccu.append("        if not isinstance(v,"+rtype.python_name+"):")
        self.paccu.append("              raise Exception('type error, expecting' + str("+rtype.python_name+") + ' got ' +str(type(v)))")
        
        for field in rtype.fields :
            (fname,ftype) = field
            (x,y,fpyput,fpyget) = self.proc_for_type(ftype)
            self.paccu.append("        self." + fpyput +"(v." +fname.lower() +")")
        
        self.paccu.append("    def " + py_get +"(self):")
        self.paccu.append("        res = " +rtype.python_name+ "()")

        for field in rtype.fields :
            (fname,ftype) = field
            (x,y,fpyput,fpyget) = self.proc_for_type(ftype)
            self.paccu.append("        res."+ fname.lower() +" = self." + fpyget +"()")
        self.paccu.append("        return res")
        self.paccu.append("")
   
        self.intern(rtype, ("put","get",py_put,py_get))
##########################################################
    def gen_object(self,otype):
        dummy_args = (",null"*otype.no_of_constructor_args)[1:None]
        pf = ("procedure put(v " + otype.name +") is\n"
             + "begin")
        gf = ("procedure get(v in out nocopy " + otype.name + ") is \n"
              + " res " + otype.name + ";\n" # fixme ? doch funktion?
              + "begin\n"
              + " res := new " + otype.name + "(" + dummy_args + ");\n")
        for field in otype.slots() :
            (fname,ftype) = field
            self.gen_type(ftype)
            (p,g,x,y) = self.proc_for_type(ftype)
            pf = pf + "\n" + p +"(v." + fname +");"
            gf = gf + "\n" + g +"(res." + fname +");"

        pf = pf + "\nend;"
        gf = (gf + "\n"
             "v:=res;\nend;")
        self.baccu.append(pf)
        self.baccu.append(gf)
      
        # generate put

        self.gen_class_for_object(otype)
        py_put = "put_" + otype.python_name
        py_get = "get_" + otype.python_name

        self.paccu.append("    def " + py_put +"(self,v):")
        self.paccu.append("        if not isinstance(v,"+otype.python_name+"):")
        self.paccu.append("              raise Exception('type error, expecting' " + 
                     "+ str("+otype.python_name+") + ' got ' +str(type(v)))")
        
        for field in otype.slots() :
            (fname,ftype) = field
            (x,y,fpyput,fpyget) = self.proc_for_type(ftype)
            self.paccu.append("        self." + fpyput +"(v." +fname.lower() +")")
        
        self.paccu.append("    def " + py_get +"(self):")
        self.paccu.append("        res = " + otype.python_name+ "()")

        for field in otype.slots() :
            (fname,ftype) = field
            (x,y,fpyput,fpyget) = self.proc_for_type(ftype)
            self.paccu.append("        res."+ fname.lower() +" = self." + fpyget +"()")
        self.paccu.append("        return res")
        self.paccu.append("")
   
        self.intern(otype, ("put","get",py_put,py_get))

    def gen_table(self,ttype):
        ty = ttype.type
        self.gen_type(ty)
        (p,g,pyput,pyget) = self.proc_for_type(ty)
        s = (Templates.table_put_get
             .replace("$tab_type",ttype.name)
             .replace("$item_put",p)
             .replace("$item_get",g))
        self.baccu.append(s)
        py_put_name = pyput +"_ar"
        py_get_name = pyget + "_ar"
        self.paccu.append("    def " + py_put_name +"(self,a):\n"
          + "        self.packing.put_array(lambda b,v : self." + pyput + "(v),a)\n\n")

        self.paccu.append("    def " + py_get_name +"(self):\n"
          + "        return self.packing.get_array(lambda b : self." + pyget +"())\n\n")

        self.intern(ttype, ("put","get",py_put_name,py_get_name))

    def gen_tablev(self,ttype) :
       ty = ttype.type
       self.gen_type(ty)
       (p,g,pyput,pyget) = self.proc_for_type(ty)
       s = (Templates.plsql_tablev_put_get
             .replace("$tab_type",ttype.name)
             .replace("$elem_type",var_type_name(ttype.type))
             .replace("$item_put",p)
             .replace("$item_get",g))
       self.baccu.append(s)
       py_put_name = pyput +"_arv"
       py_get_name = pyget + "_arv"
       self.paccu.append("    def " + py_put_name +"(self,a):\n"
          + "        self.packing.put_plsqltableV(lambda b,v : self." + pyput + "(v),a)\n\n")

       self.paccu.append("    def " + py_get_name +"(self):\n"
          + "        return self.packing.get_plsqltableV(lambda b : self." + pyget +"())\n\n")

    def gen_tablei(self,ttype) :
       ty = ttype.type
       self.gen_type(ty)
       (p,g,pyput,pyget) = self.proc_for_type(ty)
       s = (Templates.plsql_tablei_put_get
             .replace("$tab_type",ttype.name)
             .replace("$elem_type",var_type_name(ttype.type))
             .replace("$item_put",p)
             .replace("$item_get",g))
       self.baccu.append(s)
       py_put_name = pyput +"_ari"
       py_get_name = pyget + "_ari"
       self.paccu.append("    def " + py_put_name +"(self,a):\n"
          + "        self.packing.put_plsqltableI(lambda b,v : self." + pyput + "(v),a)\n\n")

       self.paccu.append("    def " + py_get_name +"(self):\n"
          + "        return self.packing.get_plsqltableI(lambda b : self." + pyget +"())\n\n")

       self.intern(ttype, ("put","get",py_put_name,py_get_name))

    def gen_type(self,type):
        if (type.name in self.type_dict) :
            pass
        else:
          if isinstance(type,Record) :
              self.gen_record(type)
          elif isinstance(type,Table) :
              self.gen_table(type)
          elif isinstance(type,PLSQLTableI) :
              self.gen_tablei(type)
          elif isinstance(type,PLSQLTableV) :
              self.gen_tablev(type)
          elif isinstance(type,Object) :
              self.gen_object(type)
          else :
              raise GenerationException("unkown type" + repr(type))

    def gen_procedure(self,proc):
        print ("generating procedure: " + proc.name)
        name = proc.name
        args= proc.args
        has_out_args = False

        if proc.pname in self.generated_methods :
            raise GenerationException("method name used twice" + repr(proc))
        else :
             self.generated_methods[proc.pname]=True
             
        for arg in args:
            self.gen_type(arg.plsqltype)
        #
        pname = ""+ self.proc_unifier.unify(name)
        i =0
        dargs = []
        iargs = []
        oargs = []
        cargs = []
        pyargs = []
        for arg in proc.args :
            #print "doing arg"
            dargs.append("x" + str(i) +" " + var_type_name(arg.plsqltype) +";\n")
            (put,get,py_put,py_get) =self.proc_for_type(arg.plsqltype)
            if arg.direction == "in" or arg.direction == "inout" :
                iargs.append( get + "(x" +str(i) +");\n")
                pyargs.append("x"+str(i))
            if arg.direction == "out" or arg.direction == "inout" :
                oargs.append( put +"(x"+str(i) +");\n")
                has_out_args = True
            cargs.append("x"+str(i))
            i=i+1


        proc_sig = ("procedure " + pname +
             " (erc out integer,erm out varchar2, cstack out varchar2,estack out varchar2)")
        txt = (proc_sig + " is\n"
             + "".join(dargs) + "begin\n"
             +  "packing.start_read;\n"
             + "".join(iargs)+"\n"
             + "begin \n"
             + name + "("
             + ",".join(cargs) +");\n"
             + "exception when others then \n "
             + "  erm:=sqlerrm; \n"
             + "  erc:=sqlcode; \n"
             + "  cstack := dbms_utility.format_error_backtrace; \n"
             + "  estack := dbms_utility.format_error_stack; \n"
             + "  packing.clear;\n"
             +"   return;\n"
             +" end;\n"
             + "packing.clear();\n"
             + "\n".join(oargs) +"\n"
             + "packing.start_read;\n"
             + "end;\n")
        self.baccu.append(txt)
        self.saccu.append(proc_sig +";")

        self.paccu.append("    def " + proc.pname + "(self," + ",".join(pyargs) + "):")
        self.paccu.append("        import time")
        # self.paccu.append("        print \"startx "+ proc.name + ": \"+ str(time.clock())")
        self.paccu.append("        self.packing.set_output()")
        i =0
        l= []
        for arg in proc.args :
            (put,get,py_put,py_get) = self.proc_for_type(arg.plsqltype)
            if arg.direction == "in" or arg.direction == "inout" :
                self.paccu.append("        self." + py_put +" (" + "x" + str(i) +")")
            if arg.direction == "out" or arg.direction == "inout" :
                l.append(" self."+py_get + "()")
            i=i+1

        self.paccu.append("        cres = self.packing.call_proc(self.con,'"+self.packname +"." + pname+"')")
        self.paccu.append("        if cres!=None : raise plsqlpack.PLSQLException(cres)")
        if has_out_args :
            self.paccu.append("        self.packing.get_data(self.con)")
            self.paccu.append("        res = (" + ",".join(l) +")")
            self.paccu.append("        return res")

    def get_gen_package(self) :
        spec = ("package " + self.packname +" is\n" +
                "\n".join(self.saccu) +"\nend;\n")
        body = ("package body " + self.packname + " is\n" +
                "\n".join(self.baccu) +"\nend;")
        pyclass = ("class " +  self.python_name + "(object):\n"
          + "    __init__(self,con):\n"
          + "        self.con= con\n"
          + default_putters())

        return (spec,body,pyclass +  "\n" +"\n".join(self.paccu),"\n".join(self.caccu))

def generate_task(task) :
    """ Generate the code for a plsql translation task.
    
    Input is a task object.
    Return value is a tuple of
    the package specifiation
    the package body
    the python package to call the procedures
    the classes for parameters, i.e. record and tables

    """

    g = Generation(task.packagename,task.classname)
    for proc in task.procedures :
        g.gen_procedure(proc)
    spec = ("create or replace package " + g.packname +" is\n" +
                ("-- generated by pyplsql " + str(datetime.datetime.today()) + "\n") +
                "\n".join(g.saccu) +"\nend;\n")
    body = ("create or replace package body " + g.packname + " is\n" +
                ("-- generated by pyplsql " + str(datetime.datetime.today()) + "\n") +
                "\n".join(g.baccu) +"\nend;")
    pyclass = ("import plsqlpack\n"
          +  ("# generated by pyplsql " + str(datetime.datetime.today()) + "\n")
          +  "class procedures (object):\n"
          + "    def __init__(self,con) :\n"
          + "        self.con= con\n"
          + "        self.packing = plsqlpack.Packing(con.encoding)\n"
          + default_putters())

    return (spec,body,pyclass +  "\n" +"\n".join(g.paccu),"\n".join(g.caccu))


def gen_sqlplus(filename,spec,body) :
    print ("Generating wrapper package: " + filename)
    f = open(filename,"w")
    # it seems, sqlplus does not stop unless we add this  quit
    f.write(spec+"\n/\n")
    f.write("show errors\n")
    f.write(body +"\n/\n")
    f.write("show errors\n")
    f.write("quit\n")
    f.close()

def generate_all(procs,py_mod,py_mod_dir,packname,pack_dir,connstr) :
    """ 
    generate everything 
    procs: a list of procedures
    py_mod: the name of the python module that will be generated
    py_mod_dir: the directory where to write the generated python 
                module
    packname: the name of the wrapper pl/sql package
    pack_dir: where to place the generated package
    connstr: the sqlplus connection whoich will be used to install
             the generated package, If None nothing will be done.
             the path for the sqlplus binary has to be in the 
             path environment variable
    """
    task = _Task(packname,py_mod,procs)
    fname = py_mod_dir +"/"+py_mod +".py"
    print ("Generating python code into: " + fname)
    (spec,body,py_pack,py_classes) = generate_task(task)
    
    f = open(fname,"w")
    f.write(py_pack)
    f.write(py_classes)
    f.close() 

    fpack = pack_dir + "/" + packname + ".pck"
    gen_sqlplus(fpack,spec,body)
    if not(connstr == None or connstr == "") : 
        import subprocess
        subprocess.call("sqlplus " +  connstr + " @"+fpack + "", shell=True)
