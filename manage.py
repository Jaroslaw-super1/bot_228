import os
import sys
import webbrowser
import sqlite3
import vk_api

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5 import QtWidgets, uic
from random import randint

from vk_api.longpoll import VkLongPoll


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Запускает информацию
def dialog():
    login_page = info_d()
    login_page.exec_()


# def login(log, password):
#     vk_session = vk_api.VkApi(log, password)
#     try:
#         vk_session.auth(token_only=True)
#         vk_s = vk_session.get_api()
#         return vk_s
#     except vk_api.AuthError as error_msg:
#         return -1


class MyWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('manage_blueprint.ui', self)  # Загружаем дизайн

        # Соеденяемся с базой
        self.conn = sqlite3.connect('base.db')
        self.cur = self.conn.cursor()
        self.conn.commit()

        # Подключаем сообщество
        token = str(self.cur.execute("""SELECT * FROM bot_log_in""").fetchone()[0])
        vk_session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(vk_session)
        self.vk = vk_session.get_api()

        # Список выбранного заказа
        self.sakas = list()

        # шаблон нажатия кнопки
        # self.имя.clicked.connect(self.функция)

        if self.vk != -1:
            self.mission_start.clicked.connect(self.mission_start_def)
            self.mission_passert.clicked.connect(self.mission_passert_def)
            self.mission_trash.clicked.connect(self.mission_trash_def)
            self.start_bot.clicked.connect(self.start_bot_def)
            self.add_bot.clicked.connect(self.add_bot_def)
        else:
            self.error3.setText("Подключите акаунт")


        self.info.clicked.connect(dialog)
        self.append.clicked.connect(self.append_def)
        self.delet.clicked.connect(self.delet_def)
        self.go_to.clicked.connect(self.go_to_def)
        self.finish.clicked.connect(self.finish_def)

        self.Towar.cellClicked.connect(self.table_cliced)
        self.updates.clicked.connect(self.loaddata)
        self.loaddata_towar()
        self.loaddata()

    # Получает данные из таблицы
    def table_cliced(self):
        self.sakas = []
        for i in range(3):
            self.sakas.append(self.Towar.item(self.Towar.currentRow(), i).text())

    # Начать заказ
    def mission_start_def(self):
        if self.sakas and self.cur.execute(
                f"""SELECT * FROM auc WHERE name_id = {self.sakas[0]} and product_name = '{self.sakas[1]}'""").fetchone()[4] == 'заказано':
            self.vk.messages.send(
                user_id=self.sakas[0],
                message=f"Мы приступили к выполнению заказа {self.sakas[1]}",
                random_id=randint(1, 1000000)
            )

            self.cur.execute(
                f"""UPDATE auc SET status = "выполняется" WHERE name_id = {self.sakas[0]} AND product_name = '{self.sakas[1]}'""")
            self.conn.commit()
            self.loaddata()
            self.sakas = []
            self.error1.setText('')
        else:
            self.error1.setText('Выбирите заказ')

    # Завершить заказ
    def mission_passert_def(self):
        if self.sakas and self.cur.execute(
                f"""SELECT * FROM auc WHERE name_id = {self.sakas[0]} and product_name = '{self.sakas[1]}'""").fetchone()[
            4] == 'выполняется':
            self.vk.messages.send(
                user_id=self.sakas[0],
                message=f'Ваш заказ "{self.sakas[1]}" выполнен!',
                random_id=randint(1, 1000000)
            )

            self.cur.execute(
                f"""UPDATE auc SET status = "выполнен" WHERE name_id = {self.sakas[0]} AND product_name = '{self.sakas[1]}'""")
            self.conn.commit()
            self.loaddata()
            self.sakas = []
            self.error1.setText('')
        else:
            self.error1.setText('Выбирите заказ')

    # Отказать заказ
    def mission_trash_def(self):
        if self.sakas:
            self.vk.messages.send(
                user_id=self.sakas[0],
                message=f"К сожалению вам было отказано в выполнении заказа '{self.sakas[1]}'",
                random_id=randint(1, 1000000)
            )

            self.cur.execute(
                f"""DELETE FROM auc WHERE name_id = {self.sakas[0]} AND product_name = '{self.sakas[1]}'""")
            self.conn.commit()
            self.loaddata()
            self.sakas = []
            self.error1.setText('')
        else:
            self.error1.setText('Выбирите заказ')

    # Добавить товар
    def append_def(self):
        a = self.towar_name.text()
        b = self.price.text()
        if a == '':
            self.error2.setText('Введите название товара')
        elif b == '':
            self.error2.setText('Введите цену')
        elif not b.isdigit():
            self.error2.setText('Цена должна быть числом')
        else:
            self.cur.execute(f"""INSERT INTO products(product, min_price) VALUES('{a.lower()}', {int(b)});""")
            self.conn.commit()
            self.towar_name.setText('')
            self.price.setText('')
            self.error2.setText('Товар добавлен')
            self.loaddata_towar()

    # Удалить товар
    def delet_def(self):
        a = self.towar_name.text()

        b = self.cur.execute(f"""SELECT * FROM products""").fetchall()
        ls = []

        for i in range(len(b)):
            ls.append(b[i][1])

        if a == '':
            self.error2.setText('Введите название товара')
        elif a not in ls:
            self.error2.setText('Такого товара нет')
        else:
            self.cur.execute(
                f"""DELETE FROM products WHERE product = '{a}'""")
            self.conn.commit()
            self.towar_name.setText('')
            self.price.setText('')
            self.error2.setText('Товар удалён')
            self.loaddata_towar()

    # Запустить бота
    def start_bot_def(self):
        os.startfile('"bot_228.exe"')

    # Добавить акаунт
    def add_bot_def(self):
        login_bot = self.log1.text()

        if login_bot == "":
            self.error3.setText("Введите токен")
        else:
            self.cur.execute(
                f"""UPDATE bot_log_in SET login = '{login_bot}'""")
            self.conn.commit()

            # Подключаем сообщество
            token = str(self.cur.execute("""SELECT * FROM bot_log_in""").fetchone()[0])
            vk_session = vk_api.VkApi(token=token)
            self.longpoll = VkLongPoll(vk_session)
            self.vk = vk_session.get_api()

            self.error3.setText("Сообщество подключено")

            # Очищаем поля
            self.log1.setText("")

    # Перейти к пользователю
    def go_to_def(self):
        if self.sakas:
            a = self.sakas[0]
            webbrowser.open(f'https://vk.com/id{int(a)}', new=2)
            self.sakas = []
            self.error4.setText('')
        else:
            self.error4.setText('Выбирите заказ')

    # Завершить заказ
    def finish_def(self):
        if self.sakas and self.cur.execute(
                f"""SELECT * FROM auc WHERE name_id = {self.sakas[0]} and product_name = '{self.sakas[1]}'""").fetchone()[
            4] == 'выполнен':
            self.cur.execute(
                f"""DELETE FROM auc WHERE name_id = {self.sakas[0]} AND product_name = '{self.sakas[1]}'""")
            self.conn.commit()
            self.loaddata()
            self.sakas = []
            self.error4.setText('')
        else:
            self.error4.setText('Выбирите заказ')

    # Выводит данные в таблицу заказов
    def loaddata(self):
        base = self.cur.execute("""SELECT * FROM auc""").fetchall()
        self.sakas = []

        z = 0
        for i in self.cur.execute("""SELECT * FROM auc"""):
            z += 1

        self.Towar.setRowCount(z)
        tablerow = 0

        for i in range(len(base)):
            self.Towar.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(base[i][3])))
            self.Towar.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(str(base[i][1])))
            self.Towar.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(str(base[i][4])))
            tablerow += 1

    # Выводит данные в таблицу товаров
    def loaddata_towar(self):
        base = self.cur.execute("""SELECT * FROM products""").fetchall()
        z = 0
        for i in self.cur.execute("""SELECT * FROM products"""):
            z += 1

        self.Towar_list.setRowCount(z)
        tablerow = 0

        for i in range(len(base)):
            self.Towar_list.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(base[i][1])))
            self.Towar_list.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(str(base[i][2])))
            tablerow += 1


class info_d(QDialog):
    def __init__(self):
        super(info_d, self).__init__()
        uic.loadUi('info.ui', self)

        self.ok.clicked.connect(self.close)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
