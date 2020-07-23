from django.contrib import admin
from djh_app.models import TtbUser, TtbPrevStep, TtbUserProperty, TtbDjSubscriber, TtbDjSubscriberProperty, TtbDjChatAvailable


# Register your models here.

def get_default_list_display(self, list_prev=None, list_last=None):
    list_display = []
    if list_prev:
        list_display.extend(list_prev)
    for field in self._meta.fields:
        list_display.append(field.name)
    if list_last:
        list_display.extend(list_last)
    return tuple(list_display)


class TtbDjSubscriberPropertyInline(admin.TabularInline):
    model = TtbDjSubscriberProperty.db_chat.through
    extra = 3


class TtbDjSubscriberAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(TtbDjSubscriber)
    inlines = [TtbDjSubscriberPropertyInline]
    search_fields = ['chat_name']
    list_filter = ['chat_type', 'language', 'created', 'updated']


class TtbUserPropertyInline(admin.TabularInline):
    model = TtbUserProperty.db_user.through
    extra = 3


class TtbUserAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(TtbUser)
    search_fields = ['name', 'username']
    list_filter = ['language', 'enabled', 'created', 'updated', 'is_bot']
    inlines = [TtbUserPropertyInline]


class TtbUserPropertyAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(TtbUserProperty)
    search_fields = ['code']
    list_filter = ['p_type', 'created', 'updated']
    inlines = [
        TtbUserPropertyInline,
    ]
    exclude = ('db_user',)


class TtbDjSubscriberPropertyAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(TtbDjSubscriberProperty)
    search_fields = ['code']
    list_filter = ['p_type', 'created', 'updated']
    inlines = [
        TtbDjSubscriberPropertyInline,
    ]
    exclude = ('db_chat',)


class TtbPrevStepAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(TtbPrevStep)


class TtbDjChatAvailableAdmin(admin.ModelAdmin):
    list_display = get_default_list_display(TtbDjChatAvailable)


admin.site.register(TtbUser, TtbUserAdmin)
admin.site.register(TtbUserProperty, TtbUserPropertyAdmin)
admin.site.register(TtbDjSubscriber, TtbDjSubscriberAdmin)
admin.site.register(TtbDjSubscriberProperty, TtbDjSubscriberPropertyAdmin)
admin.site.register(TtbPrevStep, TtbPrevStepAdmin)
admin.site.register(TtbDjChatAvailable, TtbDjChatAvailableAdmin)
