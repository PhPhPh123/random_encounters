from random import randint, choice, choices
import json
from tkinter import *


def warehouse_insignificant_event():
    pass


def warehouse_significant_event():
    pass


def insignificant_event():
    pass


def significant_event():
    pass


def main_logic():
    window = Tk()
    window.title("Рандомайзер событий ролки")
    window.geometry('600x400')
    btn = Button(window, text="Не нажимать!")
    btn.grid(column=1, row=0)
    window.mainloop()


if __name__ == "__main__":
    main_logic()
