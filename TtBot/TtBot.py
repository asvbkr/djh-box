# -*- coding: UTF-8 -*-
import os

from TamTamBot import CallbackButtonCmd, UpdateCmn, ChatExt
from TamTamBot.utils.lng import get_text as _
from TamTamBotDj.TamTamBotDj import TamTamBotDj
from openapi_client import BotCommand, Intent, ChatType


class TtBot(TamTamBotDj):

    @property
    def token(self):
        # type: () -> str
        return os.environ.get('TT_BOT_API_TOKEN')

    @property
    def description(self):
        # type: () -> str
        return 'Этот и не бот, в общем-то, а заготовка для него.\n\n' \
               'This is not a bot, in general, but a blank for him.'

    def get_commands(self):
        # type: () -> [BotCommand]
        self.lgz.warning('The default command list is used. Maybe is error?')
        commands = [
            BotCommand('start', 'начать (о боте) | start (about bot)'),
            BotCommand('menu', 'показать меню | display menu'),
            BotCommand('list_all_chats', 'список всех чатов | list all chats'),
            BotCommand('subscriptions_mng', 'управление подписками | managing subscriptions'),
            BotCommand('view_chats_available', 'доступные чаты | available chats'),
            BotCommand('view_chats_attached', 'подключенные чаты | attached chats'),

        ]
        if len(self.languages_dict) > 1:
            commands.append(BotCommand('set_language', 'изменить язык | set language'))
        return commands

    @property
    def main_menu_buttons(self):
        # type: () -> []
        self.lgz.warning('The default main menu buttons is used. Maybe is error?')
        buttons = [
            [CallbackButtonCmd(_('About bot'), 'start', intent=Intent.POSITIVE, bot_username=self.username)],
            [CallbackButtonCmd(_('All chat bots'), 'list_all_chats', intent=Intent.POSITIVE, bot_username=self.username)],
            [CallbackButtonCmd('Доступные чаты | Available chats', 'view_chats_available', intent=Intent.POSITIVE, bot_username=self.username)],
            [CallbackButtonCmd('Подключенные чаты | Attached chats', 'view_chats_attached', intent=Intent.POSITIVE, bot_username=self.username)],
        ]
        if len(self.languages_dict) > 1:
            buttons.append([CallbackButtonCmd('Изменить язык / set language', 'set_language', intent=Intent.DEFAULT, bot_username=self.username)])

        return buttons

    def cmd_handler_view_chats_available(self, update):
        return self.view_buttons_for_chats_available_direct('Выберите/Select:', 'view_selected_chat_info', update.user_id, {'type': 'доступный/available'}, update.link)

    def cmd_handler_view_chats_attached(self, update):
        return self.view_buttons_for_chats_attached('Выберите/Select:', 'view_selected_chat_info', update.user_id, {'type': 'подключенный/attached'}, update.link)

    def cmd_handler_view_selected_chat_info(self, update):
        # type: (UpdateCmn) -> bool
        if not (update.chat_type in [ChatType.DIALOG]):
            return False

        if not (update.chat_id or update.user_id):
            return False

        if not update.this_cmd_response:  # Обрабатываем только саму команду
            if update.cmd_args:
                chat_id = update.cmd_args.get('chat_id')
                if chat_id is None:
                    parts = update.cmd_args.get('c_parts') or []
                    if parts and parts[0]:
                        chat_id = parts[0][0]
                if chat_id:
                    chat_ext = ChatExt(self.chats.get_chat(chat_id), self.title)
                    chat_type = update.cmd_args.get('type')
                    self.send_notification(
                        update,
                        f'chat_type: {chat_type}; chat_id={chat_id}; подключен/attached? {self.chat_is_attached(chat_ext.chat_id, update.user_id)}; {chat_ext.chat_name_ext}'
                    )
        return True
