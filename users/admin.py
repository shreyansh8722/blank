from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea
from import_export.admin import ImportExportModelAdmin


class UserAdminConfig(ImportExportModelAdmin):
    model = NewUser
    search_fields = ('mobile_no', 'name')
    list_filter = ('mobile_no', 'name', 'is_active', 'is_staff')
    ordering = ('-joining_date',)
    list_display = ('id','user_type','mobile_no', 'alt_mobile_no', 'name',
                    'is_active')
    list_editable = ['user_type']
    fieldsets = (
        (None, {'fields': ('mobile_no',
         'is_mobile_no_verified', 'name', 'profile_pic')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',)}),
    )
    # formfield_overrides = {
    #     NewUser.about: {'widget': Textarea(attrs={'rows': 10, 'cols': 40})},
    # }
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_no','alt_mobile_no', 'name', 'password1', 'password2', 'is_active', 'is_staff', 'groups', 'profile_pic')}
         ),
    )


admin.site.register(NewUser, UserAdminConfig)

class OtpHistoryAdmin(admin.ModelAdmin):
    list_display = [f.name for f in OtpHistory._meta.fields]
    list_editable = []

admin.site.register(OtpHistory, OtpHistoryAdmin)

class UserLogAdmin(admin.ModelAdmin):
    list_display = [f.name for f in UserLog._meta.fields]
    list_editable = []

admin.site.register(UserLog, UserLogAdmin)