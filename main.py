import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication


class CoffeeWidget(QMainWindow):
    def __init__(self):
        super(CoffeeWidget, self).__init__()
        uic.loadUi('main.ui', self)

        self.con = sqlite3.connect('coffee.sqlite')

        self.initUi()
        self.pushButton.clicked.connect(self.filter)
        self.pushButton_2.clicked.connect(self.initUi)
        self.listWidget.itemClicked.connect(self.open_add)
        self.pushButton_3.clicked.connect(self.open_redactor)

    def initUi(self):
        self.pushButton_2.hide()
        self.comboBox.clear()
        self.comboBox_2.clear()
        self.spinBox.clear()
        self.spinBox_2.clear()

        cur = self.con.cursor()

        views = cur.execute("SELECT DISTINCT view FROM 'table'").fetchall()
        types = cur.execute("SELECT DISTINCT type FROM 'table'").fetchall()
        maxs = cur.execute("SELECT hundred_price FROM 'table'").fetchall()

        self.comboBox.addItem('Любой')
        self.comboBox_2.addItem('Любая')

        for val in views:
            self.comboBox.addItem(val[0])
        for val in types:
            self.comboBox_2.addItem(val[0])

        self.spinBox.setMaximum(max([i[0] for i in maxs]))
        self.spinBox_2.setMaximum(max([i[0] for i in maxs]))
        self.spinBox.setValue(0)
        self.spinBox_2.setValue(max([i[0] for i in maxs]))

        self.get_table()

    def filter(self):
        self.pushButton_2.show()
        self.get_table()

    def get_table(self):
        cur = self.con.cursor()
        self.listWidget.clear()
        self.statusBar().clearMessage()

        view = self.comboBox.currentText()
        type = self.comboBox_2.currentText()
        min = self.spinBox.value()
        max = self.spinBox_2.value()

        request = f"""SELECT sort FROM 'table' 
        WHERE hundred_price <= {max} and hundred_price >= {min}"""

        if view != 'Любой':
            request += f" and view = '{view}'"
        if type != 'Любая':
            request += f" and type = '{type}'"

        res = cur.execute(request).fetchall()

        if res:
            for i in res:
                self.listWidget.addItem(''.join(i[0]))
        else:
            self.statusBar().showMessage('Ничего не найдено')

    def open_redactor(self, *params, sort=None):
        ex1 = Redactor(self, params, sort=sort)
        ex1.show()

    def open_add(self):
        a = self.listWidget.selectedItems()[0].text()
        ex1 = AddClass(a, self)
        ex1.show()


class AddClass(QMainWindow):
    def __init__(self, name, parent=None):
        super(AddClass, self).__init__(parent)
        uic.loadUi('sort.ui', self)
        self.parent = parent
        self.name = name
        self.get_all()

        self.pushButton_2.clicked.connect(lambda: self.close())

    def get_all(self):
        self.setWindowTitle(self.name)
        cur = self.parent.con.cursor()
        params = cur.execute(f"""SELECT * FROM 'table' WHERE sort = '{self.name}'""").fetchone()
        self.pushButton.clicked.connect(lambda: self.parent.open_redactor(params, sort=self))

        fry, description, price, volume = cur.execute(f"""SELECT fry, description, price, volume FROM 'table'
                        WHERE sort = '{self.name}'""").fetchone()

        self.textEdit.setPlainText(description)
        self.label_4.setText(price + ' руб')
        self.label_5.setText(volume + ' г')
        self.label_7.setText(fry)


class Redactor(QMainWindow):
    def __init__(self, parent=None, params=None, sort=None):
        super(Redactor, self).__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.pushButton.clicked.connect(self.save_results)

        self.id = None
        self.parent = parent
        self.sort = sort

        if params[0]:
            a, b, c, d, e, f, g, h, i = params[0]
            self.id = a
            self.lineEdit.setText(b)
            self.lineEdit_2.setText(c)
            self.lineEdit_3.setText(d)
            self.comboBox.setCurrentText(e)
            self.textEdit.setPlainText(f)
            self.spinBox.setValue(int(g))
            self.spinBox_2.setValue(int(h))

    def save_results(self):
        self.statusBar().clearMessage()
        try:
            b = self.lineEdit.text()
            c = self.lineEdit_2.text()
            d = self.lineEdit_3.text()
            e = self.comboBox.currentText()
            f = self.textEdit.toPlainText()
            g = self.spinBox.value()
            h = self.spinBox_2.value()
            i = round(g // h * 100)
            cur = self.parent.con.cursor()
            if self.id:
                cur.execute(f"""UPDATE 'table'
                SET sort = '{b}', view = '{c}', fry = '{d}', type = '{e}', description = '{f}', 
                price = '{g}', volume = '{h}', hundred_price = {i}
                WHERE id = {self.id}""")
                self.parent.con.commit()
                self.sort.get_all()
            else:
                cur.execute(f"""INSERT INTO 'table'(sort,view,fry,type,description,price,volume,hundred_price)
                VALUES('{b}','{c}','{d}','{e}','{f}','{g}','{h}',{i})""")
                self.parent.con.commit()
            self.parent.get_table()
            self.close()
        except ZeroDivisionError:
            self.statusBar().showMessage('Невозможный формат')


def main():
    app = QApplication(sys.argv)
    ex = CoffeeWidget()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

