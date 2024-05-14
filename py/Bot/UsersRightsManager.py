from py.Bot.KeyboardManager import KeyBoardManager as KBM

class UsersRightsManager:

    def CreateStartKeyboard(data_mechanicum, data_admin, keyboard): # создание стартоовой клавиатуры для пользовтеля
        if data_mechanicum[4] == True:
            keyboard.add(KBM.request_button, KBM.catalog_button, KBM.search_category_button)
            keyboard.add(KBM.suggest_idea_button, KBM.show_ideas_button)
            keyboard.add(KBM.sending_settings_button)
        if data_mechanicum[5] == True:
            keyboard.add(KBM.create_new_instruction_button, KBM.edit_instructions_button)
        if data_mechanicum[6] == True:
            if data_admin[5] == False or data_admin[5] == None:
                keyboard.add(KBM.admin_section_button, KBM.edit_data_admin_button)
            elif data_admin[5] == True:
                keyboard.add( 
                    KBM.remove_instructions_button,
                    KBM.add_mechanicum_button,
                    KBM.edit_mechanicum_button,
                    KBM.remove_mechanicum_button,
                    KBM.add_prefix_button,
                    KBM.remove_prefix_button,
                    KBM.add_cap_button,
                    KBM.remove_cap_button,
                    KBM.deactivate_administration_mode_button,
                    KBM.send_admin_button)
                
        keyboard.add(KBM.market_button, KBM.open_storage_button)
        keyboard.add(KBM.reload_keyboard_button)

        return keyboard
    
    def CheckingPossibilityAdministration(data_mechanicum): # проверка, может ли механикум быть администратором
        if data_mechanicum[6] == True:
            return True
        else:
            return False
        
    def AdminAuthorizations(message, data_admin): # проверка данных для авторизации
        try:
            login, password = str(message.text).split()
        except ValueError:
            return False
        if login == data_admin[3] and password == data_admin[4]:
            return True
        else:
            return False

    def CheckingMechanicum(data): # проверка на механикума
        if data == None:
            return False
        else:
            return True
        
    def CheckingActivityAdministration(data_admin):
        if data_admin[5]:
            return True
        else:
            return False
        
    def CheckingAdminCapabilities(data_mechanicum):
        if data_mechanicum[6]:
            return True
        else:
            return False
        
    def CheckingEditorCapabilities(data_mechanicum):
        if data_mechanicum[5]:
            return True
        else:
            return False
        
    def CheckingReaderCapabilities(data_mechanicum):
        if data_mechanicum[4]:
            return True
        else:
            return False