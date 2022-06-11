from interface import start, create_list_for_randchoice, sql_select, terrain_func
from interface import type_enc, type_threat, danger_level, terrains, abspath
import random
import sqlite3
from unittest import TestCase, main


db = sqlite3.connect(abspath)  # connect to sql base
cursor = db.cursor()  # Creation sqlite cursor

test_ttk = {'угроза орков': str(random.randint(0, 5)),
            'угроза хаоситов': str(random.randint(0, 5)),
            'угроза друкхари': str(random.randint(0, 5)),
            'угроза тиранидов': str(random.randint(0, 5)),
            'угроза тау': str(random.randint(0, 5)),
            'угроза некронов': str(random.randint(0, 5)),
            'угроза мутантов': str(random.randint(0, 5)),
            'угроза малых рас': str(random.randint(0, 5)),
            'угроза дикой природы': str(random.randint(0, 5)),
            'угроза стихийных бедствий': str(random.randint(0, 5)),
            'угроза бандитов': str(random.randint(0, 5)),
            'угроза мятежников': str(random.randint(0, 5)),
            'угроза демонов': str(random.randint(0, 5)),
            'террейн': str(random.choice(terrains)),
            'сложность': str(random.choice(danger_level)),
            'тип события': 'случайное событие',
            'общий бафф': random.randint(0, 1),
            'общий дебафф': random.randint(0, 1),
            'дебафф награды': random.randint(0, 1),
            'бафф награды': random.randint(0, 1)}


class enc_testing(TestCase):
    def test_query(self):
        for _ in range(1000):
            res = create_list_for_randchoice(test_ttk)
            try:
                create_list_for_randchoice(test_ttk)
            except IndexError:
                print(res)
                print(len(res))


if __name__ == '__main__':
    tst = enc_testing()
    tst.test_query()
    print('Тест завершен')
