from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.timezone import now

from TamTamBot import UpdateCmn
from ttgb_cmn.cmn import Utils
from openapi_client import User, ChatType


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

    def disable(self, remark=None):
        self.enabled = False
        self.updated = now()
        if remark is not None and hasattr(self, 'remark'):
            self.remark = f'{self.updated}: {remark}'
        self.save()

    def enable(self, remark=None):
        self.enabled = True
        self.updated = now()
        if remark is not None and hasattr(self, 'remark'):
            self.remark = f'{self.updated}: {remark}'
        self.save()

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
        return Utils.str_to_int(res_str, def_val)

    @classmethod
    def set_property(cls, property_set, p_type, code, value):
        for db_prop in property_set.filter(p_type=p_type, code=code):
            property_set.remove(db_prop)
        if value is not None:
            db_prop, created = cls.objects.update_or_create(p_type=p_type, code=code, value=value)
            property_set.add(db_prop)


class TtbAbstractEnRem(TtbAbstractEn):
    remark = models.TextField(verbose_name='remark', null=True, blank=True)

    class Meta:
        abstract = True


class TtbAbstractEnRemComment(TtbAbstractEnRem):
    comment = models.TextField(verbose_name='comment', null=True, blank=True)

    class Meta:
        abstract = True


class TtbDjSubscriber(TtbAbstractEn):
    chat_id = models.BigIntegerField(unique=True, verbose_name='chat id')
    chat_name = models.TextField(unique=False, verbose_name='chat name')
    chat_type = models.CharField(max_length=10, unique=False, default=ChatType.CHAT, verbose_name='chat_type')
    participants_count = models.BigIntegerField(unique=False, default=0, verbose_name='participants_count')
    language = models.CharField(max_length=20, unique=False, null=True, verbose_name='language')

    class Meta:
        ordering = ('chat_type', 'chat_name')

    def __str__(self):
        return f'{self.chat_name}{f" [{self.language}]" if self.language else ""} [{self.participants_count}] |{self.chat_id} / {self.pk}|'


class TtbUser(TtbAbstractEn):
    user_id = models.BigIntegerField(unique=True, verbose_name='user id')
    name = models.TextField(unique=False, null=True, verbose_name='name')
    username = models.TextField(unique=False, null=True, verbose_name='user name')
    language = models.CharField(max_length=10, unique=False, null=True, verbose_name='language')
    avatar_url = models.TextField(unique=False, null=True, blank=True, verbose_name='avatar url')
    full_avatar_url = models.TextField(unique=False, null=True, blank=True, verbose_name='full avatar url')
    is_bot = models.BooleanField(default=None, null=True, verbose_name='is bot')
    subscriber = models.ManyToManyField(TtbDjSubscriber, verbose_name='subscriber')

    class Meta:
        ordering = ('name', 'username')

    def __str__(self):
        return f'{self.name}{f" (@{self.username})" if self.username else ""}{f" [{self.language}]" if self.language else ""}' \
               f'{f" [is bot]" if self.is_bot else ""} |{self.user_id} / {self.pk}|'

    @staticmethod
    def need_disable_user_by_last_activity_days(user, days=120):
        # type: (User, int) -> bool
        disable_user = False
        nt = now()
        ut = user.last_activity_time
        if ut:
            ut = Utils.datetime_from_unix_time(ut).astimezone()
            if ((nt - ut).total_seconds() > 60 * 60 * 24 * days) or user.name == 'DELETED USER':
                disable_user = True
        else:
            disable_user = True
        return disable_user

    @classmethod
    def update_or_create_by_tt_user(cls, user, user_id=None):
        # type: (User or None, int) -> (TtbUser, bool)
        defaults = {'updated': now()}
        if user:
            user_id = user.user_id
            defaults['name'] = user.name or '-'
            if user.username is not None:
                defaults['username'] = user.username
            if hasattr(user, 'avatar_url') and user.avatar_url is not None:
                defaults['avatar_url'] = user.avatar_url,
            if hasattr(user, 'full_avatar_url') and user.full_avatar_url is not None:
                defaults['full_avatar_url'] = user.full_avatar_url
            defaults['is_bot'] = user.is_bot

            disable_user = user.disable if hasattr(user, 'disable') else False
            if not disable_user:
                disable_user = cls.need_disable_user_by_last_activity_days(user)

            if disable_user:
                defaults['enabled'] = False
            else:
                defaults['enabled'] = True

        if user_id is not None:
            return cls.objects.update_or_create(user_id=user_id, defaults=defaults)
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
    Наличие строки означает что subscriber доступен для пользователя user
    enabled в строке управляет подключенностью subscriber - по умолчанию отключено
    """
    enabled = models.BooleanField(default=False, verbose_name='enabled')
    user = models.ForeignKey(TtbUser, unique=False, on_delete=models.CASCADE, verbose_name='user')
    subscriber = models.ForeignKey(TtbDjSubscriber, unique=False, on_delete=models.CASCADE, verbose_name='subscriber')
    chat = models.TextField(unique=False, null=False, verbose_name='chat')
    permissions = models.TextField(unique=False, null=False, verbose_name='permissions')

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
