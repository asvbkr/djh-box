from django.contrib import admin
from djh_app.models import TtbUser, TtbPrevStep, TtbUserProperty, TtbDjSubscriber, TtbDjSubscriberProperty, TtbDjChatAvailable

# Register your models here.
from ttgb_cmn.cmn import Utils


class TtbDjSubscriberPropertyInline(admin.TabularInline):
    model = TtbDjSubscriberProperty.db_chat.through
    extra = 3


class TtbDjSubscriberAdmin(admin.ModelAdmin):
    list_display = Utils.get_default_list_display(TtbDjSubscriber)
    inlines = [TtbDjSubscriberPropertyInline]
    search_fields = ['chat_name']
    list_filter = ['chat_type', 'language', 'created', 'updated']


class TtbUserPropertyInline(admin.TabularInline):
    model = TtbUserProperty.db_user.through
    extra = 3


class TtbUserAdmin(admin.ModelAdmin):
    list_display = Utils.get_default_list_display(TtbUser)
    search_fields = ['name', 'username']
    list_filter = ['language', 'enabled', 'created', 'updated', 'is_bot']
    inlines = [TtbUserPropertyInline]


class TtbUserPropertyAdmin(admin.ModelAdmin):
    list_display = Utils.get_default_list_display(TtbUserProperty)
    search_fields = ['value', 'description']
    list_filter = ['p_type', 'code', 'created', 'updated']
    inlines = [
        TtbUserPropertyInline,
    ]
    exclude = ('db_user',)


class TtbDjSubscriberPropertyAdmin(admin.ModelAdmin):
    list_display = Utils.get_default_list_display(TtbDjSubscriberProperty)
    search_fields = ['value', 'description']
    list_filter = ['p_type', 'code', 'created', 'updated']
    inlines = [
        TtbDjSubscriberPropertyInline,
    ]
    exclude = ('db_chat',)


class TtbPrevStepAdmin(admin.ModelAdmin):
    list_display = Utils.get_default_list_display(TtbPrevStep)


class TtbDjChatAvailableAdmin(admin.ModelAdmin):
    list_display = Utils.get_default_list_display(TtbDjChatAvailable)


admin.site.register(TtbUser, TtbUserAdmin)
admin.site.register(TtbUserProperty, TtbUserPropertyAdmin)
admin.site.register(TtbDjSubscriber, TtbDjSubscriberAdmin)
admin.site.register(TtbDjSubscriberProperty, TtbDjSubscriberPropertyAdmin)
admin.site.register(TtbPrevStep, TtbPrevStepAdmin)
admin.site.register(TtbDjChatAvailable, TtbDjChatAvailableAdmin)
