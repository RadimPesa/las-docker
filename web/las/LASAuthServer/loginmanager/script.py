from django.conf import settings

def runInParallel(*fns):
    from multiprocessing import Process
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()


def resetDatabases():
    import time
    print 'start reset databases',time.time()
    import subprocess
    ret = subprocess.call(["ssh", "administrator@"+ settings.DB_HOST, "sudo /home/administrator/LAS/backup_demo/script/recover-db-data.sh"])
    print ret

    # or, with stderr:
    #process = Popen('mysql %s -u%s' % ('caxeno', 'root'),stdout=PIPE, stdin=PIPE, shell=True)
    #output = process.communicate('source /srv/www/LASAuthServer/loginmanager/0.resetDatabase.sql')[0]
    print 'end reset databases',time.time()





def resetCaxeno():
    from subprocess import Popen, PIPE
    import time
    print 'start reset caxeno',time.time()
    #process = Popen('mysql %s -u%s' % ('caxeno', 'root'),stdout=PIPE, stdin=PIPE, shell=True)
    #output = process.communicate('source /srv/www/LASAuthServer/loginmanager/0.resetDatabase.sql')[0]
    print 'end reset caxeno',time.time()

def resetBiobank():
    import time
    from subprocess import Popen, PIPE
    print 'start reset biobank',time.time()
    #process = Popen('mysql %s -u%s' % ('biobanca', 'root'),stdout=PIPE, stdin=PIPE, shell=True)
    #output = process.communicate('source /srv/www/LASAuthServer/loginmanager/AggiornamentoBanca.sql')[0]
    print 'end reset biobank',time.time()

def resetStorage():
    import time
    from subprocess import Popen, PIPE
    print 'start reset storage',time.time()
    #process = Popen('mysql %s -u%s' % ('storage', 'root'),stdout=PIPE, stdin=PIPE, shell=True)
    #output = process.communicate('source /srv/www/LASAuthServer/loginmanager/AggiornamentoStorage.sql')[0]
    print 'end reset storage',time.time()


def resetMicro():
    import time
    from subprocess import Popen, PIPE
    print 'start reset uarray',time.time()
    #process = Popen('mysql %s -u%s' % ('uarray', 'root'),stdout=PIPE, stdin=PIPE, shell=True)
    #output = process.communicate('source /srv/www/LASAuthServer/loginmanager/uarray_demo.sql')[0]
    print 'end reset uarray',time.time()


