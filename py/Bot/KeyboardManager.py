from telebot import types
from keyboa import Keyboa

class KeyBoardManager:
        """просто перенёс все кнопки в отдельный класс"""
        
        reload_keyboard_button = types.KeyboardButton(text='🔄 Обновить клавиатуру')
        
        request_button = types.KeyboardButton(text='📩 Сделать запрос')
        catalog_button = types.KeyboardButton(text='📂 Открыть каталог')
        search_category_button = types.KeyboardButton(text='🔎 Поиск по категории')

        suggest_idea_button = types.KeyboardButton(text='💡 Предложить идею')
        show_ideas_button = types.KeyboardButton(text='👀 Посмотреть на идеи')

        sending_settings_button = types.KeyboardButton(text='⚙️ Настройки рассылки')

        admin_section_button = types.KeyboardButton(text='🛠️ Активировать режим администрирования')

        create_new_instruction_button = types.KeyboardButton(text='📝 Создать новую инструкцию')
        edit_instructions_button = types.KeyboardButton(text='✏️ Редактировать инструкцию')
        
        remove_instructions_button = types.KeyboardButton(text='🗑 Удалить инструкцию')

        market_button = types.KeyboardButton(text='🏪 Открыть магазин') 
        open_storage_button = types.KeyboardButton(text='📦 Открыть склад')

        add_prefix_button = types.KeyboardButton(text='🆕 Добавить префикс 🔝')
        remove_prefix_button = types.KeyboardButton(text='🗑 Удалить префикс 🔝')

        add_cap_button = types.KeyboardButton(text='🆕 Добавить шапку 🧢')
        remove_cap_button = types.KeyboardButton(text='🗑 Удалить шапку 🧢')

        add_mechanicum_button = types.KeyboardButton(text='➕ Добавить механикума') 
        edit_mechanicum_button = types.KeyboardButton(text='✏️ Редактировать механикума')
        remove_mechanicum_button = types.KeyboardButton(text='🗑 Удалить механикума')

        send_admin_button = types.KeyboardButton(text='📤 Создать расылку')

        edit_data_admin_button = types.KeyboardButton(text='Изменить данные для входа')
        deactivate_administration_mode_button = types.KeyboardButton(text='🚫 Деактивировать режим администрирования')

        def GetKeyboardInstruction(id_instruction):
        
            menu = []
            
            set_comment_inline_button = types.InlineKeyboardButton(text='Оставить коментарий', callback_data=f'set_comment {id_instruction}')
            get_comment_inline_button = types.InlineKeyboardButton(text='Посмотреть коментарии', callback_data=f'get_comment {id_instruction}')

            menu.append(set_comment_inline_button)
            menu.append(get_comment_inline_button)
            
            answer = Keyboa(items=menu)
            return answer
        

        def CreatingListIstructions(data, tag):
            menu = []
            for i in data:
                menu.append({f'{i[4]}': f'{tag} {i[0]}'})

            answer = Keyboa(items=menu)
            return answer
        
        def CreatingListSections(data):
            menu = []
            for i in data:
               menu.append({i: f'section {i}'})

            answer = Keyboa(items=menu)
            return answer
        
        def CreateMarketCategory(call):
            
            prefix_market_inline_button = types.InlineKeyboardButton(text='🔝 Префиксы',
                                                                     callback_data=f'prefix_{call}')
            cap_market_inline_button = types.InlineKeyboardButton(text='🧢 Шапки',
                                                                  callback_data=f'cap_{call}')

            menu = [prefix_market_inline_button,
                    cap_market_inline_button]
            
            answer = Keyboa(items=menu)

            return answer
        
        def GetItemsKeyboard(data, call):
            menu = []
            for i in data:
                menu.append({f'{i[1]} - {i[2]} 🎖️': f'{call}_buy {i[0]}'})
            answer = Keyboa(items=menu)
            return answer
        
        def GetItemsKeyboardFromStotage(data, call):
            menu = []
            for i in data:
                menu.append({f'{i}': f'set_{call} {i}'})
            answer = Keyboa(items=menu)
            return answer
        
        def GetKeyboardForConfirmationIdea(id_idea):

            accept_idea_button = types.InlineKeyboardButton(text='✅', callback_data=f'idea_accept {id_idea}')
            reject_idea_button = types.InlineKeyboardButton(text='❌', callback_data=f'idea_reject {id_idea}')

            menu = [accept_idea_button, reject_idea_button]
            answer = Keyboa(items=menu, items_in_row=2)
            return answer
        
        def GetSendingSettingsKeyboard():

            personal_sending_button = types.InlineKeyboardButton(text='Изменить персонаяльную рассылку', callback_data='personal_sending')
            admin_sending_button = types.InlineKeyboardButton(text='Изменить рассылку администрации', callback_data='admin_sending')

            menu = [personal_sending_button, admin_sending_button]

            answer = Keyboa(items=menu)
            return answer
        
        def GetAllIdesKeyboard(data):
            text_edit = {
                '0': 'на рассмотрении',
                '1': 'голосание',
                '2': 'принят на создание',
                '3': 'выпущен'
            }
            menu = []
            for i in data:
                menu.append({f'{i[2]} - {text_edit[i[5]]} | {i[6]}': f'show_idea {i[0]}'})
            answer = Keyboa(items=menu)
            return answer
        
        def GetIdeaKeyboard(idea, user_editor, user_admin):
            menu = []
            menu.append(types.InlineKeyboardButton(text='Проголосовать', callback_data=f'vote {idea[0]}'))
            if user_editor:
                if idea[5] == '1':
                    menu.append(types.InlineKeyboardButton(text='Принять на создание', callback_data=f'to_create {idea[0]}'))
                elif idea[5] == '2':
                    menu.append(types.InlineKeyboardButton(text='Выпустить', callback_data=f'release {idea[0]}'))
            if user_admin:
                if idea[5] == '0':
                    menu.append(types.InlineKeyboardButton(text='Подтвердить', callback_data=f'idea_accept {idea[0]}'))
                menu.append(types.InlineKeyboardButton(text='Удалить', callback_data=f'remove_idea {idea[0]}'))

            answer = Keyboa(items=menu)
            return answer