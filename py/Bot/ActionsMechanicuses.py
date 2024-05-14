from py.Bot.KeyboardManager import KeyBoardManager as KBM
from py.Bot.UsersRightsManager import UsersRightsManager as URM

from datetime import datetime
import os
import ast

class Actions:

    class BasicActions:

        def FoundItem(items, value):
            return value in items
        
        def ParseItems(items, value):
            answer = []
            for i in items:
                if Actions.BasicActions.FoundItem(items, value):
                    continue
                else:
                    answer.append(i)
            return answer
        
        def ParseCallItems(data):
            answer = ''
            for i in data.split()[1:]:
                answer += i + ' '
            return answer
        
        def SendingSettings(chat_id, bot, dbm, data_mechanicum):
            text = {
                1: 'включено',
                0: 'выключено',
                None: 'выключено'}
            keyboard = KBM.GetSendingSettingsKeyboard()
            bot.send_message(chat_id, f'Ваши настройки:\nПерсональные рассылки: {text[data_mechanicum[7]]}\nРассылки администрации: {text[data_mechanicum[8]]}', reply_markup=keyboard())
        
        def PrsonalSendingEdit(chat_id, bot, dbm):
            edit_values = {
                1: [0, 'выключена'],
                0: [1, 'включена'],
                None: [1, 'включена']}
            data_mechanicum = dbm.GetMechanicum(chat_id)
            dbm.EditSendingSettings('sending_personal', edit_values[data_mechanicum[7]][0], chat_id)
            bot.send_message(chat_id, f'Персональная рассылка была {edit_values[data_mechanicum[7]][1]}')

        def AdminSendingEdit(chat_id, bot, dbm):
            edit_values = {
                1: [0, 'выключена'],
                0: [1, 'включена'],
                None: [1, 'включена']}
            data_mechanicum = dbm.GetMechanicum(chat_id)
            dbm.EditSendingSettings('sending_admin', edit_values[data_mechanicum[8]][0], chat_id)
            bot.send_message(chat_id, f'Рассылка администрации была {edit_values[data_mechanicum[8]][1]}')
        
        def OpenMarket(message, bot, dbm):
            
            keyboard = KBM.CreateMarketCategory('market')
            bot.send_message(message.chat.id, 'Выберите полку:', reply_markup=keyboard())

        def OpenItemsMarket(chat_id, bot, dbm, text):
            
            values = dbm.GetAllItems(text)
            if len(values) != 0 and values:
                keyboard = KBM.GetItemsKeyboard(values, text)
                if text == 'prefix':
                    bot.send_message(chat_id, 'Смотрите какие префиксы!', reply_markup=keyboard())
                elif text == 'cap':
                    bot.send_message(chat_id, 'Смотрите какие шапки!', reply_markup=keyboard())
            else:
                bot.send_message(chat_id, 'Тут ничего нету :(')

        def BuyItem(chat_id, bot, dbm, call, text):
            data_mechanicum = dbm.GetMechanicum(chat_id)
            value = dbm.GetItem(text, call)
            if data_mechanicum[12] == None or data_mechanicum[13] == None:
                items_mechanicum = []
            else:
                if text == 'prefix':
                    items_mechanicum = ast.literal_eval(data_mechanicum[12])
                else:
                    items_mechanicum = ast.literal_eval(data_mechanicum[13])
            if not Actions.BasicActions.FoundItem(items_mechanicum, value[1]):
                if data_mechanicum[9] >= int(value[2]):
                    dbm.RemovingPoints(chat_id, value[2])
                    items_mechanicum.append(value[1])
                    dbm.SetMechanicumInventory(text, chat_id, items_mechanicum)
                    bot.send_message(chat_id, f'Предмет {value[1]} был куплен и добавлен в инвентарь')
                else:
                    bot.send_message(chat_id, f'Не хвататет очков активности!')    
            else:
                bot.send_message(chat_id, f'Этот предмет у вас уже е сть!')

        def OpenStorage(chat_id, bot, dbm):
            keyboard = KBM.CreateMarketCategory('storage')
            bot.send_message(chat_id, 'Выберите полку склада:', reply_markup=keyboard())

        def OpenItemStorage(chat_id, bot, dbm, call, text):
            user_items = dbm.GetItemsUser(text, chat_id)
            if user_items != None and len(user_items) != 0:
                user_items = ast.literal_eval(user_items)
                user_items = Actions.BasicActions.ParseItems(user_items, dbm.GetUseUserItem(text, call.from_user.id))
                keyboard = KBM.GetItemsKeyboardFromStotage(user_items, text)
                bot.send_message(chat_id, 'Выберите предмет для отображения:', reply_markup=keyboard())
            else:
                bot.send_message(chat_id, 'У вас нету предметов!')

        def SetItem(chat_id, bot, dbm, call, text):
            item = Actions.BasicActions.ParseCallItems(call.data)
            dbm.SetItemUser(text, call.from_user.id, item)
            bot.send_message(chat_id, f'Предмет {item} был установлен!')

        def SetComment(chat_id, bot, dbm, call):

            def GetDataForSetComment(msg, bot, dbm, call, data_mechanicum):
                data = (call, msg.from_user.id, data_mechanicum[2], msg.text)
                if data[2] != None:
                    dbm.SetComment(data)
                    bot.send_message(msg.chat.id, 'Комментарий добавлен!')
                    dbm.AddActivityPointsUser(msg.from_user.id, 1)
                else:
                    bot.send_message(msg.chat.id, 'Неверный данные для коментария!')

            data_mechanicum = dbm.GetMechanicum(chat_id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                msg = bot.send_message(chat_id, 'Напишите, что вы хотите оставить в виде комментария:')
                bot.register_next_step_handler(msg, GetDataForSetComment, bot, dbm, call, data_mechanicum)
            else:
                bot.UserNotHaveRightsMessage(chat_id)

        def RequestInstructions(chat_id, bot, dbm): # запрос инструкции
            
            def FindInstructions(find_value, instructions):
                answer = []
                for inst in instructions:
                    if inst[4] in find_value:
                        answer.append(inst)

                return answer
            
            def GetDataForRequest(msg, bot, dbm):
                request = msg.text
                instructions = dbm.GetAllInstructions()
                find = FindInstructions(request, instructions)
                if len(find) == 0:
                    bot.send_message(msg.chat.id, 'Не удалось найти инструкцию по такому запросу')    
                
                else:
                    keyboard = KBM.CreatingListIstructions(find, 'id_instruction')
                    bot.send_message(msg.chat.id, 'Нашли такие инструкции:', reply_markup=keyboard())

            data_mechanicum = dbm.GetMechanicum(chat_id)
            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                msg = bot.send_message(chat_id, 'Введите название требуюемой инструкции.')
                bot.register_next_step_handler(msg, GetDataForRequest, bot, dbm)
            else:
                bot.UserNotHaveRightsMessage(chat_id)

        def GetComment(chat_id, bot, dbm, call):
            def ParseComments(data):
                answer = ''
                if len(data) != 0:
                    for i in data:
                        answer += f'[{i[0]}] {' '.join(dbm.GetNameMechanicum(i[2])[0])} - {i[4]}\n'
                else:
                    answer = '🦗 ...'
                
                return answer

            data_mechanicum = dbm.GetMechanicum(chat_id)
            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                comments = dbm.GetComments(call)
                bot.send_message(chat_id, f'Коментарии под иструкцией:\n{ParseComments(comments)}')
                
            else:
                bot.UserNotHaveRightsMessage(chat_id)
        
        def CatalogDisplay(chat_id, bot, dbm): # запрос на показ каталога
            
            def ParsingSection(instructions):
                answer = []
                for i in instructions:
                    if i[3] in answer:
                        continue
                    else:
                        answer.append(i[3])

                return answer
            

            instructions = dbm.GetAllInstructions()
            if len(instructions) != 0:
                data_mechanicum = dbm.GetMechanicum(chat_id)
                if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                    sections = ParsingSection(instructions)
                    keyboard = KBM.CreatingListSections(sections)
                    bot.send_message(chat_id, 'Найдены следующие категории:', reply_markup=keyboard())
                else:
                    bot.UserNotHaveRightsMessage(chat_id)
            else:
                bot.send_message(chat_id, 'Каталоги не найдены :(')

        def ShowAllInstructionsSections(chat_id, bot, dbm, section):
            data_mechanicum = dbm.GetMechanicum(chat_id)
            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                instructions = dbm.GetAllInstructionsSection(section)
                keyboard = KBM.CreatingListIstructions(instructions, 'id_instruction')
            else:
                bot.UserNotHaveRightsMessage(chat_id)

            bot.send_message(chat_id, f'Нашли инструкции из категории {section}:', reply_markup=keyboard())

        def SearchCategory(chat_id, bot, dbm):

            def GetCategoryName(msg, bot, dbm):
                instructions = dbm.GetAllInstructionsSection(msg.text)
                if len(instructions) == 0:
                    bot.send_message(msg.chat.id, f'Категория не найдена.')
                else:
                    keyboard = KBM.CreatingListIstructions(instructions, 'id_instruction')
                    bot.send_message(chat_id, f'Нашли инструкции из категории {msg.text}:', reply_markup=keyboard())
            
            data_mechanicum = dbm.GetMechanicum(chat_id)
            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingReaderCapabilities(data_mechanicum):
                msg = bot.send_message(chat_id, f'Введите название категории:')
                bot.register_next_step_handler(msg, GetCategoryName, bot, dbm)
            else:
                bot.UserNotHaveRightsMessage(chat_id)

        def SuggestIdea(chat_id, bot, dbm, self):
            
            def ParseDataForSuggestIdea(text):
                name = ''
                description = ''
                index = 0
                for i in text:
                    if i == '\n':
                        index += 1
                    else:
                        if index == 0:
                            name += i
                        elif index == 1:
                            description += i
                return name, description
            
            def GetDataForSuggestIdea(msg, bot, dbm):
                name, description = ParseDataForSuggestIdea(msg.text)
                if len(name) != 0 and len(description) != 0:
                    date = datetime.now().date()
                    data = (msg.from_user.id,
                            name, description,
                            f'{date.year}-{date.month}-{date.day}',
                            0, 0)
                    dbm.SuggestIdea(data)
                    keyboard = KBM.GetKeyboardForConfirmationIdea(dbm.GetLastIdea()[0][0])
                    bot.send_message(msg.chat.id, 'Идея предложена со статусом "на расмотрении"')
                    self.SendMessageAllAdmins(f'Предложена запись с данными:\n{data}', keyboard)
                else:
                    bot.send_message(msg.chat.id, 'Данные введены неверно!')

                
            msg = bot.send_message(chat_id, 'Введите построчно:\nНазвание идеи\nОписание идеи')
            bot.register_next_step_handler(msg, GetDataForSuggestIdea, bot, dbm)

        def ShowAllIdeas(chat_id, bot, dbm, user_admin):
            ideas = dbm.GetAllIdea(user_admin)
            if len(ideas) != 0:
                ideas.sort(reverse=True, key=lambda idea: idea[6])
                keyboard = KBM.GetAllIdesKeyboard(ideas)
                bot.send_message(chat_id, 'Нашли вот такие идеи:', reply_markup=keyboard())
            else:
                bot.send_message(chat_id, 'Идей пока что нету...')

        def ShowIdea(chat_id, bot, dbm, call, user_admin):
            data_mechanicum = dbm.GetMechanicum(chat_id)
            idea = dbm.GetIdea(call)
            if len(idea) != 0:
                idea = idea[0]
                keyboard = KBM.GetIdeaKeyboard(idea, data_mechanicum[5], user_admin)
                bot.send_message(chat_id, f'Идея: {idea[2]}\nОписание: {idea[3]}\nГолоса: {idea[6]}\nСоздатель: {' '.join(dbm.GetNameMechanicum(idea[1])[0])}', reply_markup=keyboard())
            else:
                bot.send_message(chat_id, 'Возможно, эта идея уже удалена')

        def VoteIdea(chat_id, bot, dbm, call):
            if dbm.CheckUserVote(call, chat_id):
                dbm.VoteIdea(chat_id, call)
                bot.send_message(chat_id, 'Ваш голос записан!')
                dbm.AddActivityPointsUser(chat_id, 1)
            else:
                bot.send_message(chat_id, 'Вы уже проголосовали!')
        
        def RemoveIdea(chat_id, bot, dbm, call):

            def GetDataForRemoveIdea(msg, bot, dbm, call):
                if msg.text == 'подтвердить':
                    dbm.IdeaReject(call)
                    bot.send_message(msg.chat.id, 'Идея была удалена!')
                else:
                    pass
            
            msg = bot.send_message(chat_id, 'Напишите "подтвердить" для удаления:')
            bot.register_next_step_handler(msg, GetDataForRemoveIdea, bot, dbm, call)

        def ToCreateIdea(chat_id, bot, dbm, call):
            idea = dbm.GetIdea(call)
            if len(idea) != 0:
                idea = idea[0]
                if int(idea[5]) == 1:
                    dbm.IdeaAccept(call, 2)
                    bot.send_message(chat_id, 'Идея взята на разработку!')
                    if dbm.GetMechanicum(idea[1])[7] and idea[1] != chat_id:
                        bot.send_message(idea[1], f'Ваша идея "{idea[2]}" принята на разработку!')
                else:
                    bot.send_message(chat_id, 'Идея имеет другой статус')
            else:
                bot.send_message(chat_id, 'Возможно, эта идея уже удалена')

        def ReleaseIdea(chat_id, bot, dbm, call):
            idea = dbm.GetIdea(call)
            if len(idea) != 0:
                idea = idea[0]
                if int(idea[5]) == 2:
                    dbm.IdeaAccept(call, 3)
                    bot.send_message(chat_id, 'Вы выпустили продукт идеи!')
                    if dbm.GetMechanicum(idea[1])[7] and idea[1] != chat_id:
                        bot.send_message(idea[1], f'Ваша идея "{idea[2]}" была выпущена!')
                else:
                    bot.send_message(chat_id, 'Идея имеет другой статус')
            else:
                bot.send_message(chat_id, 'Возможно, эта идея уже удалена')




    class EditingModeActions(BasicActions):

        def ParseData(data):
            section = ''
            name = ''
            description = ''
            url = ''
            index = 0
            try:
                for i in data:
                    if i == '\n':
                        index += 1
                        continue
                    elif index == 0:
                        section += i
                    elif index == 1:
                        name += i
                    elif index == 2:
                        description += i
                    elif index == 3:
                        url += i

            except Exception:
                return False, False, False, False
            else:
                return section, name.lower(), description, url
            
        def CreatingInstructions(chat_id, bot, dbm): # создание новой инструкции

            def GetDataForAddInstructions(msg, bot, dbm):
                date = datetime.now().date()
                section, name, description, url = Actions.EditingModeActions.ParseData(msg.caption)
                if section:
                    photo = msg.photo[-1]
                    file_info = bot.get_file(photo.file_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    save_path = f'{photo.file_id}.png'
                    with open(f'Content/photos/{save_path}', 'wb') as new_file:
                        new_file.write(downloaded_file)

                    data = (msg.from_user.id,
                            f'{date.year}-{date.month}-{date.day}',
                            section,
                            name,
                            description,
                            url,
                            save_path)
                        
                    dbm.AddInstruction(data)
                    bot.send_message(msg.chat.id, f'Добавлена инструкция со следующими данными:\n{data}')
                    dbm.AddActivityPointsUser(msg.from_user.id, 3)
                else:
                    bot.send_message(msg.chat.id, f'Инструкция не была добавлена из-за неверных данных')

            
            data_mechanicum = dbm.GetMechanicum(chat_id)
            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingEditorCapabilities(data_mechanicum):
                msg = bot.send_message(chat_id, 'Напишите текст следующим оброазом (цифра означает номер строки):\n[1] Имя раздела\n[2] Название инструкции\n[3] Краткое описание раздела\n[4] Ссылка на документ\nТакже прикрепите фото к записе.')
                bot.register_next_step_handler(msg, GetDataForAddInstructions, bot, dbm)
            else:
                bot.UserNotHaveRightsMessage(chat_id)

        
        def GetIDEditInstructions(message, bot, dbm):
            data_mechanicum = dbm.GetMechanicum(message.chat.id)
            data_admin = dbm.GetAdmin(message.chat.id)

            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingEditorCapabilities(data_mechanicum):
                if URM.CheckingAdminCapabilities(data_mechanicum) and URM.CheckingActivityAdministration(data_admin):
                    instructions = dbm.GetAllInstructions()
                else:
                    instructions = dbm.GetInstructionsUser(message.from_user.id)
                
                if len(instructions) != 0:
                    keyboard = KBM.CreatingListIstructions(instructions, 'edit_id')
                    bot.send_message(message.chat.id, 'Выберите инструкцию для редактирования:', reply_markup=keyboard())
                else:
                    pass
            else:
                bot.UserNotHaveRightsMessage(message.chat.id)
            

        def EditInstructions(chat_id, bot, dbm, id_instruction):
            
            def GetDataForEditInstructions(msg, bot, dbm, id_instruction):
                section, name, description, url = Actions.EditingModeActions.ParseData(msg.caption)
                if section:
                    photo = msg.photo[-1]
                    file_info = bot.get_file(photo.file_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    save_path = f'{photo.file_id}.png'
                    with open(f'Content/photos/{save_path}', 'wb') as new_file:
                        new_file.write(downloaded_file)

                    data_instruction = dbm.GetInstruction(id_instruction)

                    os.remove(f'Content/photos/{data_instruction[7]}')
                    
                    data = (msg.from_user.id,
                            section,
                            name,
                            description,
                            url,
                            save_path)
                            
                    
                    dbm.EditInstruction(id_instruction, data)
                    bot.send_message(msg.chat.id, f'Инструкция отредактирована со следующими данными:\n{data}')
                    dbm.AddActivityPointsUser(msg.from_user.id, 2)
                else:
                    bot.send_message(msg.chat.id, f'Инструкция не была отредактирована из-за неверных данных')
            
            data_mechanicum = dbm.GetMechanicum(chat_id)
            if URM.CheckingMechanicum(data_mechanicum) and URM.CheckingEditorCapabilities(data_mechanicum):
                msg = bot.send_message(chat_id, 'Для редактирования напишите текст следующим оброазом (цифра означает номер строки):\n[1] Имя раздела\n[2] Название инструкции\n[3] Краткое описание раздела\n[4] Ссылка на документ\nТакже прикрепите фото к записе.')
                bot.register_next_step_handler(msg, GetDataForEditInstructions, bot, dbm, id_instruction)
            else:
                bot.UserNotHaveRightsMessage(chat_id)

        def RemoveInstructions(chat_id,  bot, dbm):
            
            def GetDataForRemoveInstructions(msg, bot, dbm):
                id = int(msg.text)
                try:
                    dbm.RemoveInstruction(id)
                except Exception:
                    bot.send_message(msg.chat.id, 'Неверные данные для удаления')
                else:
                    bot.send_message(msg.chat.id, 'Инструкция удалена')
            
            def ParseInstructions(data):
                answer = 'id  |  section  |  name\n'
                for i in data:
                    answer += f'[{i[0]}]  |  {i[3]}  |  {i[4]}\n'
                return answer

            instructions = ParseInstructions(dbm.GetAllInstructions())

            msg = bot.send_message(chat_id, f'Введите id инструкции для удаления:\n{instructions}')
            bot.register_next_step_handler(msg, GetDataForRemoveInstructions, bot, dbm)

    class AdministrationModeAtions(EditingModeActions):

        def ParsePrefixAndCapForAdd(data):
            value = ''
            price = ''

            index = 0
            for i in data:
                if i == '\n':
                    index += 1
                    continue
                elif index == 0:
                    value += i
                elif index == 1:
                    price += i
                
            
            return value, price
        
        def ParsePrefixAndCapForRemove(data):
            answer = 'id  |  value  |  price\n'
            for i in data:
                answer += f'[{i[0]}]    {i[1]}    {i[2]}\n'
            return answer
        
        def ParseMechanicum(data):
            answer = 'id  |  id_telegram  |  real_name  |  rank  | reader | editor | admin\n'
            for i in data:
                answer += f'[{i[0]}]  |  {i[1]}  |  {i[2]}  |  {i[3]}  | {i[4]} | {i[5]} | {i[6]}\n'
            return answer

        def IdeaAccept(admin_id, bot, dbm, call):
            idea = dbm.GetIdea(call)
            if len(idea) != 0:
                idea = idea[0]
                if int(idea[5]) == 0:
                    dbm.IdeaAccept(call, 1)
                    dbm.AddActivityPointsUser(admin_id, 1)
                    data_mechanicum = dbm.GetMechanicum(idea[1])
                    if data_mechanicum[7] and idea[1] != admin_id:
                        bot.send_message(idea[1], f'Идея {idea[2]} была проверена!')
                    
                    bot.send_message(admin_id, f'Вы подтвержили идею')
                else:
                    bot.send_message(admin_id, f'Идея уже принята')
            else:
                bot.send_message(admin_id, f'Возможно, идея была удалена')

        def IdeaReject(admin_id, bot, dbm, call):
            idea = dbm.GetIdea(call)
            if len(idea) != 0:
                idea = idea[0]
                if int(idea[5]) == 1:
                    bot.send_message(admin_id, f'Идея уже принята. Невозможно удалить.')
                else:
                    dbm.IdeaReject(call)
                    dbm.AddActivityPointsUser(admin_id, 1)
                    data_mechanicum = dbm.GetMechanicum(idea[1])
                    if data_mechanicum[7]:
                        bot.send_message(idea[1], f'Идея {idea[2]} была отвергнута!')
                    
                    bot.send_message(admin_id, f'Идея была удалена')
            else:
                bot.send_message(admin_id, f'Возможно, идея была удалена')
        
        
        def AddItem(message, bot, dbm, text):
            
            def GetDataForAddItem(msg, bot, dbm):
                item, price = Actions.AdministrationModeAtions.ParsePrefixAndCapForAdd(msg.text)
                try:
                    int(price)
                except Exception:
                    bot.send_message(msg.chat.id, f'Неверные данные!')
                else:
                    if (len(item) == 1 and text == 'cap') or text == 'prefix':
                        data = (item, price)
                        dbm.AddItem(text, data)
                        if text == 'prefix':
                            bot.send_message(msg.chat.id, f'Префикс добавлен с данными: {data}')
                        elif text == 'cap':
                            bot.send_message(msg.chat.id, f'Шапка добавлена с данными: {data}')
                        dbm.AddActivityPointsUser(msg.chat.id, 1)
                    else:
                        bot.send_message(msg.chat.id, f'Шапка - это один смайлик!')
                
                dbm.UpdatingAdministratorActivity(msg.from_user.id)

            
            if text == 'prefix':
                msg = bot.send_message(message.chat.id, 'Введите префикс и цену построчно:')
            elif text == 'cap':
                msg = bot.send_message(message.chat.id, 'Введите шапку и цену построчно:')

            bot.register_next_step_handler(msg, GetDataForAddItem, bot, dbm)

        def RemoveItem(message, bot, dbm, text):

            def GetDataForRemoveItem(msg, bot, dbm, items):
                id_item = msg.text
                try:
                    dbm.RemoveItem(text, id_item)
                except Exception:
                    bot.send_message(msg.chat.id, 'Неверные данные для удаления')
                else:
                    bot.send_message(msg.chat.id, 'Предмет был удалён!')
                    dbm.AddActivityPointsUser(msg.from_user.id, 1)

                dbm.UpdatingAdministratorActivity(msg.from_user.id)
            
            values = dbm.GetAllItems(text)
            if text == 'prefix':
                msg = bot.send_message(message.chat.id, f'Введите id префикса, который требуется удалить:\n{Actions.AdministrationModeAtions.ParsePrefixAndCapForRemove(values)}')
            elif text == 'cap':
                msg = bot.send_message(message.chat.id, f'Введите id шапки, который требуется удалить:\n{Actions.AdministrationModeAtions.ParsePrefixAndCapForRemove(values)}')
            bot.register_next_step_handler(msg, GetDataForRemoveItem, bot, dbm, values)

        
        def AddMechanicum(chat_id, bot, dbm): # добавление механикума
            
            def ParseName(value):
                answer = ''
                for i in value:
                    if i == '_':
                        answer += ' '
                    else:
                        answer += i

                return answer
            
            def GetDataForAddMechanicum(msg, bot, dbm):
                data = msg.text.split()
                try:
                    data[1] = ParseName(data[1])
                    dbm.AddMechanicum(data)
                    if int(data[5]) == 1:
                        a = dbm.GetLastMechanicum(data[0])[0]
                        dbm.AddAdmin([a[1], a[0]])
                except Exception as e:
                    bot.send_message(msg.chat.id, 'Механикум не был добавлен из-за неверно введённых данных.')
                else:
                    bot.send_message(msg.chat.id, f'Механикум был добавлен со следующими данными:\n{data}')
                    dbm.AddActivityPointsUser(msg.from_user.id, 2)
                    

                dbm.UpdatingAdministratorActivity(msg.from_user.id)
            
            msg = bot.send_message(chat_id, 'Для добавления нвого механикума введите через пробел данные:\n \
id_telegram INTEGER (id тг-пользователя)\n \
real_name TEXT (как зовут механикума, фамилия и имя разделяется "_")\n\
rank TEXT, (ранг механикума)\n\
reader BOOLEAN, (возможность чтения)\n\
editor BOOLEAN, (возможность редактирования)\n\
admin BOOLEAN (возможность администрирования)')
            
            bot.register_next_step_handler(msg, GetDataForAddMechanicum, bot, dbm)

        
        def EditMechanicum(chat_id, bot, dbm):
            
            def ParseText(text):
                data = ''
                id_m = ''
                index = 0
                for i in text:
                    if i == '\n':
                        index += 1
                        continue
                    elif index == 0:
                        data += i
                    elif index == 1:
                        id_m += i
                return data, id_m

            def GetDataForEditMechanicum(msg, bot, dbm):
                data, id_m = ParseText(msg.text)
                try:
                    dbm.EditMechanicum(data, id_m)
                except Exception as e:
                    bot.send_message(msg.chat.id, 'Механикум не был отредактирован. Неверные данные!')
                else:
                    bot.send_message(msg.chat.id, 'Механикум был отредактирован')
                    dbm.AddActivityPointsUser(msg.from_user.id, 1)

                dbm.UpdatingAdministratorActivity(msg.from_user.id)

            text = Actions.AdministrationModeAtions.ParseMechanicum(dbm.GetAllMechanicum())
            
            bot.send_message(chat_id, '**Внимание!** Для использваония этой функции администратору требуется знать немного синтаксиса SQL! На то он и администратор...', parse_mode='Markdown')
            bot.send_message(chat_id, 'На первой строке перечислите названия столбцов и чему они равны, на второй же напишите id механикума, которого требуется отредактировать. Пример реализации:\n```SQL\nreal_name = "test_name", admin = 0\n2```', parse_mode='Markdown')
            msg = bot.send_message(chat_id, f'Все механикумы:\n{text}')
            bot.register_next_step_handler(msg, GetDataForEditMechanicum, bot, dbm)

        def RemoveMechanicum(chat_id, bot, dbm):
            
            def GetDataForRemoveMechanicum(msg, bot, dbm):
                id_m = msg.text
                try:
                    dbm.RemoveMechanicum(id_m)
                except Exception:
                    bot.send_message(msg.chat.id, 'Механикум не был удалён. Неверные данные!')
                else:
                    bot.send_message(msg.chat.id, 'Механикум удалён')
                    dbm.AddActivityPointsUser(msg.from_user.id, 1)

                dbm.UpdatingAdministratorActivity(msg.from_user.id)
                
            
            text = Actions.AdministrationModeAtions.ParseMechanicum(dbm.GetAllMechanicum())

            msg = bot.send_message(chat_id, f'Введите id механикума, которого нужно удалить:\n{text}')
            bot.register_next_step_handler(msg, GetDataForRemoveMechanicum, bot, dbm)

        def AdminSending(chat_id, bot, dbm, self):
            
            def GetDataForAdminSending(msg, bot, dbm, self):
                self.SendMessageAllMechanicum(msg.text, msg.from_user.id)
            
            msg = bot.send_message(chat_id, f'Напишите, что вы хотите разослать механикумам:')
            bot.register_next_step_handler(msg, GetDataForAdminSending, bot, dbm, self)