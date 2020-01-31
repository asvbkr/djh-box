# -*- coding: UTF-8 -*-
from django.utils.timezone import now

from TamTamBot import UpdateCmn
from TamTamBot.TamTamBot import TamTamBot
from djh_app.models import TtbUser, TtbPrevStep
from openapi_client import Update


class TamTamBotDj(TamTamBot):

    @property
    def description(self):
        # type: () -> str
        raise NotImplementedError

    @property
    def token(self):
        # type: () -> str
        raise NotImplementedError

    def db_prepare(self):
        pass

    def get_user_language_by_update(self, update):
        # type: (Update) -> str
        update = UpdateCmn(update)
        language = update.user_locale or self.get_default_language()
        if language[:2] not in self.languages_dict.keys():
            language = self.get_default_language()
        if update:
            ttb_user, created = TtbUser.update_or_create_by_update(update)
            if isinstance(ttb_user, TtbUser):
                language = ttb_user.language or language
        return language

    def set_user_language_by_update(self, update, language, soft_setting=False):
        # type: (Update, str, bool) -> None
        update = UpdateCmn(update)
        language = language or self.get_default_language()
        if language[:2] not in self.languages_dict.keys():
            language = self.get_default_language()
        if update:
            ttb_user, created = TtbUser.update_or_create_by_update(update)
            if isinstance(ttb_user, TtbUser):
                if ttb_user.language:
                    if not soft_setting:
                        ttb_user.language = language
                else:
                    ttb_user.language = language
                ttb_user.save()

    def prev_step_write(self, index, update):
        # type: (str, Update) -> None
        if not self.prev_step_exists(index):
            b_obj = self.serialize_update(update)
            ttb_user, created = TtbUser.update_or_create_by_update(UpdateCmn(update))
            if isinstance(ttb_user, TtbUser):
                TtbPrevStep.objects.update_or_create(user=ttb_user, index=index, defaults={'update': b_obj, 'updated': now()})

    def prev_step_exists(self, index):
        # type: (str) -> bool
        return TtbPrevStep.objects.filter(index=index).exists()

    def prev_step_delete(self, index):
        # type: (str) -> None
        if self.prev_step_exists(index):
            for prev_step in TtbPrevStep.objects.filter(index=index):
                prev_step.delete()

    def prev_step_all(self):
        # type: () -> {}
        return TtbPrevStep.objects.all()

    def prev_step_get(self, index):
        # type: (str) -> Update
        prev_steps = TtbPrevStep.objects.filter(index=index)
        if prev_steps.exists() and isinstance(prev_steps[0], TtbPrevStep):
            update = self.deserialize_update(prev_steps[0].update)
            TtbUser.update_or_create_by_update(UpdateCmn(update))
            return update
