def getLASUrl():
    try:
        import _mysql
        db=_mysql.connect('localhost','storageusr','storagepwd2012','storage')
        db.query(" " " SELECT domain FROM django_site WHERE name='LASDomain' " " ")
        r=db.use_result()
        tup=r.fetch_row()
        return tup[0][0]
    except Exception,e:
        print 'Error retrieving LAS Url:',e
        return ''