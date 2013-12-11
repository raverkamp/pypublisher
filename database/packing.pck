create or replace package packing is

  sep          constant varchar2(1) := ';';
  esc          constant varchar2(1) := '\';
  co_accu_size constant integer := 100;

  function escape(v varchar2) return varchar2;
  function descape(v varchar2) return varchar2;
  
  function str_to_number(x varchar2) return number;

  type tab is table of varchar2(32000);
  data      tab;
  tab_index integer;
  str_pos   integer;
  accu      varchar2(32000);

  procedure store(v varchar2);

  procedure store10(v1  varchar2,
                    v2  varchar2,
                    v3  varchar2,
                    v4  varchar2,
                    v5  varchar2,
                    v6  varchar2,
                    v7  varchar2,
                    v8  varchar2,
                    v9  varchar2,
                    v10 varchar2);

  procedure clear;

  --procedure test1;
  procedure start_read;

  procedure put(v in varchar2);
  procedure get(v out varchar2);

  procedure putv(v in varchar2);
  procedure getv(v out varchar2);

  procedure putn(v in number);
  procedure getn(v out number);

  procedure putd(v in date);
  procedure getd(v out date);
  
  procedure putg(v in raw);
  procedure getg(v out raw);

  type string_array is table of  varchar2(2000 char);
  function get_data return string_array
    pipelined;

end;
/
create or replace package body packing is

  sep_repl varchar2(1) := 'a';
  esc_repl varchar2(1) := 'b';

  procedure p(v varchar2) is
  begin
    dbms_output.put_line(v);
  end;

  function escape(v varchar2) return varchar2 is
  begin
    return replace(replace(v, esc, esc || esc_repl), sep, esc || sep_repl);
  end;

  function descape(v varchar2) return varchar2 is
  begin
    return replace(replace(v, esc || sep_repl, sep), esc || esc_repl, esc);
  end;

  -- schiebe Daten in so grossen brocken wie möglich rüber.
  -- wir interessieren uns an dieser Stelle nicht wie die Daten separiert werden.
  procedure store(v varchar2) is
  begin
    --plog.info('store', 'Size:'|| length(v)||'   >'||substr(v, 1, 200));
    data.extend();
    data(data.last) := v;
    -- oder wenn aktueller String klein dann dran pappen.
  end;

  procedure store10(v1  varchar2,
                    v2  varchar2,
                    v3  varchar2,
                    v4  varchar2,
                    v5  varchar2,
                    v6  varchar2,
                    v7  varchar2,
                    v8  varchar2,
                    v9  varchar2,
                    v10 varchar2) is
  begin
    store(v1);
    store(v2);
    store(v3);
    store(v4);
    store(v5);
    store(v6);
    store(v7);
    store(v8);
    store(v9);
    store(v10);
  end;

  -- Längen Kodierung 0,1,2,3,4,5,6,7,8,9 Zeichen oder a12 oder b12345 Zeichen

  -- Zustand ist acc plus pos in acc plus index

  -- oder  finde nächsten CR => Problem Strings sind evtl doppelt so lang
  --  also Strings maximal 10000 reicht eigentlich

  -- Zustand index,pos

  procedure start_read is
  begin
    store(accu);
    tab_index := data.first;
    str_pos   := 1;
  end;

  procedure get(v out varchar2) is
    res varchar2(32000) := '';
    pos integer;
  begin
    --plog.info('pos','pos: '||str_pos);
    loop
      pos := instr(data(tab_index), sep, str_pos);
      p('p: ' || pos);
      if pos > 0 then
        res := res || substr(data(tab_index), str_pos, pos - str_pos);
        if pos >= length(data(tab_index)) then
          data(tab_index) := ''; -- clear read data
          tab_index := tab_index + 1;
          str_pos := 1;
        else
          str_pos := pos + 1;
        end if;
        v := descape(res);
      -- plog.info('got',substr(v,1,20)||substr(v,-10));
        return;
      else
        res := res || substr(data(tab_index), str_pos);
        data(tab_index) := ''; -- clear read data
        tab_index := tab_index + 1;
        str_pos := 1;
      end if;
    end loop;
  end;

  procedure put(v in varchar2) is
    a varchar2(32000);
  begin
    --plog.info('x',v);
    a := v || sep;
    if nvl(length(a), 0) + nvl(length(accu), 0) > co_accu_size then
      store(accu);
      accu := a;
    else
      accu := accu || a;
    end if;
    p('#' || accu);
  end;

  procedure putv(v in varchar2) is
  begin
    put(escape(v));
  end;

  procedure getv(v out varchar2) is
  begin
    get(v);
  end;

  procedure putn(v in number) is
  begin
    put(to_char(v, 'TM', 'NLS_NUMERIC_CHARACTERS = ''.x'''));
  end;
  
  function str_to_number(x varchar2) return number is
    p integer;
  begin
    if x is null then
      return null;
    end if;
    p:= instr(x,'.');
    if p=0 then
      return to_number(x);
    else
      return to_number(substr(x,1,p-1)) 
        + to_number(substr(x,p),
             '.9999999999999999999999999999999999999999',
                   'NLS_NUMERIC_CHARACTERS = ''.,''');
    end if;
  end; 
  

  procedure getn(v out number) is
    x varchar(500);
  begin
    get(x);
    v:= str_to_number(x);
  end;

  procedure putd(v in date) is
  begin
    put(to_char(v, 'yyyy-mm-dd HH24:MI:SS'));
  end;

  procedure getd(v out date) is
    x varchar2(25);
  begin
    get(x);
    v := to_date(x, 'yyyy-mm-dd HH24:MI:SS');
  end;

 procedure putg(v in raw) is
  begin
    put(rawtohex(v));
  end;

  procedure getg(v out raw) is
    x varchar2(32);
  begin
    get(x);
    v:=hextoraw(x);
  end;

  procedure clear is
  begin
    --plog.info('clear', '-');
    data := new tab();
    accu := '';
  end;

  function get_data return string_array
    pipelined is
    v varchar2(32000);
    p integer;
  begin
    if data.first is not null then
      for i in data.first .. data.last loop
        v := data(i);
        p := 1;
        while p <= length(v) loop
          --plog.info('y',substr(v, p, 100));
          pipe row(substr(v, p, 100));
          p := p + 100;
        end loop;
      end loop;
    end if;
  end;

-- wie wird raus geschrieben?
--das zeug wird per select geholt?
-- einfach erstmal speichern im Array?
-- immmer concat ist teuer O(n^2)!

end ;
/
