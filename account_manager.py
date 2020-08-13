import sqlite3
import os.path
import pandas as pd
import re
import numpy as np

class Account():
    
    MESSAGES = {'already_exist': 'Ваш аккаунт уже существует.',
                'created': 'Ваш аккаунт создан.',
                'expense_added': 'Запись добавлена.',
                'error_expense_add': 'Ошибка: запись не добавлена.',
                'account_link_add': 'Ссылка на аккаунт добавлена.',
                'account_link_delete': 'Ссылка на аккаунт удалена.',
                'account_link_error': 'Ошибка: действие не выполнено.',
                'cancel_complete': 'Последняя запись отменена.',
                'cancel_error': 'Ошибка: последняя запись не отменена.'
               }
    
    MODIFER_FIELDS = {'get_date' : ['Дата'], 
                      'get_category' : ['Категория'],
                      'get_linked' : ['Аккаунт'],
                      'get_together': ['Вместе'],
                      'get_all' : ['Все']
                     }
    
    def __init__(self, user_id):
        self.user_id = user_id
        
    def check(self):
        if os.path.exists('.\data\{}.db'.format(self.user_id)):
            return self.MESSAGES['already_exist']
        else:
            conn = sqlite3.connect('.\data\{}.db'.format(self.user_id))
            c = conn.cursor()
            c.execute('''CREATE TABLE finance (            
                            date     DATETIME,
                            category VARCHAR (100),
                            expenses INTEGER,
                            description     VARCHAR (100)
                        );''')
            c.execute('''CREATE TABLE config (
                            parameter VARCHAR (100),
                            value     VARCHAR (100) 
                        );''')
            conn.commit()
            conn.close()        
            return self.MESSAGES['created']
        
    def add_expense(self, data):
        try:
            conn = sqlite3.connect('.\data\{}.db'.format(self.user_id))
            c = conn.cursor()
            c.execute('''INSERT INTO finance (
                                date,
                                category,
                                expenses,
                                description
                            )
                            VALUES (
                                '{0}',
                                '{1}',
                                '{2}',
                                '{3}'
                            );'''.format(
                                         data[0], 
                                         data[1], 
                                         data[2], 
                                         data[3]
                                        ))
            conn.commit()
            conn.close()
            return self.MESSAGES['expense_added']
        except: 
            return self.MESSAGES['error_expense_add']
    
    def account_link(self, linked_account, mode):
        if mode == 'add':
            try:
                conn = sqlite3.connect('.\data\{}.db'.format(self.user_id))
                c = conn.cursor()
                c.execute('''INSERT INTO config (
                                        parameter,
                                        value
                                    )
                                    VALUES (
                                        '{0}',
                                        '{1}'
                                    );'''.format(
                                                 'linked_account', 
                                                 linked_account
                                                ))
                conn.commit()
                conn.close()
                return self.MESSAGES['account_link_add']
            except: 
                return self.MESSAGES['account_link_error']
        elif mode == 'delete':
            try:
                conn = sqlite3.connect('.\data\{}.db'.format(self.user_id))
                c = conn.cursor()
                c.execute('''DELETE FROM config 
                                    WHERE
                                    parameter = '{0}' AND
                                    value = '{1}'
                                    ;'''.format(
                                                 'linked_account', 
                                                 linked_account
                                                ))
                conn.commit()
                conn.close()
                return self.MESSAGES['account_link_delete']
            except: 
                return self.MESSAGES['account_link_error']
        else:
            return self.MESSAGES['account_link_error']        
        
    def get_expense(self, modifers):
        
        linked_accounts = [self.user_id]
        result = []
        
        # получение списка связанных аккаунтов
        conn = sqlite3.connect('.\data\{}.db'.format(self.user_id))
        c = conn.cursor()        
        for row in c.execute('''SELECT DISTINCT value
                                        FROM config
                                        WHERE parameter = 'linked_account'  '''):
            linked_accounts.append(str(row[0]))
        conn.close()   
        
        # подготовка списка полей для группировки результатов
        modifers_final = []
        if type(modifers) == str:
            modifers_final.append(self.MODIFER_FIELDS[modifers][0])
        elif type(modifers) == list:
            for modifer in modifers:
                try:
                    modifers_final.append(self.MODIFER_FIELDS[modifer][0])
                except:
                    modifers_final.append(None)
        if len(modifers_final) == 0:
            modifers_final = None           
        
        # Если нет запроса на связанные аккаунты, то берем только свой
        if 'Аккаунт' not in modifers_final and 'Вместе' not in modifers_final:
            linked_accounts = [self.user_id]
            
        # получение данных   
        for account in linked_accounts:
            conn = sqlite3.connect('.\data\{}.db'.format(account))
            c = conn.cursor()
            for row in c.execute('''SELECT date, category, expenses, description, '{}' as account
                                            FROM finance
                                            order by date DESC, category ASC, expenses DESC'''.format(account)):
                date_data = str(row[0])
                category_data = str(row[1])
                expense_data = row[2]    
                description_data = row[3]
                account_data = row[4]
                result.append([
                                date_data,
                                category_data,
                                expense_data,
                                description_data,
                                account_data])
        conn.close()
        df = pd.DataFrame(result, columns=['Дата', 'Категория', 'Расходы', 'Описание', 'Аккаунт'])    
       
        # корректировка и вывод результатов        
        if 'Вместе' in modifers_final:
            modifers_final.remove('Вместе') 
            if 'Аккаунт' in modifers_final:
                modifers_final.remove('Аккаунт')
        if 'Все' in modifers_final or len(modifers_final) == 0:
            df_string = df.to_string(index = False, justify = 'left')
            df_string = re.sub('\n\s+', '\n', df_string)
        else:            
            df = pd.pivot_table(df, values='Расходы', index = modifers_final,
                        aggfunc=np.sum)
            df_string = df.to_string()
            
                                
        df_string_corrected = '`' + df_string + '`'
        return df_string_corrected
    
    def cancel_expense(self):
        try:
            conn = sqlite3.connect('.\data\{}.db'.format(self.user_id))
            c = conn.cursor()
            c.execute('''DELETE FROM finance
                         WHERE ID = (SELECT max(id)
                                     FROM finance
                                     );''')
            conn.commit()
            conn.close()        
            return self.MESSAGES['cancel_complete']
        except: 
            return self.MESSAGES['cancel_error']