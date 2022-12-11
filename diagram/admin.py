from django.contrib import admin

from diagram.models import Subdivision, Soldier, Activity, User

# Register your models here.
admin.site.register(User)
admin.site.register(Subdivision)
admin.site.register(Soldier)
admin.site.register(Activity)