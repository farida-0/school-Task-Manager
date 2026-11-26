from PyQt6.QtWidgets import (QMainWindow,
                             QApplication,
                             QWidget,
                             QMessageBox,
                             QTableWidgetItem,
                             QHeaderView,
                             QDialog)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QDate
import sqlite3
from main_window_ui import Ui_MainWindow
from task_change_ui import Ui_Form
from confirm_dialog_ui import Ui_confirmDialog
from signUp_ui import Ui_reg_window
from signIn_ui import Ui_signIn_window
from confirm_logout_ui import Ui_Dialog
from about_ui import Ui_AboutDialog
import sys


class TaskManager(QMainWindow, Ui_MainWindow):
    def __init__(self, db, user_id):
        super().__init__()
        self.setupUi(self)
        self.db = db
        self.user_id = user_id

        header = self.tasksTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.load()

        self.addBtn.clicked.connect(self.pressed_add)
        self.editBtn.clicked.connect(self.pressed_change)
        self.deleteBtn.clicked.connect(self.pressed_delete)

        self.searchLine.textChanged.connect(self.chosen_filter)
        self.dateCombo.currentIndexChanged.connect(self.chosen_filter)
        self.statusCombo.currentIndexChanged.connect(self.chosen_filter)
        self.resetBtn.clicked.connect(self.reset_filter)

        self.logoutBtn.clicked.connect(self.logout)
        self.aboutBtn.clicked.connect(self.about)

    def logout(self):
        self.dialog = LogoutDialog(self)
        self.dialog.exec()

    def about(self):
        self.about_window = AboutDialog()
        self.about_window.exec()

    def reset_filter(self):
        self.searchLine.clear()
        self.statusCombo.setCurrentText('По умолчанию')
        self.dateCombo.setCurrentText('По умолчанию')


    def chosen_filter(self):
        text = self.searchLine.text()
        status = self.statusCombo.currentText()
        date = self.dateCombo.currentText()

        rows = self.db.filter(text, status, date, self.user_id)
        self.tasksTable.setRowCount(len(rows))

        for i, j in enumerate(rows):
            self.tasksTable.setItem(i, 0, QTableWidgetItem(str(j[0])))
            self.tasksTable.setItem(i, 1, QTableWidgetItem(j[1]))
            self.tasksTable.setItem(i, 2, QTableWidgetItem(j[2]))
            self.tasksTable.setItem(i, 3, QTableWidgetItem(j[3]))

    def pressed_add(self):
        self.form = TaskChanger(self.db, self, user_id=self.user_id)
        self.form.show()

    def pressed_change(self):
        r = self.tasksTable.currentRow()

        if r == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите задачу')
            return

        task_id = int(self.tasksTable.item(r, 0).text())
        
        self.form = TaskChanger(self.db, self, task_id, self.user_id)
        self.form.show()

    def pressed_delete(self):
        r = self.tasksTable.currentRow()

        if r == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите задачу')
            return

        task_id = int(self.tasksTable.item(r, 0).text())
        self.dialog = Dialog(self.db, self, task_id, self.user_id)
        self.dialog.exec()

    def load(self):
        rows = self.db.all(self.user_id)
        self.tasksTable.setRowCount(len(rows))
        for i, j in enumerate(rows):
            self.tasksTable.setItem(i, 0, QTableWidgetItem(str(j[0])))
            self.tasksTable.setItem(i, 1, QTableWidgetItem(j[1]))
            self.tasksTable.setItem(i, 2, QTableWidgetItem(j[2]))
            self.tasksTable.setItem(i, 3, QTableWidgetItem(j[3]))



class TaskChanger(QWidget, Ui_Form):
    def __init__(self, db, main_window, id=None, user_id=None):
        super().__init__()
        self.setupUi(self)
        self.user_id = user_id

        self.statusCombo.setItemData(0, 1)
        self.statusCombo.setItemData(1, 0)

        self.db = db
        self.main_window = main_window
        self.id = id

        self.imageLabel.setPixmap(QPixmap('douma_chibik.png'))
        self.imageLabel.setScaledContents(True)
        
        self.dateEdit.setDate(QDate.currentDate())

        self.saveButton.clicked.connect(self.save)
        self.declineButton.clicked.connect(self.close)

        if self.id is not None:
            self.setWindowTitle('Редактирование задачи')
            task = db.get(self.id, self.user_id)
            self.titleEdit.setText(task[1])
            self.dateEdit.setDate(QDate.fromString(task[2], 'yyyy-MM-dd'))

            index = self.statusCombo.findData(task[3])
            self.statusCombo.setCurrentIndex(index)
        else:
            self.setWindowTitle('Запись новой задачи')


    def save(self):
        title = self.titleEdit.text().strip()
        if not title:
            QMessageBox.warning(self, 'Ошибка', 'Введите задачу')
            return

        date_txt = self.dateEdit.date().toString('yyyy-MM-dd')
        status_id = self.statusCombo.currentData()
        if self.id is None:
            self.db.add(title, date_txt, status_id, self.user_id)
        else:
            self.db.update(self.id, title, date_txt, status_id, self.user_id)
        self.main_window.chosen_filter()
        self.close()


class Dialog(QDialog, Ui_confirmDialog):
    def __init__(self, db, main_window, id, user_id):
        super().__init__()
        self.setupUi(self)

        self.db = db
        self.main_window = main_window
        self.id = id
        self.user_id = user_id

        self.buttonBox.accepted.connect(self.confirm_delete)

    def confirm_delete(self):
        self.db.delete(self.id, self.user_id)
        self.main_window.chosen_filter()
        self.accept()


class LogoutDialog(QDialog, Ui_Dialog):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)

        self.main_window = main_window
        self.setWindowTitle('Выход из аккаунта')
        self.buttonBox.accepted.connect(self.logout)
        self.buttonBox.rejected.connect(self.close)

    def logout(self):
        self.signInWindow = SignIn(self.main_window.db)
        self.signInWindow.show()

        self.main_window.close()
        self.accept()


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.image.setPixmap(QPixmap('douma_about.jpeg'))
        self.image.setScaledContents(True)


class DB:
    def __init__(self):
        self.f = sqlite3.connect('tasks.db')
        self.cur = self.f.cursor()

    def all(self, user_id):
        r = self.cur.execute("""
            SELECT tasks.id, tasks.title, tasks.date, statuses.name
            FROM tasks
            JOIN statuses
            ON tasks.status_id = statuses.id
            WHERE tasks.user_id = ?
            ORDER BY tasks.id
        """, (user_id,)).fetchall()
        return r

    def get(self, id, user_id):
        r = self.cur.execute("""
            SELECT id, title, date, status_id
            FROM tasks
            WHERE id = ?
            AND user_id = ?
        """, (id, user_id)).fetchone()
        return r

    def add(self, title, date, id, user_id):
        r = self.cur.execute("""
            INSERT INTO tasks (title, date, status_id, user_id)
            VALUES (?, ?, ?, ?)
        """, (title, date, id, user_id))
        self.f.commit()
        return

    def update(self, task_id, title, date, status_id, user_id):
        self.cur.execute("""
            UPDATE tasks
            SET title = ?, date = ?, status_id = ?
            WHERE id = ?
            AND user_id = ?
        """,(title, date, status_id, task_id, user_id))
        self.f.commit()
        return

    def delete(self, id, user_id):
        self.cur.execute("""
            DELETE FROM tasks
            WHERE id = ?
            AND user_id = ?
        """, (id, user_id))
        self.f.commit()
        return

    def filter(self, text, status, date, user_id):
        a = """
            SELECT tasks.id, tasks.title, tasks.date, statuses.name
            FROM tasks
            JOIN statuses
            ON tasks.status_id = statuses.id
            WHERE tasks.title LIKE ?
            AND tasks.user_id = ?
        """
        items = [f'%{text}%', user_id]
        if status == 'Активные':
            a += " AND tasks.status_id = ?"
            items.append(1)
        elif status == 'Выполнены':
            a += " AND tasks.status_id = ?"
            items.append(0)

        if date == 'Сначала новые':
            a += " ORDER BY tasks.date DESC"
        elif date == 'Сначала старые':
            a += ' ORDER BY tasks.date ASC'
        else:
            a += ' ORDER BY tasks.id'

        r = self.cur.execute(a, items).fetchall()
        return r

    def signingUp(self, login, password):
        user = self.cur.execute("""
            SELECT id
            FROM users
            WHERE username = ?
        """, (login,)).fetchone()

        if user is not None:
            return 0

        self.cur.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (login, password))

        self.f.commit()
        return 1

    def signingIn(self, login, password):
        user = self.cur.execute("""
            SELECT id
            FROM users
            WHERE username = ?
            AND password = ?
        """, (login, password)).fetchone()

        if user is None:
            return 0

        return user[0]


class SignUp(QWidget, Ui_reg_window):
    def __init__(self, db):
        super().__init__()
        self.setupUi(self)
        self.db = db
        self.SignUpBtn.clicked.connect(self.registration)
        self.backBtn.clicked.connect(self.close)

    def registration(self):
        login = self.loginEdit.text().strip()
        password = self.passwordEdit.text()

        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'ПОЛЯ ЗАПОЛНИ')
            return

        r = self.db.signingUp(login, password)

        if r == 0:
            QMessageBox.warning(self, 'Ошибка', 'Такой логин уже существует \(Т-Т)/')
        elif r == 1:
            QMessageBox.information(self, 'Поздравляем', 'Вы успешно зарегистрировались<3')
            self.loginEdit.clear()
            self.passwordEdit.clear()
            self.close()


class SignIn(QWidget, Ui_signIn_window):
    def __init__(self, db):
        super().__init__()
        self.setupUi(self)
        self.db = db
        self.SignInBtn.clicked.connect(self.signing_in)
        self.SignUpBtn.clicked.connect(self.toSignUp)

    def signing_in(self):
        login = self.loginEdit.text().strip()
        password = self.passwordEdit.text()

        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'зачем поля пустыми оставил?')
            return

        user_id = self.db.signingIn(login, password)

        if user_id == 0:
            QMessageBox.warning(self, 'Ошибка', 'ВВЕДИ ДАННЫЕ ПРАВИЛЬНО (>_<)')
            return

        self.main_window = TaskManager(self.db, user_id)
        self.main_window.show()
        self.close()

    def toSignUp(self):
        self.signUpWindow = SignUp(self.db)
        self.signUpWindow.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = DB()
    window = SignIn(db)
    window.show()
    sys.exit(app.exec())

