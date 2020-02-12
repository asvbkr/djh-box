# -*- coding: UTF-8 -*-
import os

from TamTamBotDj.TamTamBotDj import TamTamBotDj
from openapi_client import BotCommand


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
        ]
        if len(self.languages_dict) > 1:
            commands.append(BotCommand('set_language', 'изменить язык | set language'))
        return commands
