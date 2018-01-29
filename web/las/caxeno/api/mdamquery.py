from django.db import connection
import os
import inspect
import json
import zlib
import re
from math import ceil

from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt

from mdamconf import app_name, models_to_exclude, external_models_to_include

AND   = 0
IN    = 1
OR    = 2
NOTIN = 3
GB    = 4
GENID = 5
QE    = 6
DISTINCT = 7
STAR = 8
MIN = 9
MAX = 10
AVG = 11

phi = {MIN: 'min', MAX: 'max', AVG: 'avg'}

column_types = {2: 'date', 3: 'double', 4: 'varchar(1024)', 5: 'varchar(1024)', 10: 'int(11)'}

HANDLE_KEY_ATTR = 'id'
HANDLE_FILTER_ATTR = 'x'

OP_MAP = { "<": "< all", ">": "> all", "=": "in", "<>": "not in"}
MAX_FW_LEN = 100
BULK_INSERT_SIZE = 30000

def GetDbSchemaHandler(request):
    e = {}
    r = []
    from django.db import models
    all_models = models.get_models()
    for obj in all_models:
        if (obj._meta.app_label == app_name and obj._meta.object_name not in models_to_exclude) or ((obj._meta.app_label, obj._meta.object_name) in external_models_to_include):
            this_db_table = obj._meta.db_table
            f = []
            for x in obj._meta.local_fields:
                f.append(x.column)
                if x.rel:
                    r.append((this_db_table, x.rel.to._meta.db_table, x.column, x.rel.to._meta.pk.column))
            e[this_db_table] = {'pkey': obj._meta.pk.column, 'fields': f}
    return HttpResponse(json.dumps({'entities': e, 'relationships': r}))

@csrf_exempt
def CleanupQuery(request):
    if request.method != 'POST':
        return HttpResponseServerError("allowed methods: POST")

    try:
        handles = request.POST.getlist('handles')
        temptables = request.POST.getlist('temptables')
    except:
        return HttpResponseServerError(json.dumps(['Error', 'Invalid syntax']))

    cursor = connection.cursor()
    for x in handles:
        try:
            print "drop view " + x
            cursor.execute("drop view " + x)
        except:
            pass

    for x in temptables:
        try:
            print "drop table " + x
            cursor.execute("drop table " + x)
        except:
            pass

    return HttpResponse("ok")

@csrf_exempt
def MakePhi(request):
    if request.method != 'POST':
        return HttpResponseServerError("allowed methods: POST")
    print request.POST
    try:
        table = request.POST['table']
        fk = request.POST['fk']
        attr = request.POST['attr']
        f = phi[int(request.POST['phi'])]
    except Exception as e:
        return HttpResponseServerError(json.dumps(['Error', 'Invalid syntax']))
    cursor = connection.cursor()
    view_name = "%s_%s_%s" % (table, f, attr)
    try:
        r = cursor.execute("show tables like %s", [view_name])
    except Exception as e:
        return HttpResponseServerError(json.dumps(['Error', str(e)]))
    if r > 0:
        return HttpResponse(json.dumps(['Exists', view_name]))
    try:
        cursor.execute("create view %s as select `%s`.`%s` as `%s`, %s(`%s`.`%s`) as `%s` from `%s` group by `%s`.`%s`" % (view_name, table, fk, HANDLE_KEY_ATTR, f, table, attr, HANDLE_FILTER_ATTR, table, table, fk))
        print "create view %s as select `%s`.`%s` as `%s`, %s(`%s`.`%s`) as `%s` from `%s` group by `%s`.`%s`" % (view_name, table, fk, HANDLE_KEY_ATTR, f, table, attr, HANDLE_FILTER_ATTR, table, table, fk)
        return HttpResponse(json.dumps(['Created', view_name]))
    except Exception as e:
        return HttpResponseServerError(json.dumps(['Error', str(e)]))




@csrf_exempt
def RunQuery(request):
    if request.method != 'POST':
        return HttpResponseServerError("allowed methods: POST")

    try:
        data = json.loads(zlib.decompress(request.body))
    except:
        print "An exception occurred while decompressing, will treat as uncompressed content"
        data = json.loads(request.body)

    try:
        from_list = data['f']
        select_list = data['s']
        get_handle = data['geth']
    except:
        return HttpResponseServerError(json.dumps(['Error', 'Invalid syntax']))

    distinct = data['distinct'] if 'distinct' in data else False

    # join where, filter where
    join_where_list = data['jw'] if 'jw' in data else []
    filter_where_list = data['fw'] if 'fw' in data else []

    #left outer join
    outer_join_list = data['oj'] if 'oj' in data else []

    # group by
    groupby_list = data['gb'] if 'gb' in data else []
    
    # having
    having_list = data['h'] if 'h' in data else []
    
    # limit
    limit = data['l'] if 'l' in data else None
    
    # secondary query type
    sec_type = data['sec_type'] if 'sec_type' in data else None
    
    # secondary query attribute
    sec_attr = data['sec_attr'] if 'sec_attr' in data else None
    
    # secondary query handle
    sec_src = data['sec_src'] if 'sec_src' in data else None

    #sesskey
    view_name = data['viewname'] if 'viewname' in data else None
        
    # from, select, get_handle
    dataTables = data['tables'] if 'tables' in data else []
        
    #m = __import__('_caQuery').models
    #c = getattr(m, target)

    # save primary key values in a temporary table for future use (e.g., translators)
    # it assumes (i.e. requires) that the primary key is the first item in the select list
    savePrimaryKeys = data['save_pk'] if 'save_pk' in data else False

    try:
        
        # select clause with distinct
        select_clause = "select "
        if get_handle or distinct:
            select_clause += "distinct "
        select_clause += ", ".join(["`" + x[0] + "`.`" + x[1] + "`" if len(x) == 2 else x[0] for x in select_list])

        """
        # from clause
        from_clause = " from "
        from_clause += "`" + from_list[0] + "`"
        from_clause += ", ".join(["".join([" left outer join `" + x[3] + "` on `" + x[0] + "`.`" + x[1] + "`" + x[2] + "`" + x[3] + "`.`" + x[4] + "`" for x in outer_join_list])] + ["`" + x + "`" for x in from_list[1:]])
        
        # join where
        # clause syntax:
        #  0             1              2         3             4              5        6       7        8
        # (table_name_1, column_name_1, operator, table_name_2, column_name_2, before1, after1, before2, after2)
        join_where = []
        """
        e = re.compile('drop|delete', re.IGNORECASE)
        for x in join_where_list:
            for i in xrange(5, 9):
                x[i] = x[i] or ""
                x[i] = e.sub("", x[i])
        """
            join_where.append("%s`%s`.`%s`%s %s %s`%s`.`%s`%s" % (x[5], x[0], x[1], x[6], x[2], x[7], x[3], x[4], x[8]))

        join_where = " and ".join(join_where)
        """
        
        ### new code starts here
        # from clause (new)
        from_clause = " from "
        from_clause += "`" + from_list[0] + "`"
        prev_to = ''
        base_table = from_list[0]
        joined_table = {}
        for x in join_where_list:
            first_table, second_table = (x[0], x[3]) if x[3] != base_table else (x[3], x[0])
            if second_table not in joined_table:
                joined_table[second_table] = []
                joined_table[second_table].append(x)
            else:
                if first_table == base_table or first_table in joined_table:
                    joined_table[second_table].append(x)
                else:
                    joined_table[first_table] = []
                    joined_table[first_table].append(x)
            #inner_join_to = x[3] if x[3] not in tables_from else x[0]
            #tables_from.add(inner_join_to)
            #if prev_to == inner_join_to:
            #    from_clause += " and "
        joined_table = joined_table.items()
        tables_from = set()
        tables_from.add(base_table)
        for inner_join_to, conditions in joined_table:
            # don't try to instantiate a table until all of the tables mentioned in its join conditions have been instantiated
            # (if so, enqueue it and leave it until later)
            enqueue = False
            for c in conditions:
                other_table = c[0] if c[0] != inner_join_to else c[3]
                if other_table not in tables_from:
                    enqueue = True
                    break
            if enqueue:
                joined_table.append((inner_join_to, conditions))
                continue

            tables_from.add(inner_join_to)
            
            outer_join = reduce(lambda x, y: x or y, [z[9] for z in conditions])
            if outer_join == False:
                from_clause += " inner join `%s` on " % inner_join_to
            else:
                from_clause += " left outer join `%s` on " % inner_join_to
            #prev_to = inner_join_to
            from_clause += " and ".join(["%s`%s`.`%s`%s %s %s`%s`.`%s`%s" % (x[5], x[0], x[1], x[6], x[2], x[7], x[3], x[4], x[8]) for x in conditions])
        '''
        for x in outer_join_list:
            from_clause += " left outer join `%s` on `%s`.`%s` %s `%s`.`%s`" % (x[3], x[0], x[1], x[2], x[3], x[4])
        '''

        join_where = ''
        ### new code ends here


        # filter where
        # clause syntax:
        #  0           1            2         3            4                              5                             6
        # (table_name, column_name, operator, values_list, before table_name+column_name, after table_name+column_name, extra_for_each_value)
        temptables = []
        filter_where = []

        for x in filter_where_list:
            for i in xrange(4, 6):
                x[i] = x[i] or ""
                x[i] = e.sub("", x[i])

            if x[6] != None:
                filter_where.append(" or ".join(["(%s`%s`.`%s`%s %s '%s' %s)" % (x[4], x[0], x[1], x[5], x[2], y, z if z else "") for y,z in zip(x[3],x[6])]))
            else:
                if len(x[3]) == 0:
                    filter_where.append("(false)")
                elif len(x[3]) < MAX_FW_LEN or x[2] not in OP_MAP:
                    filter_where.append("(" + " or ".join(["%s`%s`.`%s`%s %s '%s'" % (x[4], x[0], x[1], x[5], x[2], y) for y in x[3]]) + ")")
                else:
                    ttname = "__temp__" +  os.urandom(10).encode("hex")
                    temptables.append((ttname, x[3]))
                    filter_where.append("%s`%s`.`%s`%s %s (select x from `%s`)" % (x[4], x[0], x[1], x[5], OP_MAP[x[2]], ttname))
            #elif x[4] == 'all':
            #    filter_where.append("`%s`.`%s` not in (select `%s`.`%s` from `%s` where not (" % (x[6], x[7], x[0], x[5], x[0]) + 
            #        (" or " if x[2] != "<>" else " and ").join(["`%s`.`%s` %s '%s'" % (x[0], x[1], x[2], y) for y in x[3]]) +
            #        "))")

        filter_where = " and ".join(filter_where)

        # merge all wheres to build where clause
        if len(join_where) > 0 or len(filter_where) > 0 or sec_type in [IN, NOTIN]:
            where_clause = " where "
            where = []
            
            if len(join_where) > 0:
                where.append(join_where)

            if len(filter_where) > 0:
                where.append(filter_where)
            
            if sec_type == IN:
                where.append("`%s`.`%s`" % tuple(sec_attr) + " in (select " + HANDLE_KEY_ATTR + " from " + sec_src + ")")
            elif sec_type == NOTIN:
                where.append("`%s`.`%s`" % tuple(sec_attr) + " not in (select " + HANDLE_KEY_ATTR + " from " + sec_src + ")")

            where_clause += " and ".join(where)
        else:
            where_clause = ""

        # group by clause
        if len(groupby_list) > 0:
            groupby_clause = " group by "
            groupby_clause += ", ".join(["`" + x[0] + "`.`" + x[1] + "`" for x in groupby_list])
        else:
            groupby_clause = ""

        # having clause syntax:
        #  1                   2         3             4           5               6             7
        # (aggregate operator, star Y/N, distinct Y/N, table_name, attribute_name, cmp_operator, value)
        if len(having_list) > 0:
            having_clause = " having "
            having_clause += " and ".join([x[0] + "(" + ("*" if x[1] and int(x[1]) == STAR else ("distinct " if x[2] and int(x[2]) == DISTINCT else "" + "`" + x[3] + "`.`" + x[4] + "`")) + ")" + x[5] + "'" + x[6] + "'" for x in having_list])
        else:
            having_clause = ""

        if limit:
            limit_clause = " limit " + str(limit)
        else:
            limit_clause = ""

        if sec_type == OR:
            union_clause = " union select " + HANDLE_KEY_ATTR + " from " + sec_src
        else:
            union_clause = ""

    except Exception,e:
        return HttpResponseServerError(json.dumps(["Error", str(e)]))


    #print select_clause + from_clause + where_clause + groupby_clause + having_clause + limit_clause
    #return select_clause + from_clause + where_clause + genid_clause + groupby_clause + having_clause + limit_clause
    try:
        temp = "temporary " if not get_handle else ""
        cursor = connection.cursor()
        # create data tables
        for x in dataTables:
            col_def = '('
            col_list = '('
            for c in x['columns']:
                col_def += c['name'] + ' ' + column_types[c['type']] + ', '
                col_list += c['name'] + ', '
            col_def = col_def[:-2] + ')'
            col_list = col_list[:-2] + ')'
            print "create " + temp + "table " + x['name'] + " " + col_def + " engine=memory"
            cursor.execute("create " + temp + "table " + x['name'] + " " + col_def + " engine=memory")
            n = int(ceil(float(len(x['data']))/BULK_INSERT_SIZE))
            for i in xrange(0,n):
                ll = x['data'][i*BULK_INSERT_SIZE:(i+1)*BULK_INSERT_SIZE]
                s = "insert into " + x['name'] + col_list + " values" + ",".join(["("+ ",".join(["'" + str(w) + "'" for w in z]) +")" for z in ll])
                cursor.execute(s)
            if 'indexed_column' in x:
                print "create index " + x['name'] + "_idx on " + x['name'] + "(%s) using hash" % x['indexed_column']
                cursor.execute("create index " + x['name'] + "_idx on " + x['name'] + "(%s) using hash" % x['indexed_column'])
        
        for x in temptables:
            print "create " + temp + "table " + x[0] + " (x varchar(255)) engine=memory"
            cursor.execute("create " + temp + "table " + x[0] + " (x varchar(255)) engine=memory")
            n = int(ceil(float(len(x[1]))/BULK_INSERT_SIZE))
            for i in xrange(0,n):
                ll = x[1][i*BULK_INSERT_SIZE:(i+1)*BULK_INSERT_SIZE]
                s = "insert into " + x[0] + "(x) values" + ",".join(["('"+z+"')" for z in ll])
                cursor.execute(s)
            print "create index " + x[0] + "_idx on " + x[0] + "(x) using hash"
            cursor.execute("create index " + x[0] + "_idx on " + x[0] + "(x) using hash")

        if get_handle:
            ttname = view_name
            view_attrs = [HANDLE_KEY_ATTR] + ["attr_" + str(i) for i in xrange(0,len(select_list)-1)]
            print          "create view " + ttname + "(" + ", ".join(view_attrs)  + ") as " + select_clause + from_clause + where_clause + groupby_clause + having_clause + union_clause + limit_clause
            cursor.execute("create view " + ttname + "(" + ", ".join(view_attrs)  + ") as " + select_clause + from_clause + where_clause + groupby_clause + having_clause + union_clause + limit_clause)
            return HttpResponse(json.dumps([ttname] + [x[0] for x in temptables] + [x['name'] for x in dataTables]))
        else:
            print select_clause + from_clause + where_clause + groupby_clause + having_clause + union_clause + limit_clause
            cursor.execute(select_clause + from_clause + where_clause + groupby_clause + having_clause + union_clause + limit_clause)
            res = cursor.fetchall()

            if savePrimaryKeys == True:
                print "create table " + view_name + " engine=memory select " + ("distinct " if distinct == True else "" ) + "`" + select_list[0][0] + "`.`" + select_list[0][1] + "`" + from_clause + where_clause + groupby_clause + having_clause + union_clause + limit_clause
                cursor.execute("create table " + view_name + " engine=memory select " + ("distinct " if distinct == True else "" ) + "`" + select_list[0][0] + "`.`" + select_list[0][1] + "`" + from_clause + where_clause + groupby_clause + having_clause + union_clause + limit_clause)
                print "create index " + view_name + "_idx on " + view_name + "(" + select_list[0][1] + ")"
                cursor.execute("create index " + view_name + "_idx on " + view_name + "(" + select_list[0][1] + ")")

            for x in temptables:
                cursor.execute("drop table " + x[0])
            return HttpResponse(zlib.compress(json.dumps(res, default=lambda x:str(x))), content_type="application/octet-stream")
            #return HttpResponse(json.dumps(res))

    except Exception,e:
        return HttpResponseServerError(json.dumps(["Error", str(e)]))

