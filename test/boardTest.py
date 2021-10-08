import sys
import math as m
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem

class MovingObject(QGraphicsEllipseItem):
    def __init__(self, x, y, r):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.setBrush(Qt.blue)
        self.setAcceptHoverEvents(True)

    # mouse hover event
    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    # mouse click event
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        print('x: {0}, y: {1}'.format(self.pos().x(), self.pos().y()))

class Piece(QtWidgets.QPushButton):
    def __init__(self,col,row):
        super().__init__()
        self.image = QtGui.QPixmap('black_piece.jpg')
        self.setStyleSheet("background-color: transparent")
        
        self.clicked.connect(self.on_click)

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        size = min(self.width(), self.height())
        print("size is", size)
        #qp.setBrush(QtGui.QBrush(Qt.red, Qt.SolidPattern))
        qp.setBrush(QtGui.QBrush(Qt.black, Qt.SolidPattern))
        qp.drawEllipse(0,0,34,34)

    """
    def paintEvent(self, event):
        super().paintEvent(event)
        #if not self.rect.isNull():
        qp = QtGui.QPainter(self)
        size = min(self.width(), self.height())
        print("size is", size)
        #qp.setBrush(QtGui.QBrush(Qt.red, Qt.SolidPattern))
        qp.setBrush(QtGui.QBrush(Qt.black, Qt.SolidPattern))
        qp.drawEllipse(0,0,size,size)
    """

    def on_click(self):
        print("hello world")

class Piece(QtWidgets.QWidget):
    """Controller for Checkerpiece"""
    def __init__(self,row,column):
        super().__init__()
        #self.image = QtGui.QPixmap('black_piece.jpg')
        self.setMinimumSize(32, 32)
        self.index = [row,column]
        print("index:", self.index)
    def paintEvent(self, event):
        """paints checkerpiece, need to set this as param for black or red
        also check if it is king or not
        leave this as Viewer part"""
        qp = QtGui.QPainter(self)
        self.size = min(self.width(), self.height())
        qp.setBrush(QtGui.QBrush(Qt.red, Qt.SolidPattern))
        qp.drawEllipse(0,0, self.size, self.size)
        
        self.rect = QtCore.QRect()
        #return center coordinates of individual piec
        self.center = [self.size/2, self.size/2]
        
    def mousePressEvent(self, event) -> None:
        """return location of board"""
        super().mousePressEvent(event)
        pressed_x = event.pos().x()
        pressed_y = event.pos().y() 
        if self.is_checker_selected(pressed_x,pressed_y):
            print("true")
        else:
            print("nope")
        
    
    def is_checker_selected(self, x,y):
        """check if mouse click is within circle returns true if it is"""
        radius = self.size/2
        mouse_click_dist = m.sqrt((self.center[0]-x)**2 + (self.center[1]-y)**2)
        if abs(mouse_click_dist) <= radius:
            print("within bounds")
            return True
        else:
            print("out of bounds")

    def move_piece(self,x,y):
        pass


#https://www.pythonguis.com/tutorials/bitmap-graphics/
class Board(QtWidgets.QWidget):
    """this is more of the graphical view and controller"""
    def __init__(self):
        super().__init__()
        self.length = 8
        layout = QtWidgets.QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.background = QtGui.QPixmap('checkersboard.jpg')

        for i in range(self.length):
            layout.setRowStretch(i, 1)
            layout.setColumnStretch(i, 1)

        for col in range(self.length):
            (col)
            layout.addWidget(Piece(1,col), 1, col)

    def minimumSizeHint(self):
        return QtCore.QSize(500, 250)


    def sizesHint(self):
        return QtCore.QSize(1280, 720)

    def resizeEvent(self, event):
        """resize checkerboard"""
        self.size = min(self.width(), self.height())
        rect = QtCore.QRect(0, 0, self.size, self.size)
        rect.moveCenter(self.rect().center())
        self.layout().setGeometry(rect)
        print("board sizesize is:", self.width(), self.height())
        print("individual square sizes are:", self.width()/self.length)
    
    def paintEvent(self, event):
        """resize paint"""
        qp = QtGui.QPainter(self)
        rect = self.layout().geometry()
        qp.drawPixmap(rect, self.background.scaled(rect.size(), 
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        
    def mousePressEvent(self, event) -> None:
        """return location of board"""
        x = event.pos().x()
        y = event.pos().y() 
        print("board location is:",x,y)
        
class CheckersEngine():
    """checks if moves are legal"""
    def possible_moves(self):
        pass

class CheckersGame(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)
        self.board = Board()
        layout.addWidget(self.board)
        self.table = QtWidgets.QTableWidget(1, 3)
        layout.addWidget(self.table)


app = QtWidgets.QApplication(sys.argv)
game = CheckersGame()
game.show()
sys.exit(app.exec_())
