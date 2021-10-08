import random
import sys

from PyQt5 import QtCore, QtGui, QtWidgets


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.rect = QtCore.QRect()
        self.drag_position = QtCore.QPoint()

        button = QtWidgets.QPushButton("Add", self)
        button.clicked.connect(self.on_clicked)

        self.resize(640, 480)

    @QtCore.pyqtSlot()
    def on_clicked(self):
        if self.rect.isNull():
            self.rect = QtCore.QRect(
                QtCore.QPoint(*random.sample(range(200), 2)), QtCore.QSize(100, 100)
            )
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.rect.isNull():
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 5, QtCore.Qt.SolidLine))
            painter.drawEllipse(self.rect)

    def mousePressEvent(self, event):
        if (
            2 * QtGui.QVector2D(event.pos() - self.rect.center()).length()
            < self.rect.width()
        ):
            self.drag_position = event.pos() - self.rect.topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.drag_position.isNull():
            self.rect.moveTopLeft(event.pos() - self.drag_position)
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = QtCore.QPoint()
        super().mouseReleaseEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Rect = Window()
    Rect.show()
    sys.exit(app.exec_())