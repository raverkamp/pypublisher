create or replace package test_pypub1 is

  procedure p0(a  number,
               b  varchar2,
               c  date,
               d  raw,
               oa out number,
               ob out varchar2,
               oc out date,
               od out raw);

  --  a = Record("bla.aas",[("A",Number()),("B",Varchar2(56))])
  --  b = Table("bla.table",a)

  type aas is record(
    a number,
    b varchar2(56),
    c date);
  type table_ is table of aas;

  procedure p1(x table_, z out table_);

  type r1 is record(
    a number,
    b integer,
    c varchar2(32000),
    d date);

  type t1 is table of r1;

  type r2 is record(
    a r1,
    b t1);

  procedure p2(x r1, y r2, z out r2);

  procedure p2b(a out r2);

  procedure p2c(a in r2, b out r2);

  procedure p3(a varchar2, b out varchar2);

  procedure p4(a number,
               b integer,
               c date,
               x out number,
               y out integer,
               z out date);

  procedure p5(x out t1, y in t1);

  -- umlaute
  procedure p6(a varchar2, b out varchar2);

  procedure p7(a in number_array, b in string_array);

  procedure p8(a out number_array, b out string_array);

  -- test for guids
  procedure p9(a in raw, b out raw);

  -- test exceptions
  procedure p10(a in varchar2, b out varchar2);

  procedure t1_ident(x t1, y out t1);

  /*
  OWNER                VARCHAR2(30)
  TABLE_NAME           VARCHAR2(30)                   Table, view or cluster name
  COLUMN_NAME          VARCHAR2(30)                   Column name
  DATA_TYPE            VARCHAR2(106) Y                Datatype of the column
  DATA_TYPE_MOD        VARCHAR2(3)   Y                Datatype modifier of the column
  DATA_TYPE_OWNER      VARCHAR2(30)  Y                Owner of the datatype of the column
  DATA_LENGTH          NUMBER                         Length of the column in bytes
  DATA_PRECISION       NUMBER        Y                Length: decimal digits (NUMBER) or binary digits (FLOAT)
  DATA_SCALE           NUMBER        Y                Digits to right of decimal point in a number
  NULLABLE             VARCHAR2(1)   Y                Does column allow NULL values?
  COLUMN_ID            NUMBER        Y                Sequence number of the column as created
  DEFAULT_LENGTH       NUMBER        Y                Length of default value for the column
  DATA_DEFAULT         LONG          Y                Default value for the column
  NUM_DISTINCT         NUMBER        Y                The number of distinct values in the column
  LOW_VALUE            RAW(32)       Y                The low value in the column
  HIGH_VALUE           RAW(32)       Y                The high value in the column
  DENSITY              NUMBER        Y                The density of the column
  NUM_NULLS            NUMBER        Y                The number of nulls in the column
  NUM_BUCKETS          NUMBER        Y                The number of buckets in histogram for the column
  LAST_ANALYZED        DATE          Y                The date of the most recent time this column was analyzed
  SAMPLE_SIZE          NUMBER        Y                The sample size used in analyzing this column
  CHARACTER_SET_NAME   VARCHAR2(44)  Y                Character set name
  CHAR_COL_DECL_LENGTH NUMBER        Y                Declaration length of character type column
  GLOBAL_STATS         VARCHAR2(3)   Y                Are the statistics calculated without merging underlying partitions?
  USER_STATS           VARCHAR2(3)   Y                Were the statistics entered directly by the user?
  AVG_COL_LEN          NUMBER        Y                The average length of the column in bytes
  CHAR_LENGTH          NUMBER        Y                The maximum length of the column in characters
  CHAR_USED            VARCHAR2(1)   Y                C if maximum length is specified in characters, B if in bytes
  V80_FMT_IMAGE        VARCHAR2(3)   Y                Is column data in 8.0 image format?
  DATA_UPGRADED        VARCHAR2(3)   Y                Has column data been upgraded to the latest type version format?
  HISTOGRAM            VARCHAR2(15)  Y
  */
  type all_tab_columns is record(
    OWNER           varchar(30),
    TABLE_NAME      VARCHAR2(30),
    COLUMN_NAME     VARCHAR2(30),
    DATA_TYPE       VARCHAR2(106),
    DATA_TYPE_MOD   VARCHAR2(3),
    DATA_TYPE_OWNER VARCHAR2(30),
    DATA_LENGTH     NUMBER,
    DATA_PRECISION  NUMBER,
    DATA_SCALE      NUMBER,
    NULLABLE        VARCHAR2(1),
    COLUMN_ID       NUMBER,
    DEFAULT_LENGTH  NUMBER,
    --DATA_DEFAULT         LONG          ,
    NUM_DISTINCT NUMBER,
    --LOW_VALUE            RAW(32),
    --HIGH_VALUE           RAW(32),
    DENSITY              NUMBER,
    NUM_NULLS            NUMBER,
    NUM_BUCKETS          NUMBER,
    LAST_ANALYZED        DATE,
    SAMPLE_SIZE          NUMBER,
    CHARACTER_SET_NAME   VARCHAR2(44),
    CHAR_COL_DECL_LENGTH NUMBER,
    GLOBAL_STATS         VARCHAR2(3),
    USER_STATS           VARCHAR2(3),
    AVG_COL_LEN          NUMBER,
    CHAR_LENGTH          NUMBER,
    CHAR_USED            VARCHAR2(1),
    V80_FMT_IMAGE        VARCHAR2(3),
    DATA_UPGRADED        VARCHAR2(3),
    HISTOGRAM            VARCHAR2(15));

  type all_tab_columns_array is table of all_tab_columns;

  procedure get_all_tab_columns(no integer, cols out all_tab_columns_array);

  procedure tab_columns_ident(rein all_tab_columns_array,
                              raus out all_tab_columns_array);

  type tabi_r1 is table of r1 index by binary_integer;
  type tabv_r1 is table of r1 index by varchar2(200);

  procedure p_tabi_r1(x in tabi_r1, y out tabi_r1);
  procedure p_tabv_r1(x in tabv_r1, y out tabv_r1);

  procedure o1(x in test_object, y out test_object);

  procedure testo;

  procedure testuni1(x out varchar2,y out integer);

end;
/
create or replace package body test_pypub1 is

  string_array_p7_p8 string_array;
  number_array_p7_p8 number_array;

  procedure p0(a  number,
               b  varchar2,
               c  date,
               d  raw,
               oa out number,
               ob out varchar2,
               oc out date,
               od out raw) is
  begin
    oa := a;
    ob := b;
    oc := c;
    od := d;
  end;

  procedure p1(x table_, z out table_) is
    v table_;
  begin
    for i in x.first .. x.last loop
      null;
      --plog.info('x' || i, '' || x(i).a || '|' || x(i).b);
    end loop;
    v := new Table_();
    for i in 1 .. 5 loop
      v.extend();
      v(v.last).a := i;
      v(v.last).b := 'abcd-' || i;
      v(v.last).c := to_date('13-9-2005', 'dd-mm-yyyy') + i;

    end loop;
    z := v;
  end;

  procedure p2(x r1, y r2, z out r2) is
    f r1;
    t t1;
  begin
    --plog.info('p2.x', x.a || ',' || x.b || ',' || x.c || ',' || x.d);
    f := y.a;
    --plog.info('p2.y.a', f.a || ',' || f.b || ',' || f.c || ',' || f.d);
    t := y.b;
    for i in t.first .. t.last loop
      f := t(i);
      --plog.info('p2.y(' || i || ').a',
      --          f.a || ',' || f.b || ',' || f.c || ',' || f.d);
    end loop;
  end;

  procedure p2b(a out r2) is
    res r2;
  begin
    res.a.a := 1223.1233;
    res.a.b := 1221;
    res.a.c := 'assas';
    res.a.d := sysdate;
    res.b   := t1();
    res.b.extend(1);
    res.b(res.b.last).a := 1991;
    res.b(res.b.last).b := 1;
    res.b(res.b.last).c := 'kawumm';
    res.b(res.b.last).d := sysdate + 1999;
  end;

  procedure p2c(a in r2, b out r2) is
  begin
    b := a;
  end;

  procedure p3(a varchar2, b out varchar2) is
  begin
    --plog.info('p3.a', a);
    if a is null then
      b := null;
    else
      b := 'q' || substr(a, 2, length(a) - 2) || 'r';
    end if;
    --plog.info('p3', 'done');
  end;

  procedure p4(a number,
               b integer,
               c date,
               x out number,
               y out integer,
               z out date) is
  begin
    x := a + 1;
    y := b + 1;
    z := c + 1;
  end;

  procedure p5(x out t1, y in t1) is
    res t1;
  begin
    res := new t1();
    if y.first is not null then
      for i in y.first .. y.last loop
        res.extend();
        res(res.last) := y(y.last + y.first - i);
      end loop;
    end if;
    x := res;
  end;

  procedure p6(a varchar2, b out varchar2) is
  begin
    --plog.info('p6.a', a);
    b := a || 'äöüß';
    --plog.info('p6', 'done');
  end;

  procedure p7(a in number_array, b in string_array) is
  begin
    string_array_p7_p8 := b;
    number_array_p7_p8 := a;
  end;

  procedure p8(a out number_array, b out string_array) is
  begin
    a := number_array_p7_p8;
    b := string_array_p7_p8;
  end;

  procedure p9(a in raw, b out raw) is
  begin
    b := a;
  end;

  procedure p10(a in varchar2, b out varchar2) is
  begin
    raise_application_error(-20001, 'aua');
  end;

  procedure t1_ident(x t1, y out t1) is
  begin
    y := x;
  end;

  procedure get_all_tab_columns(no integer, cols out all_tab_columns_array) is
    res all_tab_columns_array := all_tab_columns_array();
  begin
    select OWNER,
           TABLE_NAME,
           COLUMN_NAME,
           DATA_TYPE,
           DATA_TYPE_MOD,
           DATA_TYPE_OWNER,
           DATA_LENGTH,
           DATA_PRECISION,
           DATA_SCALE,
           NULLABLE,
           COLUMN_ID,
           DEFAULT_LENGTH,
           --DATA_DEFAULT     ,
           NUM_DISTINCT,
           -- LOW_VALUE,
           -- HIGH_VALUE,
           DENSITY,
           NUM_NULLS,
           NUM_BUCKETS,
           LAST_ANALYZED,
           SAMPLE_SIZE,
           CHARACTER_SET_NAME,
           CHAR_COL_DECL_LENGTH,
           GLOBAL_STATS,
           USER_STATS,
           AVG_COL_LEN,
           CHAR_LENGTH,
           CHAR_USED,
           V80_FMT_IMAGE,
           DATA_UPGRADED,
           HISTOGRAM bulk collect
      into res
      from all_tab_columns
     where rownum < no;
    cols := res;
  end;

  procedure tab_columns_ident(rein all_tab_columns_array,
                              raus out all_tab_columns_array) is
  begin
    raus := rein;
  end;

  procedure p_tabi_r1(x in tabi_r1, y out tabi_r1) is
  begin
    y := x;
  end;

  procedure p_tabv_r1(x in tabv_r1, y out tabv_r1) is
  begin
    y := x;
  end;

  procedure o1(x in test_object, y out test_object) is
  begin
    y := x;
  end;

  -- check if object identity remains
  procedure testo is
    x test_object2;
    y test_object;
    z test_object2;
  --  u ref obla;
  begin
    x := test_object2('a', 1, sysdate, 'x');
    y := x;
    z := treat(y as test_object2);
    dbms_output.put_line(z.v);
    x.v := 'a';
    dbms_output.put_line(z.v);
    --u:= ref x;
  end;

  procedure testuni1(x out varchar2,y out integer) is
    res varchar(2000 char);
    begin
      for i in 0 .. 256 loop
        res:= res||chr(i);
      end loop;
      x:= res;
      y:= 1234;
      dbms_output.put_line(lengthc(res));
       dbms_output.put_line(lengthb(res));
       dbms_output.put_line(length2(res));
       dbms_output.put_line(length4(res));
    end;

begin
  null;
  --plog.log_level := plog.level_debug;
end;
/
