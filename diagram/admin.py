from django.contrib import admin

from diagram.models import Subdivision, Soldier, Activity, User, SoldierInfo

# Register your models here.
admin.site.register(User)
admin.site.register(Subdivision)
admin.site.register(Soldier)
admin.site.register(SoldierInfo)
admin.site.register(Activity)