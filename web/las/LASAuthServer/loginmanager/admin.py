from loginmanager.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

'''
class MyUserAdmin(UserAdmin):
    fields = list(UserAdmin.fieldsets[0][1]['fields'])
    fields.append('modules')
    filter_horizontal = ('modules',)
    def __init__(self,*args,**kwargs):
        super(MyUserAdmin,self).__init__(*args,**kwargs)
'''
'''
class LASUserAdmin(admin.ModelAdmin):
    filter_horizontal = ['modules']
'''

class LASUserAdmin(UserAdmin):
    def __init__(self,*args,**kwargs):
        super(LASUserAdmin,self).__init__(*args,**kwargs)
        fields = list(UserAdmin.fieldsets[0][1]['fields'])
        fields.append('modules')
        filter_horizontal = ['modules']
        UserAdmin.fieldsets[0][1]['fields'] = fields
        UserAdmin.filter_horizontal = filter_horizontal

admin.site.unregister(User)
admin.site.register(LASUser,LASUserAdmin)

admin.site.register(LASModule)
admin.site.register(LASPermission)

admin.site.register(Activity)
admin.site.register(LASVideo)
