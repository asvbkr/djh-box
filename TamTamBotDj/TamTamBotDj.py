# -*- coding: UTF-8 -*-
import json
from datetime import timedelta

from django.utils.timezone import now

from TamTamBot import UpdateCmn, ChatExt, CallbackButtonCmd
from TamTamBot.TamTamBot import TamTamBot
from ttgb_cmn.lng import get_text as _
from djh_app.models import TtbUser, TtbPrevStep, TtbDjSubscriber, TtbDjChatAvailable, TtbDjLimitedButtons
from openapi_client import Update, User, Chat, SimpleQueryResult, Intent, Button, ChatType, NewMessageBody, NewMessageLink, SendMessageResult, BotStartedUpdate, BotAddedToChatUpdate, \
    BotRemovedFromChatUpdate, MessageCreatedUpdate, MessageCallbackUpdate, UserAddedToChatUpdate, UserRemovedFromChatUpdate, ChatTitleChangedUpdate, MessageChatCreatedUpdate, ChatMember
from openapi_client.rest import ApiException


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
        update = UpdateCmn(update, self)
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
        update = UpdateCmn(update, self)
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
            ttb_user, created = TtbUser.update_or_create_by_update(UpdateCmn(update, self))
            if isinstance(ttb_user, TtbUser):
                TtbPrevStep.objects.update_or_create(index=index, defaults={'user': ttb_user, 'update': b_obj, 'updated': now()})

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
            TtbUser.update_or_create_by_update(UpdateCmn(update, self))
            return update

    @staticmethod
    def limited_buttons_get(index):
        # type: (str) -> [[]]
        qs_buttons = TtbDjLimitedButtons.objects.filter(index=index)
        if qs_buttons:
            buttons_str = qs_buttons.first().buttons
            buttons = json.loads(buttons_str)
            return buttons

    def limited_buttons_set(self, index, buttons):
        # type: (str, [[]]) -> None
        b_obj = self.serialize_open_api_object(buttons)
        TtbDjLimitedButtons.objects.update_or_create(index=index, defaults={'buttons': b_obj, 'updated': now()})

    @staticmethod
    def limited_buttons_del(index):
        # type: (str) -> None
        TtbDjLimitedButtons.objects.filter(index=index).delete()

    def change_subscriber(self, update, enabled, chat_ext=None, api_user=None, recreate_cache=True):
        # type: (UpdateCmn or None, bool or None, ChatExt, User, bool) -> TtbDjSubscriber
        subscriber = None
        defaults = {
            'updated': now()
        }
        if enabled is not None:
            defaults['enabled'] = enabled
        if update:
            if not api_user:
                api_user = update.user
                if api_user and not hasattr(api_user, 'disable'):
                    api_user.disable = True
            try:
                chat_ext = chat_ext or ChatExt(self.chats.get_chat(update.chat_id), self.get_dialog_name(self.title, user=api_user))
            except ApiException:
                chat_ext = None

        if chat_ext:
            defaults['chat_name'] = chat_ext.chat_name
            defaults['chat_type'] = chat_ext.chat.type
            defaults['participants_count'] = chat_ext.chat.participants_count
            subscriber, created = TtbDjSubscriber.objects.update_or_create(chat_id=chat_ext.chat_id, defaults=defaults)

        db_user = None
        if api_user:
            if api_user.is_bot:
                api_user.disable = True
            db_user, created = TtbUser.update_or_create_by_tt_user(api_user)
            api_user.disable = not db_user.enabled
            if db_user:
                if subscriber:
                    db_user.subscriber.add(subscriber)
                else:
                    subscriber, created = TtbDjSubscriber.objects.update_or_create(chat_id=update.chat_id, defaults=defaults)
                    db_user.subscriber.remove(subscriber)

        if isinstance(subscriber, TtbDjSubscriber) and chat_ext:
            if subscriber.language is None:
                if chat_ext.lang:
                    subscriber.language = chat_ext.lang
                    subscriber.save()
                elif isinstance(db_user, TtbUser) and db_user.language:
                    subscriber.language = db_user.language
                    subscriber.save()

        if api_user:
            if recreate_cache and api_user.user_id:
                self.recreate_cache(api_user.user_id)

        return subscriber

    def process_command(self, update):
        # type: (Update) -> bool
        uc = UpdateCmn(update, self)
        uc.user.disable = False
        self.change_subscriber(uc, True, recreate_cache=False)
        return super(TamTamBotDj, self).process_command(update)

    def handle_message_created_update(self, update):
        # type: (MessageCreatedUpdate) -> bool
        self.change_subscriber(UpdateCmn(update, self), True, recreate_cache=False)
        return super(TamTamBotDj, self).handle_message_created_update(update)

    def handle_message_callback_update(self, update):
        # type: (MessageCallbackUpdate) -> bool
        self.change_subscriber(UpdateCmn(update, self), True, recreate_cache=False)
        return super(TamTamBotDj, self).handle_message_callback_update(update)

    def handle_bot_started_update(self, update):
        # type: (BotStartedUpdate) -> bool
        return super(TamTamBotDj, self).handle_bot_started_update(update) and self.change_subscriber(UpdateCmn(update, self), False)

    def handle_bot_added_to_chat_update(self, update):
        # type: (BotAddedToChatUpdate) -> bool
        update = UpdateCmn(update, self)
        chat = self.chats.get_chat(update.chat_id)
        if isinstance(chat, Chat):
            admins_chats = self.admins_contacts.get('chats') or []
            if update.chat_id not in admins_chats:
                chat_ext = self.chat_is_available(chat, update.user.user_id)
                if chat_ext and self.chat_is_allowed_for_add(chat_ext, update.user.user_id):
                    return bool(self.change_subscriber(update, True))
                res = self.chats.leave_chat(update.chat_id)
                if isinstance(res, SimpleQueryResult) and not res.success and isinstance(update.user, User):
                    self.send_admin_message(
                        f'Error leaving chat {chat.chat_id} ({chat.title}/{chat.link}): {res.message}\nTry adding user {update.user.user_id} - {update.user.name}(@{update.user.username})'
                    )
                elif isinstance(res, SimpleQueryResult) and res.success and isinstance(update.user, User):
                    if not chat_ext:
                        chat_ext = ChatExt(chat, self.title)
                    try:
                        # noinspection PyTypeChecker
                        self.send_message(
                            NewMessageBody(
                                _('The bot %(bot_name)s cannot be added to %(chat_name)s, because it cannot work correctly under the current environment (rights, chat type, etc.).') % {
                                    'bot_name': f'<{self.name} (@{self.username})>',
                                    'chat_name': chat_ext.chat_name_ext, }
                            ), user_id=update.user.user_id)
                    except (ApiException, ValueError):
                        pass
        return False

    def handle_bot_removed_from_chat_update(self, update):
        # type: (BotRemovedFromChatUpdate) -> bool
        return bool(self.change_subscriber(UpdateCmn(update, self), False))

    def handle_user_added_to_chat_update(self, update):
        # type: (UserAddedToChatUpdate) -> bool
        self.change_subscriber(UpdateCmn(update, self), True, recreate_cache=False)
        return super(TamTamBotDj, self).handle_user_added_to_chat_update(update)

    def handle_user_removed_from_chat_update(self, update):
        # type: (UserRemovedFromChatUpdate) -> bool
        self.change_subscriber(UpdateCmn(update, self), True, recreate_cache=False)
        return super(TamTamBotDj, self).handle_user_removed_from_chat_update(update)

    def handle_chat_title_changed_update(self, update):
        # type: (ChatTitleChangedUpdate) -> bool
        self.change_subscriber(UpdateCmn(update, self), True, recreate_cache=False)
        return super(TamTamBotDj, self).handle_chat_title_changed_update(update)

    def handle_message_chat_created_update(self, update):
        # type: (MessageChatCreatedUpdate) -> bool
        self.change_subscriber(UpdateCmn(update, self), True, recreate_cache=False)
        return super(TamTamBotDj, self).handle_message_chat_created_update(update)

    # Определяет разрешённость чата для добавления бота
    def chat_is_allowed_for_add(self, chat_ext, user_id=None):
        # type: (ChatExt, int) -> bool
        return self.chat_is_allowed(chat_ext, user_id)

    @staticmethod
    def switch_chat_available(enabled, chat_id, user_id=None):
        # type: (bool, int, int) -> None
        # , 'enabled': True
        if user_id:
            qs = TtbDjChatAvailable.objects.filter(subscriber__chat_id=chat_id, user__user_id=user_id)
        else:
            qs = TtbDjChatAvailable.objects.filter(subscriber__chat_id=chat_id)
        qs.update(enabled=enabled, updated=now())

    def change_chat_available(self, chat_ext, db_user, api_user=None):
        # type: (ChatExt, TtbUser, User) -> None
        try:
            api_user = api_user or self.get_chat_admins(chat_ext.chat_id).get(db_user.user_id) if chat_ext.chat.type != ChatType.DIALOG else self.chats.get_chat(chat_ext.chat_id).dialog_with_user
        except ApiException:
            api_user = User(
                user_id=db_user.user_id, name=db_user.name or '-', username=db_user.username, is_bot=bool(db_user.is_bot), last_activity_time=0,
            )
            api_user.disable = True

        subscriber = self.change_subscriber(None, True, chat_ext, api_user, recreate_cache=False)

        if api_user.disable:
            TtbDjChatAvailable.objects.filter(user=db_user, subscriber=subscriber, ).delete()
            return
        TtbDjChatAvailable.objects.update_or_create(
            user=db_user, subscriber=subscriber,
            defaults={'chat': self.serialize_open_api_object(chat_ext.chat), 'permissions': json.dumps(chat_ext.admin_permissions), 'updated': now()}
        )

    def recreate_cache(self, user_id=None):
        # type: (int) -> timedelta or str
        tb = now()

        all_bot_relation = self.get_all_chats_with_bot_admin(True)
        all_chats_members = all_bot_relation['ChatsMembers']
        all_members = all_bot_relation['Members']
        all_chats = all_bot_relation['Chats']

        proc_user_list = list(all_members.keys())
        proc_chat_list = list(all_chats.keys())

        if user_id:
            if user_id not in proc_user_list:
                return _('Current user (%s) not found.') % user_id
            api_user = all_members[user_id]
            TtbUser.update_or_create_by_tt_user(api_user)
            qs_db_user = TtbUser.objects.filter(user_id=user_id)
        else:
            # Синхронизация пользователей
            proc_user_list = []
            c_u = 0
            for api_user in all_members.values():
                if isinstance(api_user, ChatMember):
                    pass
                c_u += 1
                if api_user.is_bot:
                    api_user.disable = True
                db_user, created = TtbUser.update_or_create_by_tt_user(api_user)
                u_i = f'{"bot " if api_user.is_bot else ""}name={api_user.name}; user_id={api_user.user_id}; enabled={db_user.enabled}'
                if api_user.username:
                    u_i += f'; username={api_user.username}'
                # if api_user.description:
                #     u_i += f' ({api_user.description[:50]})'
                self.lgz.debug(f'User synchronization +++++++++++++++> ({c_u} of {len(all_members)}) - {u_i}')
                proc_user_list.append(api_user.user_id)

            duc = TtbUser.objects.filter(enabled=True).exclude(user_id__in=proc_user_list).update(enabled=False, updated=now())
            self.lgz.debug(f'Other users disabled: {duc}')

            qs_db_user = TtbUser.objects.filter(enabled=True)

        cnt_u = len(qs_db_user)

        c_u = 0
        for db_user in qs_db_user:
            c_u += 1
            self.lgz.debug(f'+++++++++++++++> ({c_u} of {len(qs_db_user)}) - {db_user}')
            chat_ext_dict = all_chats_members.get(db_user.user_id)
            api_user = all_members.get(db_user.user_id)
            if chat_ext_dict and api_user:
                cnt_c = len(chat_ext_dict)
                c_c = 0
                for chat_ext in chat_ext_dict.values():
                    c_c += 1
                    self.lgz.debug('Executing %.4f%% (user %d of %d) -> %.4f%% (chat %d of %d)' % (c_u / cnt_u * 100, c_u, cnt_u, c_c / cnt_c * 100, c_c, cnt_c))
                    self.change_chat_available(chat_ext, db_user, api_user)
                    if not self.chat_is_allowed(chat_ext, db_user.user_id) and chat_ext.chat_id in proc_chat_list:
                        proc_chat_list.remove(chat_ext.chat_id)
            elif not chat_ext_dict:
                self.lgz.debug(f"do not available chats for user_id={db_user.user_id}")
                TtbDjChatAvailable.objects.filter(user=db_user).delete()
                TtbUser.objects.filter(enabled=True, user_id=db_user.user_id).update(enabled=False, updated=now())

        # Удаление строк кэша по неактивным подписчикам и пользователям
        if user_id:
            TtbDjChatAvailable.objects.filter(user__user_id=user_id).exclude(subscriber__chat_id__in=proc_chat_list).delete()
            TtbDjChatAvailable.objects.filter(user__user_id=user_id, subscriber__enabled=False).delete()
        else:
            dcc = TtbDjSubscriber.objects.filter(enabled=True).exclude(chat_id__in=proc_chat_list).update(enabled=False, updated=now())
            self.lgz.debug(f'Other chats disabled: {dcc}')

            TtbDjChatAvailable.objects.filter(subscriber__enabled=False).delete()
            TtbDjChatAvailable.objects.filter(user__enabled=False).delete()

        e_t = now() - tb
        self.lgz.debug(f'100% executed in {e_t}')
        return e_t

    def get_users_chats_with_bot(self, user_id):
        # type: (int) -> dict
        chats_available = {}
        user, created = TtbUser.update_or_create_by_tt_user(None, user_id)
        if user:
            if not TtbDjChatAvailable.objects.filter(user=user, subscriber__enabled=True).exists():
                self.recreate_cache(user_id)
            for chat_available in TtbDjChatAvailable.objects.filter(user=user, subscriber__enabled=True):
                if isinstance(chat_available, TtbDjChatAvailable):
                    chat = self.deserialize_open_api_object(bytes(chat_available.chat, encoding='utf-8'), 'Chat')
                    if isinstance(chat, Chat):
                        chat_ext = ChatExt(chat, self.get_dialog_name(self.title, chat=chat, user_id=user.user_id), json.loads(chat_available.permissions))
                        chats_available[chat.chat_id] = chat_ext
                        self.lgz.debug('chat => chat_id=%(id)s added into list available chats from cache' % {'id': chat.chat_id})
        else:
            self.lgz.debug(f"it can't be, but it happened... user_id={user_id}")
        return chats_available

    # chats_available - доступные чаты — доступные для бота в разрезе пользователя.
    # chats_attached - подключенные чаты — подмножество доступных чатов, по которым оформлена "подписка" в разрезе пользователя.
    # что из этого использовать - решает разработчик исходя из решаемой задачи.
    # В принципе, возможно и одновременное использование обоих словарей
    def get_chats_available(self, user_id):
        return self.get_users_chats_with_bot(user_id)

    def get_chats_attached(self, user_id):
        chats_dict = self.get_users_chats_with_bot(user_id)
        res_dict = {}
        for chat in chats_dict.values():
            found_subscription = self.chat_is_attached(chat.chat_id)
            if found_subscription:
                res_dict[chat.chat_id] = chat
        return res_dict

    # Определяет является ли чат подключенным — т.е. "подписчиком" бота в разрезе пользователя
    @staticmethod
    def chat_is_attached(chat_id, user_id=None):
        # type: (int, int or None) -> bool
        if user_id is not None:
            found_subscription = TtbDjChatAvailable.objects.filter(subscriber__chat_id=chat_id, user__user_id=user_id, enabled=True).exists()
        else:
            found_subscription = TtbDjChatAvailable.objects.filter(subscriber__chat_id=chat_id, enabled=True).exists()
        return found_subscription

    # Определяет является ли чат доступным для подключения — т.е. для "подписки" в разрезе пользователя
    def chat_is_attachable(self, chat_id, user_id):
        # type: (int, int) -> bool
        chats = self.get_users_chats_with_bot(user_id)
        return chat_id in chats.keys()

    def get_buttons_for_chats_available(self, user_id, cmd, ext_args=None):
        # type: (int, str, dict) -> [[CallbackButtonCmd]]
        buttons = super(TamTamBotDj, self).get_buttons_for_chats_available(user_id, cmd, ext_args)
        if buttons:
            for i in range(len(buttons)):
                if isinstance(buttons[i][0], CallbackButtonCmd):
                    chat_id = buttons[i][0].cmd_args['chat_id']
                    found_subscription = self.chat_is_attached(chat_id)
                    buttons[i][0].intent = Intent.POSITIVE if found_subscription else Intent.DEFAULT
                    buttons[i][0].text = ((' ☑️ ' if found_subscription else ' 🔲 ') + buttons[i][0].text)[:Button.MAX_TEXT_LENGTH]

        return buttons

    def get_buttons_for_chats_available_direct(self, user_id, cmd, ext_args):
        # type: (int, str, dict) -> [[CallbackButtonCmd]]
        return super(TamTamBotDj, self).get_buttons_for_chats_available(user_id, cmd, ext_args)

    def get_buttons_for_chats_attached(self, user_id, cmd, ext_args):
        # type: (int, str, dict) -> [[CallbackButtonCmd]]
        ext_args = ext_args or {}

        buttons = []
        chats_dict = self.get_chats_attached(user_id)
        i = 0
        for chat in sorted(chats_dict.values()):
            i += 1
            args = {'chat_id': chat.chat_id}
            args.update(ext_args)
            buttons.append([CallbackButtonCmd('%d. %s' % (i, chat.chat_name), cmd, args, Intent.POSITIVE, bot_username=self.username)])
        return buttons

    def view_buttons_for_chats_available(self, title, cmd, user_id, chat_id, link=None, update=None):
        # type: (str, str, int, int, NewMessageLink, Update) -> SendMessageResult
        return self.view_buttons(title, self.get_buttons_for_chats_available(user_id, cmd), user_id, chat_id, link=link, update=update, add_close_button=True)

    def view_buttons_for_chats_available_direct(self, title, cmd, user_id, chat_id, ext_args, link=None, update=None, add_close_button=False):
        # type: (str, str, int, int, dict, NewMessageLink, Update, bool) -> SendMessageResult
        return self.view_buttons(title, self.get_buttons_for_chats_available_direct(user_id, cmd, ext_args), user_id, chat_id, link=link, update=update, add_close_button=add_close_button)

    def view_buttons_for_chats_attached(self, title, cmd, user_id, chat_id, ext_args, link=None, update=None, add_close_button=False):
        # type: (str, str, int, int, dict, NewMessageLink, Update, bool) -> SendMessageResult
        return self.view_buttons(title, self.get_buttons_for_chats_attached(user_id, cmd, ext_args), user_id, chat_id, link=link, update=update, add_close_button=add_close_button)

    # Вызов перестроения кеша
    def cmd_recreate_cache(self, update, user_id=None, dialog_only=True):
        # type: (UpdateCmn, int, bool) -> bool
        if dialog_only and not (update.chat_type in [ChatType.DIALOG]):
            return False
        if not update.chat_id:
            return False
        te = self.recreate_cache(user_id)
        if isinstance(te, timedelta):
            msg_text = '@%s: ' % self.username + _('Cache recreated.') + ' (%s)' % te
        else:
            msg_text = ' (%s)' % te if te else ''
            msg_text = '@%s: ' % _('Error recreate cache.%s') % msg_text
        return bool(
            self.msg.send_message(NewMessageBody(msg_text, link=update.link), chat_id=update.chat_id)
        )

    # Обработка команды перестроения кеша
    def cmd_handler_cache(self, update):
        # type: (UpdateCmn) -> bool
        return self.cmd_recreate_cache(update, update.user_id)

    # Обработка команды полного перестроения кеша
    def cmd_handler_cache_all(self, update):
        # type: (UpdateCmn) -> bool
        return self.cmd_recreate_cache(update)

    def cmd_handler_subscriptions_mng(self, update):
        # type: (UpdateCmn) -> bool
        if not (update.chat_type in [ChatType.DIALOG]):
            return False

        if not (update.chat_id or update.user_id):
            return False

        if not update.this_cmd_response:  # Обработка самой команды
            if not update.cmd_args:
                return bool(
                    self.view_buttons_for_chats_available(_('Select chat to attach/detach your subscription:'), 'subscriptions_mng', update.user_id, update.chat_id, link=update.link,
                                                          update=update.update_current)
                )
            else:
                is_close = update.cmd_args.get('is_close')
                if is_close:
                    return True
                chat_id = update.cmd_args.get('chat_id')
                if chat_id is None:
                    parts = update.cmd_args.get('c_parts') or []
                    if parts and parts[0]:
                        chat_id = parts[0][0]
                if chat_id:
                    update.chat_id = chat_id
                    self.switch_chat_available(False if self.chat_is_attached(chat_id) else True, chat_id)

                update.cmd_args = None
                return self.cmd_handler_subscriptions_mng(update)
        else:  # Обработка текстового ответа
            self.send_message(NewMessageBody(_('Text response is not provided'), link=update.link))
