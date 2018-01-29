class MyApp2Router(object):
    """
    A router to control all database operations on hamilton models
    """

    def db_for_read(self, model, **hints):        
        if model._meta.app_label == 'hamiltonapp':
            return 'dbhamilton'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'hamiltonapp':
            return 'dbhamilton'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'hamiltonapp' and obj2._meta.app_label == 'hamiltonapp':
            return True
        elif 'hamiltonapp' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return True
        return False

    def allow_syncdb(self, db, model):
        if db == 'dbhamilton':
            return model._meta.app_label == 'hamiltonapp'
        elif model._meta.app_label == 'hamiltonapp':
            return False
        return None
