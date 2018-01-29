def getLASUrl():
    try:
        import _mysql
        db=_mysql.connect('192.168.122.9','storageusr2','storagepwd2013','storage2')
        db.query(" " " SELECT domain FROM django_site WHERE name='LASDomain' " " ")
        r=db.use_result()
        tup=r.fetch_row()
        return tup[0][0]
    except Exception,e:
        print 'Error retrieving LAS Url:',e
        return ''