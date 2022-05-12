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


class App:
    def __init__(self):
        self.win = Tk()
        self.geom = self.win.geometry('700x250')
        self.title = self.win.title('Рандомайзер случайных событий ролки WH40k')

        """
        Кнопка старта
        """
        self.start_button = Button(self.win, text='START').place(relwidth=0.2, relheight=0.2, relx=0.4, rely=0.4)

        """
        Кнопка выбора зоны события
        """
        self.ter_name = Label(self.win, text='Выберите место действия').place(relwidth=0.2, relheight=0.1,
                                                                              relx=0.001, rely=0.0)
        self.terrain_combo = Combobox(self.win, values=terrains).place(relwidth=0.2, relheight=0.1,
                                                                       relx=0.001, rely=0.1)
        """
        Кнопка выбора опастности зоны
        """
        self.dang_name = Label(self.win, text='Выберите опастность зоны').place(relx=0.78, rely=0)
        self.danger_combo = Combobox(self.win, values=danger_level).place(relwidth=0.2, relheight=0.1,
                                                                          relx=0.799, rely=0.1)
        """
        Кнопки участвующих в событии игроков
        """
        self.user_lab = Label(self.win, text='Участвующие игроки').place(relx=0, rely=0.3)
        self.user1 = Checkbutton(self.win, text='Первый').place(relx=0, rely=0.4)
        self.user2 = Checkbutton(self.win, text='Второй').place(relx=0, rely=0.5)
        self.user3 = Checkbutton(self.win, text='Третий').place(relx=0, rely=0.6)
        self.user4 = Checkbutton(self.win, text='Четвертый').place(relx=0, rely=0.7)
        self.user5 = Checkbutton(self.win, text='Пятый').place(relx=0, rely=0.8)

        '''
        Кнопка определяющая тип проиходимого события
        '''
        self.type_name = Label(self.win, text='Выберите тип события').place(relx=0.8, rely=0.6)
        self.type_combo = Combobox(self.win, values=type_enc).place(relwidth=0.2, relheight=0.1,
                                                                    relx=0.799, rely=0.7)


        """
        Кнопки, позволяющие ГМу вносить изменения, улучшающие или ухудшающие результат события
        """
        self.gm_lab = Label(self.win, text='Кнопки, серящие или мошнящие под игроков').place(relx=0.3, rely=0.8)
        self.user1 = Checkbutton(self.win, text='Орг серит').place(relx=0.15, rely=0.9)
        self.user2 = Checkbutton(self.win, text='Орг помогает').place(relx=0.35, rely=0.9)
        self.user3 = Checkbutton(self.win, text='Душная награда').place(relx=0.55, rely=0.9)
        self.user4 = Checkbutton(self.win, text='Щедрая награда').place(relx=0.75, rely=0.9)

        """
        Текстовое поле, в которое выводятся результаты ивента
        """

        self.win.mainloop()

    def quit(self):
        self.win.destroy()


if __name__ == "__main__":
    app = App()
