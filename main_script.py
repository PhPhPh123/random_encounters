from random import randint, choice, choices
import json
import sqlite3
from tkinter import *
from tkinter.ttk import Combobox

window = Tk()
window.title("Рандомайзер событий ролки")
window.geometry('600x400')

def warehouse_insignificant_event():
    pass


def warehouse_significant_event():
    pass


def insignificant_event():
    pass


def significant_event():
    pass


def startbottom():
    global window
    combo = Combobox(window)
    combo['values'] = ('пустыня',
                       'город-улей',
                       'имперский городок',
                       'имперские руины',
                       'тундра',
                       "ледяная пустошь")
    combo.current(0)  # установите вариант по умолчанию
    combo.grid(column=0, row=0)
    return combo.current(), combo.get()


def terrain_choise():
    return print("123")


def main_logic():
    btn = Button(window, text="Старт", command=startbottom)
    btn.grid(column=2, row=0)
    window.mainloop()


if __name__ == "__main__":
    main_logic()
