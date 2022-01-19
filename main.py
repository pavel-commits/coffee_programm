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

    def open_add(self):
        a = self.listWidget.selectedItems()[0].text()
        ex1 = AddClass(a, self)
        ex1.show()


class AddClass(QMainWindow):
    def __init__(self, name, parent=None):
        super(AddClass, self).__init__(parent)

        uic.loadUi('sort.ui', self)
        self.setWindowTitle(name)

        cur = parent.con.cursor()
        description, price, volume = cur.execute(f"""SELECT description, price, volume FROM 'table'
                        WHERE sort = '{name}'""").fetchone()

        self.textEdit.setPlainText(description)
        self.label_4.setText(price + ' руб')
        self.label_5.setText(volume + ' г')


def main():
    app = QApplication(sys.argv)
    ex = CoffeeWidget()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

