import random
import sqlite3
from tkinter import *
from jinja2 import Template
from tkinter.ttk import Combobox
import tkinter.messagebox as tkm
from os import path


def get_script_dir() -> str:
    """
    Функция собирающая абсолютный путь к текущей директории
    :return: возвращает этот путь
    """
    abs_path = path.abspath(__file__)  # полный путь к файлу скрипта
    return path.dirname(abs_path)


db_name = 'sqlite_rand_enc_db.sqlite3'
abspath = get_script_dir() + path.sep + db_name  # Формирование абсолютного пути для файла базы данных

db = sqlite3.connect(abspath)  # connect to sql base
cursor = db.cursor()  # Creation sqlite cursor


def terrain_func() -> list:  # This func need to create all terrain names to use them in tkinter combobox
    name_terrain = cursor.execute('SELECT terrain_name FROM terrain').fetchall()
    return name_terrain


terrains = [x[0] for x in terrain_func()]  # making normal list

type_enc = ('случайное событие',  # base type of events using in tkinter combobox
            'боевое событие',
            'значимое событие',
            'незначимое событие')

type_threat = ('0', '1', '2', '3', '4', '5')  # levels of threat using in tkinter threat comboboxes

danger_level = ('Нулевая угроза',  # levels of danger in zone
                'Красная угроза',
                'Фиолетовая угроза',
                'Синяя угроза',
                'Зеленая угроза')

# global dict with values by default. this is final result of tkinter class, using in sql-query
# значения по умолчанию None у террейна и сложности нужны, чтобы выбивать предупреждение о ошибке, если
# в интерфейсе их не выберут. Строковое значение у угроз поставил, потому что tkinter классы ругались на int-овый тип
tkinter_result = {'угроза орков': '0',  # Все параметры угрозы ниже отвечают за удельную силу врагов и могут
                  'угроза хаоситов': '0',  # варироваться от 0(полное отсутствие угрозы - ивенты невозможны) до 5
                  'угроза друкхари': '0',  # (максимальная сила врагов)
                  'угроза тиранидов': '0',
                  'угроза тау': '0',
                  'угроза некронов': '0',
                  'угроза мутантов': '0',
                  'угроза малых рас': '0',
                  'угроза дикой природы': '0',
                  'угроза стихийных бедствий': '0',
                  'угроза бандитов': '0',
                  'угроза мятежников': '0',
                  'угроза демонов': '0',
                  'террейн': None,  # Террейн отвечает за локацию, в которой будет происходить событие
                  'сложность': None,  # Сложность отвечает за общий уровень опастности зоны. Лучшая награда в опасных
                  'тип события': 'случайное событие',  # Тип события отвечает за ручную установку типа ивента
                  'общий бафф': 0,  # Общие бафы и дебафы вносят глобальные изменения в роллы кубиков для событий
                  'общий дебафф': 0,
                  'дебафф награды': 0,  # Бафы и дебьфы награды вносят изменения в роллы награды для боевых событий
                  'бафф награды': 0}


def sql_select(ttk_list: dict) -> str:
    """
    это основная функция создающая sql запрос и возвращающая его результат в текстовом виде для использования
    :return: она возвращает список из двух стобцов, показывающий имя ивента
    """
    enc_roll = random.randint(3, 18) + ttk_list['общий дебафф'] - ttk_list['общий бафф']
    # Роллы по системе GURPS не могут быть ниже 3 и выше 18 и бд рассчитана на такие значения
    if enc_roll > 18:
        enc_roll = 18
    if enc_roll < 3:
        enc_roll = 3

    #  все боевые события в бд идут плохих роллах(15-18) и при максимально хорошем, но с огромной наградой поэтому,
    # чтобы при ручном выборе боевого события не случился отбор нуля записей выставляется ограничение по выбору цифр
    if ttk_list['тип события'] == 'боевое событие':
        enc_roll = random.choice([3, 15, 16, 17, 18])

    # Создаю список из потенциальных угроз врагов(если угроза выше 0) для использования в шаблонизаторе для SQL-селекта
    enemy_for_select = [keys for keys in ttk_list if 'угроза' in keys and int(ttk_list[keys]) > 0]

    # Пустое значение по умолчананию для шаблонизатора. Если тип события будет отличным от случайного, то в SQL-запросе
    # появится еще один WHERE отбор, в ином случае вставить пустое значение и никакого отбора не будет, выводя все типы
    # возможных событий, дефакто это и есть случайное событие
    type_event = ''
    if ttk_list['тип события'] != 'случайное событие':
        temp = ttk_list['тип события']
        type_event = f'AND type_event.type_event_name == \'{temp}\''  # Строчка для вставки в цикр for ша

    # В данном селекте я выбираю название события(его сущность), тип события, враг, который характерен событию (для
    # небоевых событий враг устанавливается как 'Никто' и дополнительные особенности события помогающие мне его обыграть
    # как правило указываются примерные результаты критической удачи и неудачи как крайние случаи
    # В селекте, в блоке отборов WHERE используется шаблонизатор вставляющий параметры отборов. Отборы типа любой,
    # относятся к событиям, не привязанным к конкретным условиям и поэтому способными возникнуть в любых условиях,
    # например событие на любой планете или событие нечувствительное к уровню опастности зоны
    select_temp = Template('''
    SELECT DISTINCT main_event.name_event, type_event.type_event_name, enemies.enemy_name, main_event.text_event
    
    FROM main_event
    INNER JOIN event_terrain_relations ON main_event.name_event == event_terrain_relations.event_name
    INNER JOIN terrain ON event_terrain_relations.terrain_name == terrain.terrain_name
    INNER JOIN event_danger_relations ON main_event.name_event == event_danger_relations.event_name
    INNER JOIN danger_zone ON event_danger_relations.danger_name == danger_zone.danger_name
    INNER JOIN enemy_event_relations ON main_event.name_event == enemy_event_relations.event_name
    INNER JOIN enemies ON enemy_event_relations.enemy_name == enemies.enemy_name
    INNER JOIN event_luck ON main_event.luck_name == event_luck.luck_name
    INNER JOIN type_event ON main_event.type_event_name == type_event.type_event_name
    
    WHERE (terrain.terrain_name == '{{ terrain }}' OR terrain.terrain_name == 'Любой')
    AND event_luck.min_luck <= '{{ enc_roll }}' AND event_luck.max_luck >= '{{ enc_roll }}'
    AND (danger_zone.danger_name == '{{ danger_zone }}' OR danger_zone.danger_name == 'Любая угроза')
    AND (
    {% for enemy in enemies %}
        enemies.enemy_name == '{{ enemy }}' OR 
    {% endfor %}
        enemies.enemy_name == 'Никто')
    {{ type_event }} 
    ''')
    select_render = select_temp.render(terrain=ttk_list['террейн'],
                                       enc_roll=enc_roll,
                                       danger_zone=ttk_list['сложность'],
                                       enemies=enemy_for_select,
                                       type_event=type_event)
    return select_render


def create_list_for_randchoice(ttk_list: dict) -> dict:
    result_of_query = cursor.execute(
        sql_select(ttk_list)).fetchall()  # собираю все значения sql отбора и отображаю их все
    list_result_of_query = []  # список в который будут добавлять словари ключ: значение из sql-отбора
    for event in result_of_query:  # связываю результаты sql-отбора с названиями для ключей для отображения
        # Добавляю получившиеся связанные значения в список. Словарь нужен в т.ч. чтобы вносить далее изменения в него
        list_result_of_query.append(dict(zip(('суть события', 'тип события', 'связанные враги', 'доп.детали'), event)))

    # Ниже будут вноситься изменения в список для добавления большей информативности в отчет
    for event in list_result_of_query:
        # Условие необходимо, чтобы в словарь событий не попадали ключ-значения, которые не должны быть в небоевых
        # событиях, а именно сила врагов и лут с врагов т.к. в небоевых событиях врагов - нет
        if event['тип события'] == 'боевое событие':
            # Устанавливаю силу врагов с учетом результатов ГМ-ских чекбоксов на бафф и дебафф. Сила не может быть
            # меньше единицы(т.к. 0 это отсутствие врагов) и не может быть больше 5 т.к. это максимальная сила врагов
            value_for_dict_enemy = int(ttk_list[event['связанные враги']]) + ttk_list['общий дебафф'] - \
                                   ttk_list['общий бафф']
            event['сила врагов'] = value_for_dict_enemy
            if event['сила врагов'] < 1:
                event['сила врагов'] = 1
            if event['сила врагов'] > 5:
                event['сила врагов'] = 5

            value_for_dict_reward = random.randint(3, 18) + (ttk_list['дебафф награды'] * 2) - (
                    ttk_list['бафф награды'] * 2)
            event['лут с врагов и награда'] = value_for_dict_reward

        event['удачливость события'] = random.randint(3, 18) + (ttk_list['общий дебафф'] * 2) - (
                ttk_list['общий бафф'] * 2)
        # Согласно системе GURPS, под которую сделан данный скрипт, 3 и 18 - крайние значения бросков кубика поэтому
        # Если при роллах с ГМ-кими кнопками значение будет выше или ниже нужно их подкорректировать
        if event['удачливость события'] < 3:
            event['удачливость события'] = 3
        if event['удачливость события'] > 18:
            event['удачливость события'] = 18
    # Окончательный выбор события из списка потенциальных событий с проброшенными кубиками. По хорошему нужно довести
    # количество потенциальных роллов событий хотябы до 15-20, чтобы события на одной локации с одниноковыми исходными
    # данными не повторялись
    rand_select = random.choice(list_result_of_query)

    return rand_select


def start() -> None:
    """
    Данная функция управляет и соединяет 4 основных этапы работы и начинает выполняться при нажатии кнопки START.
    Этапы разделены пробелами
    """
    global tkinter_result

    # Первый этап. Проверка на полную и корректную заполненность данных

    # Без выбора сложности и террайна - нельзя
    if not tkinter_result['сложность'] or not tkinter_result['террейн']:
        tkm.showwarning('Неполные данные', 'Нужно заполнить\nМесто действия и\nуровень угрозы')
    # Выбирать одновременно нулевую игрозу и боевое событие - нельзя т.к. результат будет пустой
    elif tkinter_result['сложность'] == 'Нулевая угроза' and tkinter_result['тип события'] == 'боевое событие':
        tkm.showwarning('Конфликт выбора', 'Нельзя одновременно\nвыбирать нулевую\nугрозу и\nбоевое событие')
    # На опустошенном мире нет строгих боевых действий, боевые конфликты уникальные и не будут с тегом боевого действия
    elif tkinter_result['террейн'] == 'Опустошенный мир' and tkinter_result['тип события'] == 'боевое событие':
        tkm.showwarning('Конфликт выбора', 'Нельзя одновременно\nвыбирать опустошенный мир\nи боевое событие')

    else:
        # Второй этап. Окончательное формирование словаря на основе выборов из графического интерфеса
        check_buttons()  # Чекбоксы добавляются в самом конце после START-а, остальной словарь заполняется до этого
        table_obj.quit()  # Закрытие первоначального интерфейса

        # Третий этап. Создание на основе словаря sql-запроса, а затем выбор случайного события
        text_res = create_list_for_randchoice(tkinter_result)

        # Четвертый этап. Формирование текстового графического отображения результатов случайного события и
        # выведение его на экран. Конструкция name-main нужна, чтобы при тестировании отборов не выполнялось отображение
        if __name__ == '__main__':
            win2 = Tk()
            output = Text(win2)
            for string in text_res:  # Добавление построчно с разделением в 2 пробела результатов ивента в текст. поле
                output.insert(INSERT, f'{str(string)} : {str(text_res[string])}\n\n')  # добавление вида ключ:значение
            output.pack()
            win2.mainloop()


def add_button_result_to_dict(event, button: str, combobox_name: str) -> None:
    """Данная функция добавляет результаты кнопок(все комбобоксы) в глобальный словарь результатов работы интерфейса
    :param event: стандартный аргумент под параметр command классов tkinter, не функции не используется
    :param button: строковое название кнопки
    :param combobox_name: строковое название метода, который будет использоваться для get-метода комбобокса
    :return: None
    """
    global tkinter_result

    # Вызываю метод необходимого аттрибута, который возвращает мне нужное значение
    dict_res = table_obj.universal_get(combobox_name)

    # Добавляю или изменяю в глобальном словаре tkinter_result вложенные словари в котором ключ это переданный аргумент
    # button, а значение это результат того, что вернулось из методов result-методов и дефакто является выбранным в
    # интерфейсе значениями
    tkinter_result[button] = dict_res


def check_buttons() -> None:
    """
    Данная функция собирает значения чекбоксов и добавляет их в глобальный список результата работы интерфейса
    :return: None
    """
    global tkinter_result
    tkinter_result['первый игрок'] = table_obj.user1_status.get()
    tkinter_result['второй игрок'] = table_obj.user2_status.get()
    tkinter_result['третий игрок'] = table_obj.user3_status.get()
    tkinter_result['четвертый игрок'] = table_obj.user4_status.get()
    tkinter_result['пятый игрок'] = table_obj.user5_status.get()

    tkinter_result['общий дебафф'] = table_obj.debuff1_status.get()
    tkinter_result['общий бафф'] = table_obj.buff1_status.get()

    tkinter_result['дебафф награды'] = table_obj.debuff2_status.get()
    tkinter_result['бафф награды'] = table_obj.buff2_status.get()


class App(Frame):
    """
    Основной класс графического интерфейса tkinter котором будут выбираться значения для будущего рандомного
    выбора события. Все значения, за исключением чекбоксов, сразу после выбора записываются в итоговый словарь,
    с которым будет идти работа на дальнейших этапах работы приложения. В __init__ методе прописаны сами кнопки и
    вызовы их методов////////////////////////////////сделать рефакторинг и закинуть в отдельные методы кнопки

    Ниже идут get-методы собирающие значения для словаря
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.win = parent

        """ 
        Базовые параметры устанавливающие размеры окна в пикселях и заголовок приложения
        """
        self.geom = self.win.geometry('700x250')
        self.title = self.win.title('Рандомайзер случайных событий ролки WH40k')

        """
        Кнопка старта
        """
        self.start_button = Button(self.win, text='START', command=start)
        self.start_button.place(relwidth=0.2, relheight=0.2, relx=0.4, rely=0.5)

        """
        Кнопка выбора зоны события
        """
        self.ter_name = Label(self.win, text='Выберите место действия')
        self.ter_name.place(relwidth=0.2, relheight=0.1, relx=0.001, rely=0.0)
        self.terrain_combo = Combobox(self.win, values=terrains)
        self.terrain_combo.bind('<<ComboboxSelected>>',
                                lambda event: add_button_result_to_dict(event,
                                                                        'террейн',
                                                                        'terrain_combo'))
        self.terrain_combo.place(relwidth=0.2, relheight=0.1, relx=0.001, rely=0.1)

        """
        Кнопка выбора опастности зоны
        """
        self.dang_name = Label(self.win, text='Выберите опастность зоны')
        self.dang_name.place(relx=0.78, rely=0)
        self.danger_combo = Combobox(self.win, values=danger_level)
        self.danger_combo.bind('<<ComboboxSelected>>',
                               lambda event: add_button_result_to_dict(event,
                                                                       'сложность',
                                                                       'danger_combo'))
        self.danger_combo.place(relwidth=0.2, relheight=0.1, relx=0.799, rely=0.1)

        '''
        Кнопка определяющая тип проиходимого события
        '''
        self.type_name = Label(self.win, text='Выберите тип события')
        self.type_name.place(relx=0.8, rely=0.6)
        self.type_combo = Combobox(self.win, values=type_enc)
        self.type_combo.current(0)
        self.type_combo.bind('<<ComboboxSelected>>',
                             lambda event: add_button_result_to_dict(event,
                                                                     'тип события',
                                                                     'type_combo'))
        self.type_combo.place(relwidth=0.2, relheight=0.1, relx=0.799, rely=0.7)

        '''
        Плашка угроз
        '''
        self.threat = Label(self.win, text='Степень угрозы:')
        self.threat.place(relx=0.44, rely=0)

        '''
        Кнопка определяющая степень угрозы орков на местности
        '''
        self.orcs_threat_name = Label(self.win, text='Орки')
        self.orcs_threat_name.place(relx=0.24, rely=0.08)
        self.orcs_threat_combo = Combobox(self.win, values=type_threat)
        self.orcs_threat_combo.current(0)
        self.orcs_threat_combo.bind('<<ComboboxSelected>>',
                                    lambda event: add_button_result_to_dict(event,
                                                                            'угроза орков',
                                                                            'orcs_threat_combo'))
        self.orcs_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.24, rely=0.18)

        '''
        Кнопка определяющая степень угрозы хаоса на местности
        '''
        self.chaos_threat_name = Label(self.win, text='Хаоситы')
        self.chaos_threat_name.place(relx=0.34, rely=0.08)
        self.chaos_threat_combo = Combobox(self.win, values=type_threat)
        self.chaos_threat_combo.current(0)
        self.chaos_threat_combo.bind('<<ComboboxSelected>>',
                                     lambda event: add_button_result_to_dict(event,
                                                                             'угроза хаоситов',
                                                                             'chaos_threat_combo'))
        self.chaos_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.345, rely=0.18)

        '''
        Кнопка определяющая степень угрозы друкхари на местности
        '''
        self.t_elves_threat_name = Label(self.win, text='Друкхари')
        self.t_elves_threat_name.place(relx=0.445, rely=0.08)
        self.t_elves_threat_combo = Combobox(self.win, values=type_threat)
        self.t_elves_threat_combo.current(0)
        self.t_elves_threat_combo.bind('<<ComboboxSelected>>',
                                       lambda event: add_button_result_to_dict(event,
                                                                               'угроза друкхари',
                                                                               't_elves_threat_combo'))
        self.t_elves_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.45, rely=0.18)

        '''
        Кнопка определяющая степень угрозы тиранидов на местности
        '''
        self.tyranids_threat_name = Label(self.win, text='Тираниды')
        self.tyranids_threat_name.place(relx=0.545, rely=0.08)
        self.tyranids_threat_combo = Combobox(self.win, values=type_threat)
        self.tyranids_threat_combo.current(0)
        self.tyranids_threat_combo.bind('<<ComboboxSelected>>',
                                        lambda event: add_button_result_to_dict(event,
                                                                                'угроза тиранидов',
                                                                                'tyranids_threat_combo'))
        self.tyranids_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.555, rely=0.18)

        '''
        Кнопка определяющая степень угрозы тау на местности
        '''
        self.tau_threat_name = Label(self.win, text='Тау')
        self.tau_threat_name.place(relx=0.65, rely=0.08)
        self.tau_threat_combo = Combobox(self.win, values=type_threat)
        self.tau_threat_combo.current(0)
        self.tau_threat_combo.bind('<<ComboboxSelected>>',
                                   lambda event: add_button_result_to_dict(event,
                                                                           'угроза тау',
                                                                           'tau_threat_combo'))
        self.tau_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.66, rely=0.18)

        '''
        Кнопка определяющая степень угрозы некронов на местности
        '''
        self.necrons_threat_name = Label(self.win, text='Некроны')
        self.necrons_threat_name.place(relx=0.24, rely=0.3)
        self.necrons_threat_combo = Combobox(self.win, values=type_threat)
        self.necrons_threat_combo.current(0)
        self.necrons_threat_combo.bind('<<ComboboxSelected>>',
                                       lambda event: add_button_result_to_dict(event,
                                                                               'угроза некронов',
                                                                               'necrons_threat_combo'))
        self.necrons_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.24, rely=0.38)

        '''
        Кнопка определяющая степень угрозы мутантов на местности
        '''
        self.mutants_threat_name = Label(self.win, text='Мутанты')
        self.mutants_threat_name.place(relx=0.34, rely=0.3)
        self.mutants_threat_combo = Combobox(self.win, values=type_threat)
        self.mutants_threat_combo.current(0)
        self.mutants_threat_combo.bind('<<ComboboxSelected>>',
                                       lambda event: add_button_result_to_dict(event,
                                                                               'угроза мутантов',
                                                                               'mutants_threat_combo'))
        self.mutants_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.345, rely=0.38)

        '''
        Кнопка определяющая степень угрозы малых фракций на местности
        '''
        self.small_races_threat_name = Label(self.win, text='Малые расы')
        self.small_races_threat_name.place(relx=0.443, rely=0.3)
        self.small_races_threat_combo = Combobox(self.win, values=type_threat)
        self.small_races_threat_combo.current(0)
        self.small_races_threat_combo.bind('<<ComboboxSelected>>',
                                           lambda event: add_button_result_to_dict(event,
                                                                                   'угроза малых рас',
                                                                                   'small_races_threat_combo'))
        self.small_races_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.45, rely=0.38)

        '''
        Кнопка определяющая степень угрозы дикой природы на местности
        '''
        self.wild_threat_name = Label(self.win, text='Дикие звери')
        self.wild_threat_name.place(relx=0.55, rely=0.3)
        self.wild_threat_combo = Combobox(self.win, values=type_threat)
        self.wild_threat_combo.current(0)
        self.wild_threat_combo.bind('<<ComboboxSelected>>',
                                    lambda event: add_button_result_to_dict(event,
                                                                            'угроза дикой природы',
                                                                            'wild_threat_combo'))
        self.wild_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.555, rely=0.38)

        '''
        Кнопка определяющая степень угрозы стихийных бедствий на местности
        '''
        self.disaster_threat_name = Label(self.win, text='Бедствия')
        self.disaster_threat_name.place(relx=0.657, rely=0.3)
        self.disaster_threat_combo = Combobox(self.win, values=type_threat)
        self.disaster_threat_combo.current(0)
        self.disaster_threat_combo.bind('<<ComboboxSelected>>',
                                        lambda event: add_button_result_to_dict(event,
                                                                                'угроза стихийных бедствий',
                                                                                'disaster_threat_combo'))
        self.disaster_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.66, rely=0.38)

        '''
        Кнопка определяющая степень угрозы бандитов на местности
        '''
        self.bandits_threat_name = Label(self.win, text='Бандиты')
        self.bandits_threat_name.place(relx=0.76, rely=0.3)
        self.bandits_threat_combo = Combobox(self.win, values=type_threat)
        self.bandits_threat_combo.current(0)
        self.bandits_threat_combo.bind('<<ComboboxSelected>>',
                                       lambda event: add_button_result_to_dict(event,
                                                                               'угроза бандитов',
                                                                               'bandits_threat_combo'))
        self.bandits_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.765, rely=0.38)

        '''
        Кнопка определяющая степень угрозы мятежников на местности
        '''
        self.rebels_threat_name = Label(self.win, text='Мятежники')
        self.rebels_threat_name.place(relx=0.6, rely=0.48)
        self.rebels_threat_combo = Combobox(self.win, values=type_threat)
        self.rebels_threat_combo.current(0)
        self.rebels_threat_combo.bind('<<ComboboxSelected>>',
                                      lambda event: add_button_result_to_dict(event,
                                                                              'угроза мятежников',
                                                                              'rebels_threat_combo'))
        self.rebels_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.605, rely=0.56)

        '''
        Кнопка определяющая степень угрозы демонов на местности
        '''
        self.demons_threat_name = Label(self.win, text='Демоны')
        self.demons_threat_name.place(relx=0.295, rely=0.48)
        self.demons_threat_combo = Combobox(self.win, values=type_threat)
        self.demons_threat_combo.current(0)
        self.demons_threat_combo.bind('<<ComboboxSelected>>',
                                      lambda event: add_button_result_to_dict(event,
                                                                              'угроза демонов',
                                                                              'demons_threat_combo'))
        self.demons_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.295, rely=0.56)

        """
        Кнопки участвующих в событии игроков
        """
        self.user_lab = Label(self.win, text='Участвующие игроки')
        self.user_lab.place(relx=0, rely=0.3)

        self.user1_status = IntVar()
        self.user1 = Checkbutton(self.win, text='Первый', variable=self.user1_status)
        self.user1.place(relx=0, rely=0.4)

        self.user2_status = IntVar()
        self.user2 = Checkbutton(self.win, text='Второй', variable=self.user2_status)
        self.user2.place(relx=0, rely=0.5)

        self.user3_status = IntVar()
        self.user3 = Checkbutton(self.win, text='Третий', variable=self.user3_status)
        self.user3.place(relx=0, rely=0.6)

        self.user4_status = IntVar()
        self.user4 = Checkbutton(self.win, text='Четвертый', variable=self.user4_status)
        self.user4.place(relx=0, rely=0.7)

        self.user5_status = IntVar()
        self.user5 = Checkbutton(self.win, text='Пятый', variable=self.user5_status)
        self.user5.place(relx=0, rely=0.8)

        """
        Кнопки, позволяющие ГМу вносить изменения, улучшающие или ухудшающие результат события
        """
        self.gm_lab = Label(self.win, text='ГМ-ские кнопки, вносящие корректировки в броски кубика')
        self.gm_lab.place(relx=0.3, rely=0.8)

        self.debuff1_status = IntVar()
        self.debuff1 = Checkbutton(self.win, text='Орг серит', variable=self.debuff1_status)
        self.debuff1.place(relx=0.15, rely=0.9)

        self.buff1_status = IntVar()
        self.buff1 = Checkbutton(self.win, text='Орг помогает', variable=self.buff1_status)
        self.buff1.place(relx=0.35, rely=0.9)

        self.debuff2_status = IntVar()
        self.debuff2 = Checkbutton(self.win, text='Душная награда', variable=self.debuff2_status)
        self.debuff2.place(relx=0.55, rely=0.9)

        self.buff2_status = IntVar()
        self.buff2 = Checkbutton(self.win, text='Щедрая награда', variable=self.buff2_status)
        self.buff2.place(relx=0.75, rely=0.9)

    def quit(self) -> None:
        """Метод уничтожающий экзепляр интерфейса после нажатия кнопки START"""
        self.win.destroy()

    @staticmethod
    def universal_get(get_name: str):
        """
        Функция вызывает метод get для комбобоксов, чтобы получить результаты их выборов
        :param get_name: строковое название конкретного комбобокса, которому будет вызываться метод
        :return: вызов функции get для получения итогового результата выбора combobox
        """
        combo_name = table_obj.__getattribute__(get_name)
        return combo_name.get()


if __name__ == "__main__":
    win = Tk()
    table_obj = App(win)  # Экземпляр класса Frame библиотеки tkinter в котором работает первая стадия работы скрипта
    win.mainloop()
