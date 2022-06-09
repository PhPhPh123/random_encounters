import random
import json
import sqlite3
from tkinter import *
from jinja2 import Template
from tkinter.ttk import Combobox

db = sqlite3.connect('sqlite_rand_enc_db.sqlite3')  # connect to sql base
cursor = db.cursor()  # Creation sqlite cursor


def terrain_func():  # This func need to create all terrain names to use them in tkinter combobox
    name_terrain = cursor.execute('SELECT terrain_name FROM terrain').fetchall()
    return name_terrain


db_terrain_list = terrain_func()  # tuples after sql query
terrains = [x[0] for x in db_terrain_list]  # making normal list

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
tkinter_result = {'угроза орков': '0', 'угроза хаоситов': '0', 'угроза друкхари': '0',
                  'угроза тиранидов': '0', 'угроза тау': '0', 'угроза некронов': '0',
                  'угроза мутантов': '0', 'угроза малых рас': '0', 'угроза дикой природы': '0',
                  'угроза стихийных бедствий': '0', 'угроза бандитов': '0', 'угроза мятежников': '0',
                  'угроза демонов': '0', 'террейн': None, 'сложность': None, 'тип события': 'случайное событие',
                  'общий бафф': 0, 'общий дебафф': 0, 'дебафф награды': 0, 'бафф награды': 0}


'''
это основная функция создающая sql запрос и возвращающая его результат в текстовом виде для использования
она возвращает список из двух стобцов, показывающий имя ивента
'''


def sqlselect():
    global tkinter_result
    enc_roll = random.randint(15, 18) + tkinter_result['общий дебафф'] - tkinter_result['общий бафф']
    if enc_roll > 18:
        enc_roll = 18
    if enc_roll < 3:
        enc_roll = 3

    if tkinter_result['тип события'] == 'боевое событие':
        enc_roll = random.randint(15, 18)

    enemy_for_select = [keys for keys in tkinter_result if 'угроза' in keys and int(tkinter_result[keys]) > 0]

    type_event = ''
    if tkinter_result['тип события'] != 'случайное событие':
        temp = tkinter_result['тип события']
        type_event = f'AND type_event.type_event_name == \'{temp}\''

    select_temp = Template('''
    SELECT DISTINCT main_event.name_event, enemies.enemy_name
    
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
    select_render = select_temp.render(terrain=tkinter_result['террейн'],
                                       enc_roll=enc_roll,
                                       danger_zone=tkinter_result['сложность'],
                                       enemies=enemy_for_select,
                                       type_event=type_event)
    print(select_render)
    return select_render


def create_list_for_randchoice():
    global tkinter_result
    result_of_query = cursor.execute(sqlselect()).fetchall()
    list_result_of_query = []
    print(result_of_query)
    for event in result_of_query:
        list_result_of_query.append(dict(zip(('суть ивента', 'связанные враги'), event)))

    for event in list_result_of_query:
        if event['связанные враги'] != 'Никто':
            value_for_dict_enemy = int(tkinter_result[event['связанные враги']]) + tkinter_result['общий дебафф'] - \
                                   tkinter_result['общий бафф']
            event['сила врагов'] = value_for_dict_enemy

            value_for_dict_reward = random.randint(3, 18) + (tkinter_result['дебафф награды'] * 2) - (
                    tkinter_result['бафф награды'] * 2)
            event['лут с врагов и награда'] = value_for_dict_reward

        event['удачливость события'] = random.randint(3, 18) + (tkinter_result['общий дебафф'] * 2) - (
                tkinter_result['общий бафф'] * 2)
        if event['удачливость события'] < 3:
            event['удачливость события'] = 3
        if event['удачливость события'] > 18:
            event['удачливость события'] = 18

    rand_select = random.choice(list_result_of_query)

    return rand_select


def start():
    global tkinter_result
    checkbuttons()
    table_obj.quit()
    text_res = create_list_for_randchoice()

    win2 = Tk()
    output = Text(win2)
    output.insert(INSERT, str(text_res))
    output.pack()
    win2.mainloop()


def add_button_result_to_dict(event, button, method_name):
    global tkinter_result
    result = table_obj.__getattribute__(method_name)
    dict_res = result()
    tkinter_result[button] = dict_res


def checkbuttons():
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
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.win = parent

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
                                lambda event: add_button_result_to_dict(event, 'террейн', 'terrain_result'))
        self.terrain_combo.place(relwidth=0.2, relheight=0.1, relx=0.001, rely=0.1)

        """
        Кнопка выбора опастности зоны
        """
        self.dang_name = Label(self.win, text='Выберите опастность зоны')
        self.dang_name.place(relx=0.78, rely=0)
        self.danger_combo = Combobox(self.win, values=danger_level)
        self.danger_combo.bind('<<ComboboxSelected>>',
                               lambda event: add_button_result_to_dict(event, 'сложность', 'danger_result'))
        self.danger_combo.place(relwidth=0.2, relheight=0.1, relx=0.799, rely=0.1)

        '''
        Кнопка определяющая тип проиходимого события
        '''
        self.type_name = Label(self.win, text='Выберите тип события')
        self.type_name.place(relx=0.8, rely=0.6)
        self.type_combo = Combobox(self.win, values=type_enc)
        self.type_combo.current(0)
        self.type_combo.bind('<<ComboboxSelected>>',
                             lambda event: add_button_result_to_dict(event, 'тип события', 'type_result'))
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
                                    lambda event: add_button_result_to_dict(event, 'угроза орков',
                                                                            'orcs_threat_result'))
        self.orcs_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.24, rely=0.18)

        '''
        Кнопка определяющая степень угрозы хаоса на местности
        '''
        self.chaos_threat_name = Label(self.win, text='Хаоситы')
        self.chaos_threat_name.place(relx=0.34, rely=0.08)
        self.chaos_threat_combo = Combobox(self.win, values=type_threat)
        self.chaos_threat_combo.current(0)
        self.chaos_threat_combo.bind('<<ComboboxSelected>>',
                                     lambda event: add_button_result_to_dict(event, 'угроза хаоситов',
                                                                             'chaos_threat_result'))
        self.chaos_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.345, rely=0.18)

        '''
        Кнопка определяющая степень угрозы друкхари на местности
        '''
        self.t_elves_threat_name = Label(self.win, text='Друкхари')
        self.t_elves_threat_name.place(relx=0.445, rely=0.08)
        self.t_elves_threat_combo = Combobox(self.win, values=type_threat)
        self.t_elves_threat_combo.current(0)
        self.t_elves_threat_combo.bind('<<ComboboxSelected>>',
                                       lambda event: add_button_result_to_dict(event, 'угроза друкхари',
                                                                               't_elves_threat_result'))
        self.t_elves_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.45, rely=0.18)

        '''
        Кнопка определяющая степень угрозы тиранидов на местности
        '''
        self.tyranids_threat_name = Label(self.win, text='Тираниды')
        self.tyranids_threat_name.place(relx=0.545, rely=0.08)
        self.tyranids_threat_combo = Combobox(self.win, values=type_threat)
        self.tyranids_threat_combo.current(0)
        self.tyranids_threat_combo.bind('<<ComboboxSelected>>',
                                        lambda event: add_button_result_to_dict(event, 'угроза тиранидов',
                                                                                'tyranids_threat_result'))
        self.tyranids_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.555, rely=0.18)

        '''
        Кнопка определяющая степень угрозы тау на местности
        '''
        self.tau_threat_name = Label(self.win, text='Тау')
        self.tau_threat_name.place(relx=0.65, rely=0.08)
        self.tau_threat_combo = Combobox(self.win, values=type_threat)
        self.tau_threat_combo.current(0)
        self.tau_threat_combo.bind('<<ComboboxSelected>>',
                                   lambda event: add_button_result_to_dict(event, 'угроза тау',
                                                                           'tau_threat_result'))
        self.tau_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.66, rely=0.18)

        '''
        Кнопка определяющая степень угрозы некронов на местности
        '''
        self.necrons_threat_name = Label(self.win, text='Некроны')
        self.necrons_threat_name.place(relx=0.24, rely=0.3)
        self.necrons_threat_combo = Combobox(self.win, values=type_threat)
        self.necrons_threat_combo.current(0)
        self.necrons_threat_combo.bind('<<ComboboxSelected>>',
                                       lambda event: add_button_result_to_dict(event, 'угроза некронов',
                                                                               'necrons_threat_result'))
        self.necrons_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.24, rely=0.38)

        '''
        Кнопка определяющая степень угрозы мутантов на местности
        '''
        self.mutants_threat_name = Label(self.win, text='Мутанты')
        self.mutants_threat_name.place(relx=0.34, rely=0.3)
        self.mutants_threat_combo = Combobox(self.win, values=type_threat)
        self.mutants_threat_combo.current(0)
        self.mutants_threat_combo.bind('<<ComboboxSelected>>',
                                       lambda event: add_button_result_to_dict(event, 'угроза мутантов',
                                                                               'mutants_threat_result'))
        self.mutants_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.345, rely=0.38)

        '''
        Кнопка определяющая степень угрозы малых фракций на местности
        '''
        self.small_races_threat_name = Label(self.win, text='Малые расы')
        self.small_races_threat_name.place(relx=0.443, rely=0.3)
        self.small_races_threat_combo = Combobox(self.win, values=type_threat)
        self.small_races_threat_combo.current(0)
        self.small_races_threat_combo.bind('<<ComboboxSelected>>',
                                           lambda event: add_button_result_to_dict(event, 'угроза малых рас',
                                                                                   'small_races_threat_result'))
        self.small_races_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.45, rely=0.38)

        '''
        Кнопка определяющая степень угрозы дикой природы на местности
        '''
        self.wild_threat_name = Label(self.win, text='Дикие звери')
        self.wild_threat_name.place(relx=0.55, rely=0.3)
        self.wild_threat_combo = Combobox(self.win, values=type_threat)
        self.wild_threat_combo.current(0)
        self.wild_threat_combo.bind('<<ComboboxSelected>>',
                                    lambda event: add_button_result_to_dict(event, 'угроза дикой природы',
                                                                            'wild_threat_result'))
        self.wild_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.555, rely=0.38)

        '''
        Кнопка определяющая степень угрозы стихийных бедствий на местности
        '''
        self.disaster_threat_name = Label(self.win, text='Бедствия')
        self.disaster_threat_name.place(relx=0.657, rely=0.3)
        self.disaster_threat_combo = Combobox(self.win, values=type_threat)
        self.disaster_threat_combo.current(0)
        self.disaster_threat_combo.bind('<<ComboboxSelected>>',
                                        lambda event: add_button_result_to_dict(event, 'угроза стихийных бедствий',
                                                                                'disaster_threat_result'))
        self.disaster_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.66, rely=0.38)

        '''
        Кнопка определяющая степень угрозы стихийных бедствий на местности
        '''
        self.bandits_threat_name = Label(self.win, text='Бандиты')
        self.bandits_threat_name.place(relx=0.76, rely=0.3)
        self.bandits_threat_combo = Combobox(self.win, values=type_threat)
        self.bandits_threat_combo.current(0)
        self.bandits_threat_combo.bind('<<ComboboxSelected>>',
                                       lambda event: add_button_result_to_dict(event, 'угроза бандитов',
                                                                               'bandits_threat_result'))
        self.bandits_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.765, rely=0.38)

        '''
        Кнопка определяющая степень угрозы стихийных бедствий на местности
        '''
        self.rebels_threat_name = Label(self.win, text='Мятежники')
        self.rebels_threat_name.place(relx=0.6, rely=0.48)
        self.rebels_threat_combo = Combobox(self.win, values=type_threat)
        self.rebels_threat_combo.current(0)
        self.rebels_threat_combo.bind('<<ComboboxSelected>>',
                                      lambda event: add_button_result_to_dict(event, 'угроза мятежников',
                                                                              'rebels_threat_result'))
        self.rebels_threat_combo.place(relwidth=0.1, relheight=0.1, relx=0.605, rely=0.56)

        '''
        Кнопка определяющая степень угрозы стихийных бедствий на местности
        '''
        self.demons_threat_name = Label(self.win, text='Демоны')
        self.demons_threat_name.place(relx=0.295, rely=0.48)
        self.demons_threat_combo = Combobox(self.win, values=type_threat)
        self.demons_threat_combo.current(0)
        self.demons_threat_combo.bind('<<ComboboxSelected>>',
                                      lambda event: add_button_result_to_dict(event, 'угроза демонов',
                                                                              'demons_threat_result'))
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

        """
        Текстовое поле, в которое выводятся результаты ивента
        """

    def terrain_result(self):
        return self.terrain_combo.get()

    def danger_result(self):
        return self.danger_combo.get()

    def type_result(self):
        return self.type_combo.get()

    def orcs_threat_result(self):
        return self.orcs_threat_combo.get()

    def chaos_threat_result(self):
        return self.chaos_threat_combo.get()

    def t_elves_threat_result(self):
        return self.t_elves_threat_combo.get()

    def tyranids_threat_result(self):
        return self.tyranids_threat_combo.get()

    def tau_threat_result(self):
        return self.tau_threat_combo.get()

    def necrons_threat_result(self):
        return self.necrons_threat_combo.get()

    def mutants_threat_result(self):
        return self.mutants_threat_combo.get()

    def small_races_threat_result(self):
        return self.small_races_threat_combo.get()

    def wild_threat_result(self):
        return self.wild_threat_combo.get()

    def disaster_threat_result(self):
        return self.disaster_threat_combo.get()

    def bandits_threat_result(self):
        return self.bandits_threat_combo.get()

    def rebels_threat_result(self):
        return self.rebels_threat_combo.get()

    def demons_threat_result(self):
        return self.demons_threat_combo.get()

    def quit(self):
        self.win.destroy()


if __name__ == "__main__":
    win = Tk()
    table_obj = App(win)
    win.mainloop()
