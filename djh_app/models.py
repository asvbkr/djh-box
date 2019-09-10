from django.db import models
from django.utils.timezone import now

from TamTamBot import UpdateCmn
from openapi_client import User


def ext__str__(self):
    s = ''
    for field in self._meta.fields:
        s += '%s%s: %s' % (', ' if s else '', field.verbose_name, getattr(self, field.name))
    s = '<%s: |%s|>' % (self._meta.verbose_name, s)
    return s


# Create your models here.
class InputMessage(models.Model):
    when = models.DateTimeField("date created", auto_now_add=True)
    who = models.TextField("who created")
    request_body = models.TextField('request body', null=True)


class TtbUser(models.Model):
    enabled = models.BooleanField(default=True, verbose_name='enabled')
    user_id = models.BigIntegerField(unique=True, verbose_name='user id')
    name = models.TextField(unique=False, null=True, verbose_name='name')
    username = models.TextField(unique=False, null=True, verbose_name='user name')
    language = models.CharField(max_length=10, unique=False, null=True, verbose_name='language')
    avatar_url = models.TextField(unique=False, null=True, verbose_name='avatar url')
    full_avatar_url = models.TextField(unique=False, null=True, verbose_name='full avatar url')

    updated = models.DateTimeField(auto_now_add=True, verbose_name='updated')

    def __str__(self):
        # noinspection PyTypeChecker
        return ext__str__(self)

    @classmethod
    def update_or_create_by_tt_user(cls, u, user_id=None):
        # type: (User, int) -> (TtbUser, bool)
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
        if user_id is not None:
            return cls.objects.update_or_create(user_id=user_id, defaults=dff)
        else:
            return None, False

    @classmethod
    def update_or_create_by_update(cls, update):
        # type: (UpdateCmn) -> (TtbUser, bool)
        return cls.update_or_create_by_tt_user(update.user, update.user_id)


class TtbPrevStep(models.Model):
    index = models.CharField(max_length=64, unique=True, null=False, verbose_name='index')
    update = models.TextField(unique=False, null=False, verbose_name='user update')
    user = models.ForeignKey(TtbUser, unique=False, on_delete=models.CASCADE, verbose_name='user')
    updated = models.DateTimeField(auto_now_add=True, null=True, verbose_name='updated')
