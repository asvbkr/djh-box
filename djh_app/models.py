from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.timezone import now

from TamTamBot import UpdateCmn
from TamTamBot.utils.utils import str_to_int
from openapi_client import User


class TtbAbstract(models.Model):
    created = models.DateTimeField(default=timezone.now, verbose_name='created')
    updated = models.DateTimeField(default=timezone.now, verbose_name='updated')

    class Meta:
        abstract = True

    def __str__(self):
        s = ''
        for field in self._meta.fields:
            s += '%s%s: %s' % (', ' if s else '', field.verbose_name, getattr(self, field.name))
        s = '<%s: |%s|>' % (self._meta.verbose_name, s)
        return s


class TtbAbstractEn(TtbAbstract):
    enabled = models.BooleanField(default=True, verbose_name='enabled')

    class Meta:
        abstract = True

    @classmethod
    def get_property_str(cls, property_set, p_type, code, def_val=None):
        # type: (QuerySet, str, str, str) -> str
        property_c = property_set.filter(p_type=p_type, code=code, enabled=True).first()
        if property_c:
            return property_c.value
        else:
            return def_val

    @classmethod
    def get_property_int(cls, property_set, p_type, code, def_val=None):
        # type: (QuerySet, str, str, int) -> int
        res_str = cls.get_property_str(property_set, p_type, code)
        return str_to_int(res_str, def_val)


class TtbDjSubscriber(TtbAbstractEn):
    chat_id = models.BigIntegerField(unique=True, verbose_name='chat id')
    chat_name = models.TextField(unique=False, verbose_name='chat name')
    participants_count = models.BigIntegerField(unique=False, default=0, verbose_name='participants_count')


class TtbUser(TtbAbstractEn):
    user_id = models.BigIntegerField(unique=True, verbose_name='user id')
    name = models.TextField(unique=False, null=True, verbose_name='name')
    username = models.TextField(unique=False, null=True, verbose_name='user name')
    language = models.CharField(max_length=10, unique=False, null=True, verbose_name='language')
    avatar_url = models.TextField(unique=False, null=True, blank=True, verbose_name='avatar url')
    full_avatar_url = models.TextField(unique=False, null=True, blank=True, verbose_name='full avatar url')
    is_bot = models.NullBooleanField(default=None, null=True, verbose_name='is bot')
    subscriber = models.ManyToManyField(TtbDjSubscriber, verbose_name='subscriber')

    @classmethod
    def update_or_create_by_tt_user(cls, u, user_id=None):
        # type: (User or None, int) -> (TtbUser, bool)
        dff = {'enabled': True, 'updated': now()}
        if u:
            user_id = u.user_id
            if u.name is not None:
                dff['name'] = u.name
            if u.username is not None:
                dff['username'] = u.username
            if hasattr(u, 'avatar_url') and u.avatar_url is not None:
                dff['avatar_url'] = u.avatar_url,
            if hasattr(u, 'full_avatar_url') and u.full_avatar_url is not None:
                dff['full_avatar_url'] = u.full_avatar_url
            dff['is_bot'] = u.is_bot
        if user_id is not None:
            return cls.objects.update_or_create(user_id=user_id, defaults=dff)
        else:
            return None, False

    @classmethod
    def update_or_create_by_update(cls, update):
        # type: (UpdateCmn) -> (TtbUser, bool)
        return cls.update_or_create_by_tt_user(update.user, update.user_id)


class TtbPrevStep(TtbAbstract):
    index = models.CharField(max_length=64, unique=True, null=False, verbose_name='index')
    update = models.TextField(unique=False, null=False, verbose_name='user update')
    user = models.ForeignKey(TtbUser, unique=False, on_delete=models.CASCADE, verbose_name='user')


class TtbDjChatAvailable(TtbAbstractEn):
    """
    Таблица кэша чатов-подписчиков subscriber, доступных для пользователя user
    Наличие строки означает что для пользователя user в принципе доступно управление подпиской на subscriber
    enabled в строке означает, что пользователь user отключил подписку на subscriber
    """
    user = models.ForeignKey(TtbUser, unique=False, on_delete=models.CASCADE, verbose_name='user')
    subscriber = models.ForeignKey(TtbDjSubscriber, unique=False, on_delete=models.CASCADE, verbose_name='subscriber')
    chat = models.TextField(unique=False, null=False, verbose_name='chat')
    permissions = models.TextField(unique=False, null=False, verbose_name='user update')

    class Meta:
        unique_together = (('user', 'subscriber'),)


class TtbDjLimitedButtons(TtbAbstract):
    index = models.CharField(max_length=64, unique=True, null=False, verbose_name='index')
    buttons = models.TextField(unique=False, null=False, verbose_name='user update')


class TtbPropertyAbstract(TtbAbstractEn):
    p_type = models.CharField(max_length=16, default='common', unique=False, verbose_name='type')
    code = models.CharField(max_length=32, unique=False, verbose_name='code')
    value = models.CharField(max_length=256, unique=False, verbose_name='value')
    description = models.TextField(unique=False, null=True, blank=True, verbose_name='description')

    class Meta:
        abstract = True
        unique_together = (('p_type', 'code', 'value'),)


class TtbUserProperty(TtbPropertyAbstract):
    db_user = models.ManyToManyField(TtbUser, verbose_name='user')


class TtbDjSubscriberProperty(TtbPropertyAbstract):
    db_chat = models.ManyToManyField(TtbDjSubscriber, verbose_name='chat')
