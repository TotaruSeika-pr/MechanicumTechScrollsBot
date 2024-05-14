from py.Bot.Bot import Bot
from py.DBManager.DBManager import DBManager

import sys
import os
from colorama import Fore, Back, Style

class StartBot:

    def __init__(self): # инициирую все приколы
        self.InsertingPaths()
        self.StartingDBManager()

    def InsertingPaths(self): # засовываю папки в path для удобной работы
        sys.path.insert(0, os.path.abspath('py'))
        sys.path.insert(1, os.path.abspath('py/Bot'))

        print(Fore.GREEN + 'sys.path.insert has been executed!')

    def StartingDBManager(self): # запускаю менеджера баз данных
        self.dbm = DBManager()

    def StartingBot(self): # запуск бота
        print(Fore.GREEN + 'Bot is running!')
        self.bot = Bot(self.dbm)

    def StoppingBot(self):
        self.bot.StopThread()