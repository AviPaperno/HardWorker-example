# -*- coding: utf-8 -*-

from hardworker import app, hardworkerapp, Tasks, task, BaseTask
from flask import render_template
import os
import time
import random

# Выполняется настройка полей-ограничений
hardworkerapp.config['MAX_COUNT'] = 5
hardworkerapp.config['MAX_TYPE_COUNT'] = {'task_2': 3}

# Выполняется настройка полей для отправки e-mail
# Введите свои данные или отключите доступ к сети
hardworkerapp.config['MAIL_LOGIN'] = ''
hardworkerapp.config['MAIL_PASSWORD'] = ''

# "Перенос" окружения Flask-приложения в текущий проект
app.template_folder = os.getcwd() + '/templates'
app.static_folder = os.getcwd() + '/static'


# Задаём таски
@task("task_1")
def task1(params):
    """
    Возвращает случайное число после паузы. Длительность паузы задаётся пользователем.
    :param params:
    :return:
    """
    time_for_sleep = params[u'time']
    time.sleep(time_for_sleep)
    return random.randrange(0, 120)


@task("task_2", json_schema={'type': 'object', 'properties': {u'n': {'type': 'number'}}})
def task_2(params):
    """
    Возвращает n-ое число Фибоначчи
    :param params:
    :return:
    """
    def generate_fib(n):
        if n == 0 or n == 1:
            return 1
        else:
            return generate_fib(n - 1) + generate_fib(n - 2)
    answ = generate_fib(params[u'n'])
    time.sleep(answ)
    return answ


class MyTask(BaseTask):
    name = 'task_3'
    json_schema = {}

    def run(self, params):
        """
        Возвращает факториал числа
        :param params:
        :return:
        """
        def generate_fac(n):
            if n == 0:
                return 1
            else:
                return n * generate_fac(n - 1)

        f = open("output.txt", "w")
        f.write("Факториал {} = {}".format(params[u'n'], generate_fac(params[u'n'])))
        f.close()
        time.sleep(params[u'n'])
        return {"result": u"Факториал посчитан", "file_path": os.path.abspath("output.txt")}


if __name__ == '__main__':
    @app.route('/status')
    def status_table():
        """
        Этот метод отображает таблицу со всеми процессами, одни разделяются в зависимости от типа

        :return:
        """
        s = hardworkerapp.DB()
        table1 = s.query(Tasks).filter(Tasks.status == 0).all()
        table2 = s.query(Tasks).filter(Tasks.status == 1).all()
        table3 = s.query(Tasks).filter(Tasks.status == 2).all()
        table4 = s.query(Tasks).filter(Tasks.status == 3).all()
        s.close()
        return render_template('index.html', x=(table1, table2, table3, table4),
                               vals=list(map(len, (table1, table2, table3, table4))))


    @app.route('/tasks')
    def show_tasks_info():
        """
        Этот метод отображает список зарегистрированных типов задач и их ограничения на количество одновременных запусков (если имеются)
        :return:
        """
        return render_template('index_2.html', type=hardworkerapp.types, ogr=hardworkerapp.max_types,
                               vals=len(hardworkerapp.types))


    @app.route('/add_task')
    def add_task():
        """
        Этот метод генерирует страницу для добавления задачи. Если у задачи есть json-схема, то будут автоматически
        сгенерированны поля для ввода. Если схема отсутствует, то будет единственное поле, для ввода параметров в формате JSON
        :return:
        """
        forms = {}
        for i in hardworkerapp.types:
            try:
                forms[i] = hardworkerapp.validators[i]['properties'].items()
            except Exception:
                forms[i] = {}
        return render_template('add_tasks.html', items=hardworkerapp.types, fields=forms)

hardworkerapp.start()
app.run(host='0.0.0.0', port=8089)
