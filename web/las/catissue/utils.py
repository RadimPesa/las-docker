def getLASUrl():
    from settings import DB_NAME,DB_USERNAME,DB_PASSWORD,DB_HOST
    try:
        import _mysql
        db=_mysql.connect(DB_HOST,DB_USERNAME,DB_PASSWORD,DB_NAME)
        db.query(" " " SELECT domain FROM django_site WHERE name='LASDomain' " " ")
        r=db.use_result()
        tup=r.fetch_row()
        return tup[0][0]
    except Exception,e:
        print 'Error retrieving LAS Url:',e
        return ''