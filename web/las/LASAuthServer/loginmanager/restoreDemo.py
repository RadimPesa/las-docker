import MySQLdb
import time

def restoreDemo():
    outcome=False
    db=MySQLdb.connect('192.168.122.9','lasauthserver','lasauthsrvpwd2012','lasauthserver')
    db.query("SELECT count(*) from loginmanager_lasuser_logged_in_module where id in (select id from django_session where expire_date > DATE(NOW()))")
    res=db.store_result()
    if int(res.fetch_row()[0][0])==0: #NO LOGGATI
        db.query("SELECT COUNT(*) from loginmanager_demorestore")
        res=db.store_result()    
        if len(res.fetch_row())==0: #Zero restore, lo faccio
           outcome=restore_db()
        else:
            db.query("SELECT id FROM loginmanager_demorestore WHERE end_datetime = (SELECT MAX(end_datetime) from loginmanager_demorestore) AND end_datetime < (SELECT MAX(expire_date) from django_session)")
            res=db.store_result()
            if len(res.fetch_row())>0: #SI DEVE RESTORARE
                outcome=restore_db()
        print outcome
        



def restore_db():
    db=MySQLdb.connect('192.168.122.9','lasauthserver','lasauthsrvpwd2012','lasauthserver')
    cur = db.cursor()
    try:
        cur.execute("INSERT INTO loginmanager_demorestore (start_datetime) values (NOW())")
    except Exception,e:
        print "Exception in creating restore record",e
        return False
    db.commit()
    time.sleep(30)
    try:
        cur.execute("UPDATE loginmanager_demorestore set end_datetime =NOW() where end_datetime IS NULL")
    except Exception,e:
        print "Exception in finalizing restore record",e
        return False
    db.commit()
    return True



if __name__ == "__main__":
    restoreDemo()
