from django.contrib import admin
from djh_app.models import InputMessage, TtbUser, TtbPrevStep


# Register your models here.

def get_default_list_display(self):
    list_display = []
    for field in self._meta.fields:
        list_display.append(field.name)
    return tuple(list_display)


class InputMessageAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(InputMessage)


class TtbUserAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(TtbUser)


class TtbPrevStepAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(TtbPrevStep)


admin.site.register(InputMessage, InputMessageAdmin)
admin.site.register(TtbUser, TtbUserAdmin)
admin.site.register(TtbPrevStep, TtbPrevStepAdmin)
