import re
from datetime import datetime
import pandas as pd

class Analyzer():
    
    IGNORE_LIST = ['рублей','руб','р']
    WELCOME_LIST = ['привет','хай','добрый день','здравствуйте']
    GET_LIST = ['получить','показать','затраты', 'посмотреть','вывести']
    CLEAR_LIST = ['очистить','удалить','стереть']
    CREATE_LINK_LIST = ['связать']
    DROP_LINK_LIST = ['отвязать']
    CANCEL_LIST = ['отменить','отмена']
    
    CATEGORY_LIST = {'продукты' : ['пятерочка','лента','перекресток','продукты','еда','корм','пятера','овощебаза','овощи','ягоды'], 
                     'автомобиль' : ['бензин','т/о','запчасти','автомобиль','бенз'],
                     'развлечения' : ['роллы','пиво','рейв','флекс','туса','кафе','бар','игги','томато','дудки','баня','велосипеды','развлечения','кальян','табак','шашлыки','шашлык'],
                     'красота' : ['подружка','косметика','красота','косметолог'],
                     'дом' : ['ипотека','кварплата','интернет','хозтовары']
                    }
    
    MODIFER_LIST = {'get_date' : ['дате','дату','датам'], 
                    'get_category' : ['категории', 'группе', 'категориям', 'группам'],
                    'get_all' : ['все','всё','полностью'],
                    'get_together': ['вместе'],
                    'get_linked' : ['связанные','доступные','аккаунтам', 'семейные', 'общие']
                   }
    
    MESSAGES = {'mode_data_recording': 'Запись расходов.',
                'mode_command_processing': 'Обработка команды.',
                'mode_command_processing_welcome': 'Приветствие.',
                'mode_command_processing_get': 'Получение данных.',
                'mode_command_processing_clear': 'Удаление данных.',
                'identified_categories': 'Выделены категории: ',
                'error_several_categories': 'Ошибка: определено несколько категорий.',
                'target_category': 'Категория определена: ',
                'error_invalid_input_data': 'Ошибка: некорректные входные данные.',
                'error_invalid_command': 'Ошибка: некорректная команда.',
                'error_category_detector': 'Ошибка: категория не определена.',
                'mode_command_processing_cancel': 'Последняя запись отменена.',
                'mode_command_processing_create_link': 'Добавлен связанный аккаунт.',
                'mode_command_processing_drop_link': 'Удален связанный аккаунт.'
               }
    
    # определяет категорию расходов по ключевому слову
    def category_detector(self, input_word):
        for category in self.CATEGORY_LIST:
            for key_word in self.CATEGORY_LIST[category]:
                if key_word == input_word:
                    return category
        return ValueError
    
    # определяет категорию расходов по ключевому слову
    def modifer_detector(self, input_word):
        for modifer in self.MODIFER_LIST:
            for key_word in self.MODIFER_LIST[modifer]:
                if key_word == input_word:
                    return modifer
        return ValueError
    
    '''
    Вход: сообщение пользователя
    Выходы: сообщение, данные. Если ошибка, то в данных ValueError
    '''
    def message_analyzer(self, string):
        result = []
        data = []
        date = str(datetime.now().date()) # текущая дата
        find_digit = re.findall(r'\d+', string) # поиск чисел
        find_text = re.findall(r'[A-zА-я]+', string) # поиск слов
        # если есть и числа и слова и слова не входят в списки ключевых слов управления связью аккаунтов (т.к. там будет id аккаунта)
        if len(find_digit)>0 and len(find_text)>0 and len(set(find_text) & (set(self.DROP_LINK_LIST) | set(self.CREATE_LINK_LIST))) == 0:
            result.append(self.MESSAGES['mode_data_recording']) # print('Режим 1. Запись расходов.')
            category_list = [] # хранилище под найденные категории
            expense = find_digit[0] # первое выделенное число (аналируем только его, все остальные идут в описание)
            for word in find_text: 
                word = word.strip().lower()
                category = self.category_detector(word) # определяем категорию каждого слова
                if category != ValueError: # если категория опредеена, то добавляем в список
                    category_list.append(category)
            if len(category_list)>0: # если категории удалось выделить
                result.append(self.MESSAGES['identified_categories'] + ', '.join(category_list) + '.') # print('Выделены категории: ', category_list)
                if len(set(category_list)) != 1: # выдать ошибку если выделено более одной
                    result.append(self.MESSAGES['error_several_categories']) # print('Определено несколько категорий.')
                    return result, ValueError, 'error'
                else: # если выделена одна, то сформировать список для записи в БД
                    category = category_list[0] # выделенная категория
                    description = ' '.join([word for word in find_text if word not in set(self.IGNORE_LIST)]) # описание - выделенные слова без IGNORE_LIST-слов
                    result.append(self.MESSAGES['target_category'] + category_list[0] + '.') # print('Категория определена: ', category_list[0])
                    data.append([date, category, expense, description]) # print([expense, category, date, description]) # затраты, категория, дата, описание
                    return result, data, 'add'
            else:
                result.append(self.MESSAGES['error_category_detector'])
                return result, ValueError, 'error'
        elif len(find_text)>0: # если есть толлько текст
            result.append(self.MESSAGES['mode_command_processing']) # print('Режим 2. Обработка команды.')
            for word in find_text:
                word = word.strip().lower()
                if word in self.WELCOME_LIST:
                    result.append(self.MESSAGES['mode_command_processing_welcome']) # print('Режим 2.1. Приветствие.')
                    return result, data, 'welcome'
                elif word in self.GET_LIST:
                    result.append(self.MESSAGES['mode_command_processing_get']) # print('Режим 2.2. Получение данных.')
                    modifer_list = [] # хранилище под найденные модификаторы
                    for word in find_text: 
                        word = word.strip().lower()
                        modifer = self.modifer_detector(word) # определяем модификатор каждого слова
                        if modifer != ValueError: # если модификатор опредеен, то добавляем в список
                            modifer_list.append(modifer)
                    if len(modifer_list) == 0:
                        modifer_list.append('get_all')
                    get = modifer_list #[0]
                    return result, data, get
                elif word in self.CLEAR_LIST:
                    result.append(self.MESSAGES['mode_command_processing_clear']) # print('Режим 2.3. Удаление данных.')
                    return result, data, 'clear'
                elif word in self.CANCEL_LIST:
                    result.append(self.MESSAGES['mode_command_processing_cancel']) # print('Режим 2.3. Удаление данных.')
                    return result, data, 'cancel'
                elif word in self.CREATE_LINK_LIST:
                    data.append(find_digit[0])
                    result.append(self.MESSAGES['mode_command_processing_create_link']) # print('Режим 2.3. Удаление данных.')
                    return result, data, 'create_link'
                elif word in self.DROP_LINK_LIST:
                    data.append(find_digit[0])
                    result.append(self.MESSAGES['mode_command_processing_drop_link']) # print('Режим 2.3. Удаление данных.')
                    return result, data, 'drop_link'
                else:
                    result.append(self.MESSAGES['error_invalid_command'])
                    return result, ValueError, 'error'
        else:       
            result.append(self.MESSAGES['error_invalid_input_data'])
            return result, ValueError, 'error'