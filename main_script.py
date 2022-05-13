from random import randint, choice, choices
import json
import sqlite3
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox

terrains = ('пустыня',
            'город-улей',
            'имперский городок',
            'имперские руины',
            'тундра',
            "ледяная пустошь")

danger_level = ('красная угроза',
                'фиолетовая угроза',
                'синяя угроза',
                'зеленая угроза',
                'неизвестная угроза')

type_enc = ('боевое событие',
            'значимое событие',
            'незначимое событие',
            'случайное событие')

tkinter_result = dict()


def start(event):
    print("123")


def add_button_result_to_dict(event, button):
    global tkinter_result
    print(button)
    if button == 'террейн':
        res = table_obj.terrain_result()
        tkinter_result['террейн'] = res

    if button == 'сложность':
        res = table_obj.danger_result()
        tkinter_result['сложность'] = res

    if button == 'тип события':
        res = table_obj.type_result()
        tkinter_result['тип события'] = res

    print(tkinter_result)


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
        self.start_button.place(relwidth=0.2, relheight=0.2, relx=0.4, rely=0.4)

        """
        Кнопка выбора зоны события
        """
        self.ter_name = Label(self.win, text='Выберите место действия')
        self.ter_name.place(relwidth=0.2, relheight=0.1, relx=0.001, rely=0.0)
        self.terrain_combo = Combobox(self.win, values=terrains)
        self.terrain_combo.bind('<<ComboboxSelected>>', lambda event: add_button_result_to_dict(event, 'террейн'))
        self.terrain_combo.place(relwidth=0.2, relheight=0.1, relx=0.001, rely=0.1)

        """
        Кнопка выбора опастности зоны
        """
        self.dang_name = Label(self.win, text='Выберите опастность зоны')
        self.dang_name.place(relx=0.78, rely=0)
        self.danger_combo = Combobox(self.win, values=danger_level)
        self.danger_combo.bind('<<ComboboxSelected>>', lambda event: add_button_result_to_dict(event, 'сложность'))
        self.danger_combo.place(relwidth=0.2, relheight=0.1, relx=0.799, rely=0.1)

        '''
        Кнопка определяющая тип проиходимого события
        '''
        self.type_name = Label(self.win, text='Выберите тип события')
        self.type_name.place(relx=0.8, rely=0.6)
        self.type_combo = Combobox(self.win, values=type_enc)
        self.type_combo.bind('<<ComboboxSelected>>', lambda event: add_button_result_to_dict(event, 'тип события'))
        self.type_combo.place(relwidth=0.2, relheight=0.1, relx=0.799, rely=0.7)

        """
        Кнопки участвующих в событии игроков
        """
        self.user_lab = Label(self.win, text='Участвующие игроки')
        self.user_lab.place(relx=0, rely=0.3)

        self.user1 = Checkbutton(self.win, text='Первый')
        self.user1.place(relx=0, rely=0.4)

        self.user2 = Checkbutton(self.win, text='Второй')
        self.user2.place(relx=0, rely=0.5)

        self.user3 = Checkbutton(self.win, text='Третий')
        self.user3.place(relx=0, rely=0.6)

        self.user4 = Checkbutton(self.win, text='Четвертый')
        self.user4.place(relx=0, rely=0.7)

        self.user5 = Checkbutton(self.win, text='Пятый')
        self.user5.place(relx=0, rely=0.8)

        """
        Кнопки, позволяющие ГМу вносить изменения, улучшающие или ухудшающие результат события
        """
        self.gm_lab = Label(self.win, text='Кнопки, серящие или мошнящие под игроков')
        self.gm_lab.place(relx=0.3, rely=0.8)

        self.debuff1 = Checkbutton(self.win, text='Орг серит')
        self.debuff1.place(relx=0.15, rely=0.9)

        self.buff1 = Checkbutton(self.win, text='Орг помогает')
        self.buff1.place(relx=0.35, rely=0.9)

        self.debuff2 = Checkbutton(self.win, text='Душная награда')
        self.debuff2.place(relx=0.55, rely=0.9)

        self.buff2 = Checkbutton(self.win, text='Щедрая награда')
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

    def quit(self):
        self.win.destroy()


if __name__ == "__main__":
    win = Tk()
    table_obj = App(win)
    win.mainloop()
