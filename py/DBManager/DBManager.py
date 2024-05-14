import sqlite3
import time
import threading


class DBManager:

    def __init__(self):
        self.con = sqlite3.connect('Content/DataBase.db', check_same_thread=False)
        self.cur = self.con.cursor()

        self.CreatingTables()
        self.InsertingMainUser()

    def CreatingTables(self): # создание таблиц
        self.cur.execute("""CREATE TABLE IF NOT EXISTS telegram_users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_telegram INTEGER,
                        username TEXT
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS mechanicum(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_telegram INTEGER,
                         real_name TEXT,
                         rank TEXT,
                         reader BOOLEAN,
                         editor BOOLEAN,
                         admin BOOLEAN,
                         sending_personal BOOLEAN,
                         sending_admin BOOLEAN,
                         activity_points INTEGER,
                         use_prefix TEXT,
                         use_cap TEXT,
                         inventory_prefixs TEXT,
                         inventory_caps TEXT
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS instructions(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_telegram_creator INTEGER,
                         date_creation TEXT,
                         section TEXT,
                         name TEXT,
                         description TEXT,
                         url TEXT,
                         photo TEXT
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS comments(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_instruction INTEGER,
                         id_mechanicum INTEGER,
                         name_mechanicum TEXT,
                         comment TEXT
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS creation_requests(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_telegram_user INTEGER,
                         name_request TEXT,
                         description TEXT,
                         date_creation TEXT,
                         status TEXT,
                         votes INTEGER
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS votes(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_telegram INTEGER,
                         id_idea INTEGER
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS admins(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         id_telegram INTEGER,
                         id_mechanicum INTEGER,
                         login TEXT,
                         password TEXT,
                         status BOOLEAN,
                         time_start INTEGER,
                         notifications BOOLEAN
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS prefixs(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         prefix TEXT,
                         price INTEGER
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS caps(
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         cap TEXT,
                         price INTEGER
        )""")

        self.con.commit()

    def RecordUser(self, data): # запись телеграм пользовтеля в бд

        self.cur.execute(f'SELECT id_telegram FROM telegram_users WHERE id_telegram={data.from_user.id}')
        if self.cur.fetchone() == None:
            self.cur.execute('INSERT INTO telegram_users (id_telegram, username) VALUES (?, ?);', (data.from_user.id, data.from_user.username))
            self.con.commit()
    
    def VerificationUserExistence(self, table, id_telegram): # проверка на существования пользователя в бд
        self.cur.execute(f'SELECT id_telegram FROM {table} WHERE id_telegram={id_telegram}')
        if self.cur.fetchone() == None:
            return False
        else:
            return True
    
    def InsertingMainUser(self): # добавление галвного пользователей в БД 
        if not ( self.VerificationUserExistence(table='mechanicum', id_telegram=977978002)):
            self.cur.execute('INSERT INTO mechanicum(id_telegram, real_name, rank, reader, editor, admin, activity_points, use_prefix, use_cap) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);', (977978002, 'Totaru Seika', '[неизвестно]', True, True, True, 0, '', ''))
            self.con.commit()
        if not (self.VerificationUserExistence(table='admins', id_telegram=977978002)):    
            self.cur.execute('INSERT INTO admins(id_telegram, id_mechanicum, login, password, status, time_start, notifications) VALUES (?, ?, ?, ?, ?, ?, ?);', (977978002, 1, 'TotaruSeika', 'qwerty12QQ!', False, None, True))
            self.con.commit()

    def EditSendingSettings(self, sending_type, value, id_telegram):
        self.cur.execute(f'UPDATE mechanicum SET {sending_type} = ? WHERE id_telegram = {id_telegram}', (value, ))
        self.con.commit()
        
    def GetAdmin(self, id_telegram): # получение данных о записи админи
        self.cur.execute(f'SELECT * FROM admins WHERE id_telegram={id_telegram}')
        return self.cur.fetchone()
    
    def GetAllAdmins(self):
        self.cur.execute(f'SELECT * FROM admins JOIN mechanicum ON admins.id_telegram = mechanicum.id_telegram WHERE mechanicum.admin = 1 AND admins.notifications = 1;')
        return self.cur.fetchall()
    
    def GetAllItems(self, table):
        self.cur.execute(f'SELECT * FROM {table}s')
        return self.cur.fetchall()
    
    def GetItem(self, column, id_item):
        self.cur.execute(f'SELECT * FROM {column}s WHERE id={id_item}')
        return self.cur.fetchone()
    
    def GetItemsUser(self, column, id_telegram):
        self.cur.execute(f'SELECT inventory_{column}s FROM mechanicum WHERE id_telegram={id_telegram}')
        return self.cur.fetchone()[0]
    
    def GetUseUserItem(self, column, id_telegram):
        self.cur.execute(f'SELECT use_{column} FROM mechanicum WHERE id_telegram={id_telegram}')
        return self.cur.fetchone()[0]
    
    def SetItemUser(self, column, id_telegram, item):
        self.cur.execute(f'UPDATE mechanicum SET use_{column} = ? WHERE id_telegram={id_telegram}', (item, ))
        self.con.commit()
    
    def AddItem(self, column, data):
        self.cur.execute(f'INSERT INTO {column}s({column}, price) VALUES (?, ?);', data)
        self.con.commit()

    def RemoveItem(self, item, id_item):
        self.cur.execute(f'DELETE FROM {item}s WHERE id={id_item}')
        self.con.commit()
    
    def AddActivityPointsUser(self, id_telegram, points):
        points_user = self.PointUserCheck(self.GetPointsUser(id_telegram))
        points_user += points
        self.SetPointsUser(id_telegram, points)
        
    def GetPointsUser(self, id_telegram):
        self.cur.execute(f'SELECT activity_points FROM mechanicum WHERE id_telegram={id_telegram}')
        return self.cur.fetchone()[0]
    
    def PointUserCheck(self, points):
        if points != None:
            pass
        else:
            points = 0
        return points 

    def SetPointsUser(self, id_telegram, points):
        self.cur.execute(f'UPDATE mechanicum SET activity_points = ? WHERE id_telegram={id_telegram}', (points, ))
        self.con.commit()

    def RemovingPoints(self, id_telegram, price):
        points_user = self.PointUserCheck(self.GetPointsUser(id_telegram))
        points_user -= price
        self.SetPointsUser(id_telegram, points_user)

    def SetMechanicumInventory(self, column, id_telegram, data):
        self.cur.execute(f'UPDATE mechanicum SET inventory_{column}s = ? WHERE id_telegram={id_telegram}', (str(data), ))
        self.con.commit()
    
    def GetMechanicum(self, id_telegram): # получение данных о записи механикума
        self.cur.execute(f'SELECT * FROM mechanicum WHERE id_telegram={id_telegram}')
        return self.cur.fetchone()
    
    def GetAllMechanicum(self):
        self.cur.execute('SELECT * FROM mechanicum')
        return self.cur.fetchall()
    
    def EditMechanicum(self, data, id_m):
        self.cur.execute(f'UPDATE mechanicum SET {data} WHERE id={id_m}')
        self.con.commit()

    def RemoveMechanicum(self, id_m):
        self.cur.execute(f'DELETE FROM mechanicum WHERE id={id_m}')
        self.con.commit()

    def GetNameMechanicum(self, id_telegram):
        self.cur.execute(f'SELECT use_prefix, real_name, use_cap FROM mechanicum WHERE id_telegram={id_telegram}')
        return self.cur.fetchall()

    def GetMechanicumForAdminSending(self):
        self.cur.execute(f'SELECT id_telegram FROM mechanicum WHERE sending_admin=1')
        return self.cur.fetchall()
    
    def AddAdmin(self, data):
        data.append(1)
        self.cur.execute(f'INSERT INTO admins(id_telegram, id_mechanicum, notifications) VALUES (?, ?, ?);', data)
        self.con.commit()
    
    def EditDataAAdmin(self, data, id_telegram):
        self.cur.execute(f'UPDATE admins SET login = ?, password = ? WHERE id_telegram={id_telegram}', data)
        self.con.commit()
    
    def ActivatingAdministratorMode(self, id_telegram):
        self.cur.execute(f'UPDATE admins SET status = ?, time_start = ? WHERE id_telegram={id_telegram}', (True, int(time.time())))

    def AddMechanicum(self, data):
        data.append('')
        data.append('')
        self.cur.execute('INSERT INTO mechanicum(id_telegram, real_name, rank, reader, editor, admin, use_prefix, use_cap) VALUES (?, ?, ?, ?, ?, ?, ?, ?);', data)
        self.con.commit()

    def GetLastMechanicum(self, id_telegram):
        self.cur.execute(f'SELECT * FROM mechanicum WHERE id_telegram = {id_telegram};')
        return self.cur.fetchall()

    def AddInstruction(self, data):
        self.cur.execute('INSERT INTO instructions(id_telegram_creator, date_creation, section, name, description, url, photo) VALUES (?, ?, ?, ?, ?, ?, ?)', data)
        self.con.commit()

    def UpdatingAdministratorActivity(self, id_telegram):
        self.cur.execute(f'UPDATE admins SET time_start = ? WHERE id_telegram={id_telegram}', (int(time.time()), ))
        self.con.commit()

    def SetComment(self, data):
        self.cur.execute(f'INSERT INTO comments(id_instruction, id_mechanicum, name_mechanicum, comment) VALUES (?, ?, ?, ?);', data)
        self.con.commit()
    
    def GetComments(self, id_instruction):
        self.cur.execute(f'SELECT * FROM comments WHERE id_instruction={id_instruction}')
        return self.cur.fetchall()

    def GetAllInstructions(self):
        self.cur.execute('SELECT * FROM instructions')
        return self.cur.fetchall()
    
    def GetAllInstructionsSection(self, section):
        self.cur.execute(f'SELECT * FROM instructions WHERE section="{section}"')
        return self.cur.fetchall()
    
    def GetInstruction(self, id_instruction):
        self.cur.execute(f'SELECT * FROM instructions WHERE id={id_instruction}')
        return self.cur.fetchone()

    def GetInstructionsUser(self, id_telegram):
        self.cur.execute(f'SELECT * FROM instructions WHERE id_telegram_creator={id_telegram}')
        return self.cur.fetchall()
    
    def EditInstruction(self, id_instruction, data):
        self.cur.execute(f'UPDATE instructions SET id_telegram_creator = ?, section = ?, name = ?, description = ?, url = ?, photo = ? WHERE id = {id_instruction}', data)
        self.con.commit()

    def RemoveInstruction(self, id_instruction):
        self.cur.execute(f'DELETE FROM instructions WHERE id={id_instruction}')
        self.con.commit()

    def SuggestIdea(self, data):
        self.cur.execute(f'INSERT INTO creation_requests(id_telegram_user, name_request, description, date_creation, status, votes) VALUES (?, ?, ?, ?, ?, ?);', data)
        self.con.commit()
    
    def IdeaAccept(self, id_idea, value):
        self.cur.execute(f'UPDATE creation_requests SET status = {value} WHERE id={int(id_idea)}')
        self.con.commit()

    def IdeaReject(self, id_idea):
        self.cur.execute(f'DELETE FROM creation_requests WHERE id={id_idea}')
        self.con.commit()

    def GetLastIdea(self):
        self.cur.execute(f'SELECT * FROM creation_requests WHERE id = last_insert_rowid();')
        return self.cur.fetchmany()
    
    def GetIdea(self, id_idea):
        self.cur.execute(f'SELECT * FROM creation_requests WHERE id = {id_idea}')
        return self.cur.fetchmany()
    
    def GetAllIdea(self, user_admin):
        if not user_admin:
            self.cur.execute('SELECT * FROM creation_requests WHERE status BETWEEN 1 AND 2;')
        else:
            self.cur.execute('SELECT * FROM creation_requests')
        return self.cur.fetchall()

    def CheckUserVote(self, id_idea, id_telegram):
        self.cur.execute(f'SELECT id FROM votes WHERE id={id_idea} AND id_telegram={id_telegram}')
        if self.cur.fetchone() == None:
            return True
        else:
            return False
        
    def VoteIdea(self, id_telegram, id_idea):
        self.cur.execute(f'INSERT INTO votes(id_telegram, id_idea) VALUES (?, ?)', (id_telegram, id_idea))
        votes = self.cur.execute(f'SELECT votes FROM creation_requests WHERE id={id_idea}').fetchone()
        if votes != None:
            votes = votes[0]
        else:
            votes = 0
        self.cur.execute(f'UPDATE creation_requests SET votes = {votes+1} WHERE id={id_idea}')
        self.con.commit()
            
    def DeactivateAdministrationMode(self, id_telegram):
        self.cur.execute(f'UPDATE admins SET status = ?, time_start = ? WHERE id_telegram={id_telegram}', (False, None))
        self.con.commit()


    def CheckingActivityAdministrators(self):
        t = threading.currentThread()
        while getattr(t, 'running', True):
            time.sleep(1)
            self.cur.execute('SELECT * FROM admins')
            admins = self.cur.fetchmany()
            for admin_data in admins:
                if admin_data[5]:
                    if (time.time()-admin_data[6])/60 >= 5:
                        self.DeactivateAdministrationMode(admin_data[1])
        print('Поток остановклен!')