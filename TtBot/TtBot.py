# -*- coding: UTF-8 -*-
import os

from TamTamBotDj.TamTamBotDj import TamTamBotDj


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
