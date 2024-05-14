from py.Bot.KeyboardManager import KeyBoardManager as KBM
from py.Bot.UsersRightsManager import UsersRightsManager as URM

from py.Bot.ActionsMechanicuses import Actions

import telebot
import threading

class Bot(KBM, URM):

    def __init__(self, dbm):
        self.token = self.GetToken()
        self.dbm = dbm

        self.Running()

    def GetDataForAdminAuthorizations(self, msg): # получение данных пользователя для авторизации
        if URM.AdminAuthorizations(msg, self.dbm.GetAdmin(msg.from_user.id)):
            self.bot.send_message(msg.chat.id, 'Авторизация прошла успешна.\nПрава администратора выданы.\n')
            self.dbm.ActivatingAdministratorMode(msg.from_user.id)
            self.ReloadKeyboard(msg)
        else:
            self.bot.send_message(msg.chat.id, 'Данные введены неверно.')

        self.bot.delete_message(msg.chat.id, msg.message_id)

    def GetDataForEditDataAdmin(self, msg):
        data = msg.text.split()
        try:
            data[0]
            data[1]
        except IndexError:
            self.bot.send_message(msg.chat.id, 'Неверные данные!')
        else:
            self.dbm.EditDataAAdmin(data, msg.from_user.id)
            self.bot.send_message(msg.chat.id, 'Данные изменены')
        
        self.bot.delete_message(msg.chat.id, msg.message_id)

    def SendMessageAllAdmins(self, text, keyboard):
        admins = self.dbm.GetAllAdmins()

        for i in admins:
            if keyboard != None:
                self.bot.send_message(i[1], text, reply_markup=keyboard())
            else:
                self.bot.send_message(i[1], text)
    
    def SendMessageAllMechanicum(self, text, from_id):
        print(self.dbm.GetMechanicumForAdminSending())
        for i in self.dbm.GetMechanicumForAdminSending():
            if from_id != i[0]:
                self.bot.send_message(i[0], f'Рассылка от администрации:\n{text}')

    def UserNotHaveRightsMessage(self, chat_id):
        self.bot.send_message(chat_id, 'Вы не имеете прав на использование этого действия')

    def StopThread(self):
        self.caa.running = False

    def ReloadKeyboard(self, message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum):
                start_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                start_keyboard = URM.CreateStartKeyboard(data_mechanicum, data_admin, start_keyboard)

                self.bot.send_message(message.chat.id, f'Клавиатура была перезагружена.', reply_markup=start_keyboard)
            else:
                self.bot.send_message(message.chat.id, f'Запись с идентификатором {message.from_user.id} не найдена.\nДоступ к знаниям механикус отклонен. Обратитесь к администратору для получения дополнительной информации.')

    def GetToken(self): # получение токена из файла
        with open('Content/token.txt', 'r') as f:
            return str(f.read())

    def ShowingInstructions(self, callback_data):
        data_instructions = self.dbm.GetInstruction(int(callback_data.data.split()[1]))
        data_mechanicum = self.dbm.GetMechanicum(data_instructions[1])
        keyboard = KBM.GetKeyboardInstruction(data_instructions[0])
        self.bot.send_photo(callback_data.from_user.id, 
                            open(f'Content/photos/{data_instructions[7]}', 'rb'), 
                            f'{data_instructions[3]} - **{data_instructions[4]}**\n\n{data_instructions[5]}\n\n[Свиток]({data_instructions[6]})\nСоздатель: [{data_mechanicum[10][:-1]}] {data_mechanicum[2]} {data_mechanicum[11]}',
                            reply_markup=keyboard(),
                            parse_mode='Markdown')
        
    def Running(self): # главный обработчик бота
        self.bot = telebot.TeleBot(self.token)

        @self.bot.callback_query_handler(func=lambda call: 'edit_id' in call.data)
        def CallbackQuery(call):
            Actions.EditingModeActions.EditInstructions(call.from_user.id, self.bot, self.dbm, call.data.split()[1])

        @self.bot.callback_query_handler(func=lambda call: 'set_comment' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.SetComment(call.from_user.id, self.bot, self.dbm, call.data.split()[1])

        @self.bot.callback_query_handler(func=lambda call: 'get_comment' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.GetComment(call.from_user.id, self.bot, self.dbm, call.data.split()[1])
        
        @self.bot.callback_query_handler(func=lambda call: 'id_instruction' in call.data)
        def CallbackQuery(call):
            self.ShowingInstructions(call)

        @self.bot.callback_query_handler(func=lambda call: 'section' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.ShowAllInstructionsSections(call.from_user.id, self.bot, self.dbm, call.data.split()[1])

        @self.bot.callback_query_handler(func=lambda call: 'prefix_market' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.OpenItemsMarket(call.from_user.id, self.bot, self.dbm, 'prefix')

        @self.bot.callback_query_handler(func=lambda call: 'prefix_storage' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.OpenItemStorage(call.from_user.id, self.bot, self.dbm, call, 'prefix')

        @self.bot.callback_query_handler(func=lambda call: 'set_prefix' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.SetItem(call.from_user.id, self.bot, self.dbm, call, 'prefix')

        @self.bot.callback_query_handler(func=lambda call: 'prefix_buy' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.BuyItem(call.from_user.id, self.bot, self.dbm, call.data.split()[1], 'prefix')

        @self.bot.callback_query_handler(func=lambda call: 'cap_market' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.OpenItemsMarket(call.from_user.id, self.bot, self.dbm, 'cap')

        @self.bot.callback_query_handler(func=lambda call: 'cap_buy' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.BuyItem(call.from_user.id, self.bot, self.dbm, call.data.split()[1], 'cap')

        @self.bot.callback_query_handler(func=lambda call: 'cap_storage' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.OpenItemStorage(call.from_user.id, self.bot, self.dbm, call, 'cap')

        @self.bot.callback_query_handler(func=lambda call: 'set_cap' in call.data)
        def CallbackQuery(call):
            Actions.BasicActions.SetItem(call.from_user.id, self.bot, self.dbm, call, 'cap')

        @self.bot.callback_query_handler(func=lambda call: 'personal_sending' in call.data)
        def PrsonalSendingEdit(call):
            Actions.BasicActions.PrsonalSendingEdit(call.from_user.id, self.bot, self.dbm)

        @self.bot.callback_query_handler(func=lambda call: 'admin_sending' in call.data)
        def AdminSendingEdit(call):
            Actions.BasicActions.AdminSendingEdit(call.from_user.id, self.bot, self.dbm)        

        @self.bot.callback_query_handler(func=lambda call: 'idea_accept' in call.data)
        def CallbackQuery(call):
            Actions.AdministrationModeAtions.IdeaAccept(call.from_user.id, self.bot, self.dbm, call.data.split()[1])

        @self.bot.callback_query_handler(func=lambda call: 'idea_reject' in call.data)
        def CallbackQuery(call):
            Actions.AdministrationModeAtions.IdeaReject(call.from_user.id, self.bot, self.dbm, call.data.split()[1])

        @self.bot.callback_query_handler(func=lambda call: 'show_idea' in call.data)
        def CallbackQuery(call):
            data_mechanicum = self.dbm.GetMechanicum(call.from_user.id)
            Actions.AdministrationModeAtions.ShowIdea(call.from_user.id, self.bot, self.dbm, call.data.split()[1], URM.CheckingAdminCapabilities(data_mechanicum))

        @self.bot.callback_query_handler(func=lambda call: 'vote' in call.data)
        def CallbackQuery(call):
            Actions.AdministrationModeAtions.VoteIdea(call.from_user.id, self.bot, self.dbm, call.data.split()[1])

        @self.bot.callback_query_handler(func=lambda call: 'remove_idea' in call.data)
        def CallbackQuery(call):
            data_mechanicum = self.dbm.GetMechanicum(call.from_user.id)
            if URM.CheckingAdminCapabilities(data_mechanicum):
                Actions.AdministrationModeAtions.RemoveIdea(call.from_user.id, self.bot, self.dbm, call.data.split()[1])
            else:
                self.UserNotHaveRightsMessage(call.from_user.id)

        @self.bot.callback_query_handler(func=lambda call: 'to_create' in call.data)
        def CallbackQuery(call):
            data_mechanicum = self.dbm.GetMechanicum(call.from_user.id)
            if URM.CheckingEditorCapabilities(data_mechanicum):
                Actions.AdministrationModeAtions.ToCreateIdea(call.from_user.id, self.bot, self.dbm, call.data.split()[1])
            else:
                self.UserNotHaveRightsMessage(call.from_user.id)
        
        @self.bot.callback_query_handler(func=lambda call: 'release' in call.data)
        def CallbackQuery(call):
            data_mechanicum = self.dbm.GetMechanicum(call.from_user.id)
            if URM.CheckingEditorCapabilities(data_mechanicum):
                Actions.AdministrationModeAtions.ReleaseIdea(call.from_user.id, self.bot, self.dbm, call.data.split()[1])
            else:
                self.UserNotHaveRightsMessage(call.from_user.id)

        @self.bot.message_handler(commands=['start', 'info'])
        def StartMessage(message):
            """стартовая проверка пользователя, проверка прав и выдача кнопок""" 

            self.dbm.RecordUser(message)

            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum):
                start_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                start_keyboard = URM.CreateStartKeyboard(data_mechanicum, data_admin, start_keyboard)

                self.bot.send_message(message.chat.id, f'Приветствую тебя, {data_mechanicum[2]}!', reply_markup=start_keyboard)
            else:
                self.bot.send_message(message.chat.id, f'Запись с идентификатором {message.from_user.id} не найдена.\nДоступ к знаниям механикус отклонен. Обратитесь к администратору для получения дополнительной информации.')

        
        @self.bot.message_handler(func=lambda message: message.text == '🛠️ Активировать режим администрирования')
        def ActivatingAdministratorMode(message):
            """активация режима админа: проверка на возможность администрирования и проверка пары логин-пароль"""

            if URM.CheckingPossibilityAdministration(self.dbm.GetMechanicum(message.from_user.id)):
                msg = self.bot.send_message(message.chat.id, 'Введите лоигн и пароль через пробел')
                self.bot.register_next_step_handler(msg, self.GetDataForAdminAuthorizations)
            else:
                self.bot.send_message(message.chat.id, 'Вы не имеете права использовать авторизацию как администратор!')
        
        @self.bot.message_handler(func=lambda message: message.text == 'Изменить данные для входа')
        def EditDataAdmin(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingAdminCapabilities(data_mechanicum):
                msg = self.bot.send_message(message.chat.id, 'Введите новые данные для входа')
                self.bot.register_next_step_handler(msg, self.GetDataForEditDataAdmin)
            else:
                self.bot.send_message(message.chat.id, 'Вы не имеете права использовать авторизацию как администратор!')
        
        
        @self.bot.message_handler(func=lambda message: message.text == '💡 Предложить идею')
        def SuggestIdea(message):

            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                text = Actions.BasicActions.SuggestIdea(message.chat.id, self.bot, self.dbm, self)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '👀 Посмотреть на идеи')
        def ShowAllIdeas(message):

            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                text = Actions.BasicActions.ShowAllIdeas(message.chat.id, self.bot, self.dbm, URM.CheckingAdminCapabilities(data_mechanicum))
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '📤 Создать расылку')
        def AdminSending(message):

            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                text = Actions.AdministrationModeAtions.AdminSending(message.chat.id, self.bot, self.dbm, self)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)
        
        # 📤 Создать расылку


        @self.bot.message_handler(func=lambda message: message.text == '⚙️ Настройки рассылки')
        def SendingSettings(message):

            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                text = Actions.BasicActions.SendingSettings(message.chat.id, self.bot, self.dbm, data_mechanicum)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🏪 Открыть магазин')
        def OpenMarket(message):
            
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                Actions.BasicActions.OpenMarket(message, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '📦 Открыть склад')
        def OpenStorage(message):

            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                Actions.BasicActions.OpenStorage(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🆕 Добавить префикс 🔝')
        def AddPrefix(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                Actions.AdministrationModeAtions.AddItem(message, self.bot, self.dbm, 'prefix')
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🗑 Удалить префикс 🔝')
        def RemovePrefix(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                Actions.AdministrationModeAtions.RemoveItem(message, self.bot, self.dbm, 'prefix')
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🆕 Добавить шапку 🧢')
        def AddCap(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                Actions.AdministrationModeAtions.AddItem(message, self.bot, self.dbm, 'cap')
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🗑 Удалить шапку 🧢')
        def RemoveCap(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                Actions.AdministrationModeAtions.RemoveItem(message, self.bot, self.dbm, 'cap')
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🚫 Деактивировать режим администрирования')
        def DeactivateAdministrationMode(message):
            self.dbm.DeactivateAdministrationMode(message.from_user.id)
            self.bot.send_message(message.chat.id, 'Режим администрирования был деактивирован')
            self.ReloadKeyboard(message)

        @self.bot.message_handler(func=lambda message: message.text == '📝 Создать новую инструкцию')
        def CreatingInstructions(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingEditorCapabilities(data_mechanicum):
                Actions.EditingModeActions.CreatingInstructions(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)
        
        @self.bot.message_handler(func=lambda message: message.text == '➕ Добавить механикума')
        def AddMechanicum(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                Actions.AdministrationModeAtions.AddMechanicum(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)
        
        @self.bot.message_handler(func=lambda message: message.text == '🔄 Обновить клавиатуру')
        def ReloadKeyboard(message):
            self.ReloadKeyboard(message)

        @self.bot.message_handler(func=lambda message: message.text == '📩 Сделать запрос')
        def RequestInstructions(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                Actions.BasicActions.RequestInstructions(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '📂 Открыть каталог')
        def SearchCategory(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                Actions.BasicActions.CatalogDisplay(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🔎 Поиск по категории')
        def SearchCategory(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                Actions.BasicActions.SearchCategory(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '✏️ Редактировать инструкцию')
        def EditInstructions(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingEditorCapabilities(data_mechanicum):
                Actions.EditingModeActions.GetIDEditInstructions(message, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🗑 Удалить инструкцию')
        def EditInstructions(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                Actions.EditingModeActions.RemoveInstructions(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '✏️ Редактировать механикума')
        def EditMechanicum(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                Actions.AdministrationModeAtions.EditMechanicum(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(func=lambda message: message.text == '🗑 Удалить механикума')
        def RemoveMechanicum(message):
            data_mechanicum = self.dbm.GetMechanicum(message.from_user.id)
            data_admin = self.dbm.GetAdmin(message.from_user.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingPossibilityAdministration(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                Actions.AdministrationModeAtions.RemoveMechanicum(message.chat.id, self.bot, self.dbm)
            else:
                self.UserNotHaveRightsMessage(message.chat.id)

        @self.bot.message_handler(commands=['reload_keyboard', 'rk'])
        def ReloadKeyboard(message):
            self.ReloadKeyboard(message)

        @self.bot.message_handler(commands=['help'])
        def HelpMessage(message):
            self.bot.send_message(message.chat.id, '[Документ](https://docs.google.com/document/d/1qP4frm_SSHWqu2zhMGSN06lMAmWWtK1Wv5V_s9igHI4/edit?usp=sharing), описывающий все команды',
                                  parse_mode='Markdown')


        self.caa = threading.Thread(target=self.dbm.CheckingActivityAdministrators)
        self.caa.start()
        self.bot.infinity_polling()

