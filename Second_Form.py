import sys
import random

from PyQt5.QtCore import QSize, Qt, QRect
from PyQt5.QtGui import QPixmap
from PyQt5 import Qt

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QPushButton, QTableWidget, QWidget, \
    QGridLayout, QTableWidgetItem, QLineEdit

SCREEN_SIZE = [1024, 768]
button_for_click = []
start, end = 0, 0
row, column, mines = 0, 0, 0
visual, secret = [], []
label_lose, label_win = '', ''


class SecondForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setMinimumSize(QSize(*SCREEN_SIZE))
        self.setWindowTitle('Разминка мозга')

        self.column_text = QLabel('Количество столбцов', self)
        self.column_text.move(10, 10)

        self.column_number = QLineEdit(self)
        self.column_number.move(140, 10)

        self.row_text = QLabel('Количество строк', self)
        self.row_text.move(10, 50)

        self.row_number = QLineEdit(self)
        self.row_number.move(140, 50)

        self.mine_text = QLabel('Количество мин', self)
        self.mine_text.move(300, 10)

        self.mine_number = QLineEdit(self)
        self.mine_number.move(400, 10)

        self.start = QPushButton('Начать', self)
        self.start.resize(self.start.sizeHint())
        self.start.clicked.connect(self.make_pole)
        self.start.move(300, 50)

    def make_pole(self):
        self.row, self.column, self.mines = '', '', ''
        number = self.row_number.text()
        if number.isnumeric() and int(float(number)) == float(number):
            self.row = number
        number = self.column_number.text()
        if number.isnumeric() and int(float(number)) == float(number):
            self.column = number
        number = self.mine_number.text()
        if number.isnumeric() and int(float(number)) == float(number):
            self.mines = number
        if self.row.isnumeric() and self.column.isnumeric() and self.mines.isnumeric():
            print(2)
            self.saper = Saper(self.row, self.column, self.mines)
            print(3)
            self.saper.show()


class MyButton(Qt.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        global start, visual, secret, row, column, mines, end, button_for_click
        button = event.button()
        if button == Qt.Qt.RightButton:
            h_row, h_column = self.text().split(':')[-2:]
            h_row, h_column = int(h_row), int(h_column)
            if start != 0:
                end, visual = self.moving(h_row, h_column, 'F', row, column, visual, secret)
                if 'F' not in self.text():
                    self.setStyleSheet("""QPushButton{background-color: rgb(0,0,0);color: rgb(255,255,255)}""")
                else:
                    self.setStyleSheet("""QPushButton{background-color: rgb(0,255,0);color: rgb(0,255,0)}""")
                self.show_field(visual)
        elif button == Qt.Qt.LeftButton:
            h_row, h_column = self.text().split(':')
            h_row, h_column = int(h_row), int(h_column)
            if start == 0:
                start += 1
                visual, secret = self.field_generation(h_row, h_column, row, column, mines)
                visual = self.recurrence(h_row, h_column, row, column, visual, secret)
                end = self.check_flag(visual, secret, row, column, mines)
                self.show_field(visual)
            else:
                end, visual = self.moving(h_row, h_column, 'O', row, column, visual, secret)
                if end == 1:
                    print('GAME OVER')
                    self.ended()
                    self.show_field(visual)
                else:
                    end = self.check_flag(visual, secret, row, column, mines)
                    if end == 2:
                        print('WIN')
                        self.ended()
                    self.show_field(visual)
            for i in range(row):
                for j in range(column):
                    if visual[i][j] == '[-]' or visual[i][j][1:-1].isnumeric():
                        button_for_click[i][j].setStyleSheet("""QPushButton{background-color: rgb(0,0,0);
                                                                color: rgb(255,255,255)}""")
        return Qt.QPushButton.mousePressEvent(self, event)

    def ended(self):
        global label_win, label_lose, end
        if end != 0:
            for i in range(row):
                for j in range(column):
                    button_for_click[i][j].setEnabled(False)
        if end == 2:
            label_win.show()
        elif end == 1:
            label_lose.show()

    def field_generation(self, h_row, h_column, row, column, mines):
        k = []
        f = [['[ ]' for i in range(column)] for j in range(row)]
        d = [['[ ]' for i in range(column)] for j in range(row)]
        for i in range(row):
            for j in range(column):
                if i != h_row or j != h_column:
                    k.append([i, j])
        for i in range(mines):
            h = k.pop(random.randint(0, len(k) - 1))
            f[h[0]][h[1]] = "[M]"
        for i in range(row):
            for j in range(column):
                if f[i][j] != '[M]':
                    mine = 0
                    for q in range(max(0, i - 1), min(row, i + 2)):
                        for r in range(max(0, j - 1), min(column, j + 2)):
                            if f[q][r] == '[M]':
                                mine += 1
                    f[i][j] = f'[{mine}]'
        d[h_row][h_column] = f[h_row][h_column]
        return d, f

    def show_field(self, visual):
        global row, column, button_for_click
        for i in range(row):
            for j in range(column):
                if visual[i][j] != '[ ]':
                    button_for_click[i][j].setText(visual[i][j][1:-1])
                if visual[i][j] == '[-]' or visual[i][j][1:-1].isnumeric():
                    button_for_click[i][j].setEnabled(False)
        for i in visual:
            print('\t'.join(j for j in i))

    def check_flag(self, visual, secret, row, column, mines):
        count = 0
        for i in range(row):
            for j in range(column):
                if visual[i][j][1].isnumeric() or visual[i][j] == '[-]':
                    count += 1
        if row * column - count == mines:
            return 2
        else:
            return 0

    def moving(self, h_row, h_column, h_type, row, column, visual, secret):
        if h_type != 'O':
            if 'F' not in visual[h_row][h_column]:
                visual[h_row][h_column] = f'[{h_type}:{h_row}:{h_column}]'
            else:
                visual[h_row][h_column] = f'[{h_row}:{h_column}]'
            return 0, visual
        else:
            visual[h_row][h_column] = secret[h_row][h_column]
            if visual[h_row][h_column] == '[M]':
                return 1, visual
            if visual[h_row][h_column] == '[0]':
                visual = self.recurrence(h_row, h_column, row, column, visual, secret)
            return 0, visual

    def recurrence(self, h_row, h_column, row, column, visual, secret): # h_row, h_column, row, column, visual, secret
        if secret[h_row][h_column] == '[0]' and visual[h_row][h_column] != '[-]':
            visual[h_row][h_column] = '[-]'
            if h_column > 0 and secret[h_row][h_column - 1] == '[0]':
                visual = self.recurrence(h_row, h_column - 1, row, column, visual, secret)
            elif h_column > 0 and visual[h_row][h_column - 1] != '[-]':
                visual[h_row][h_column - 1] = secret[h_row][h_column - 1]

            if h_row < row - 1 and secret[h_row + 1][h_column] == '[0]':
                visual = self.recurrence(h_row + 1, h_column, row, column, visual, secret)
            elif h_row < row - 1 and visual[h_row + 1][h_column] != '[-]':
                visual[h_row + 1][h_column] = secret[h_row + 1][h_column]

            if h_column < column - 1 and secret[h_row][h_column + 1] == '[0]':
                visual = self.recurrence(h_row, h_column + 1, row, column, visual, secret)
            elif h_column < column - 1 and visual[h_row][h_column + 1] != '[-]':
                visual[h_row][h_column + 1] = secret[h_row][h_column + 1]

            if h_row > 0 and secret[h_row - 1][h_column] == '[0]':
                visual = self.recurrence(h_row - 1, h_column, row, column, visual, secret)
            elif h_row > 0 and visual[h_row - 1][h_column] != '[-]':
                visual[h_row - 1][h_column] = secret[h_row - 1][h_column]
        return visual


class Saper(QWidget):
    def __init__(self, row, column, mines):
        super().__init__()
        self.row = int(row)
        self.column = int(column)
        self.mines = int(mines)
        self.make_pole()

    def make_pole(self):
        global button_for_click, start, end, row, column, mines, visual, secret, label_win, label_lose
        button_for_click = []
        start, end = 0, 0
        row, column, mines = 0, 0, 0
        visual, secret = [], []
        row, column, mines = self.row, self.column, self.mines
        self.setMinimumSize(QSize(*SCREEN_SIZE))
        self.setWindowTitle('Saper')
        self.layout = Qt.QHBoxLayout(self)
        self.table = Qt.QTableWidget()
        self.table.setRowCount(self.row)
        self.table.setColumnCount(self.column)
        self.button = [[MyButton(f'{i}:{j}', self) for j in range(self.column)] for i in range(self.row)]
        for i in range(self.row):
            for j in range(self.column):
                self.button[i][j].setStyleSheet('background: rgb(0,255,0); color: rgb(0, 255, 0)')
                self.table.setCellWidget(i, j, self.button[i][j])
        self.layout.addWidget(self.table)
        button_for_click = self.button

        label_win = QLabel()
        label_win.move(30, 200)
        label_win.resize(400, 200)
        label_win.setScaledContents(1)
        label_win.setPixmap(QPixmap('win.jpg'))
        label_win.hide()

        label_lose = QLabel()
        label_lose.move(30, 400)
        label_lose.resize(400, 200)
        label_lose.setScaledContents(1)
        label_lose.setPixmap(QPixmap('lose.jpg'))
        label_lose.hide()

    def check(self):
        global end, row, column, button_for_click
        print(450, end)
        if end != 0:
            for i in range(row):
                for j in range(column):
                    button_for_click[i][j].setEnabled(False)
        if end == 2:
            self.label_win.show()
        elif end == 1:
            self.label_lose.show()

