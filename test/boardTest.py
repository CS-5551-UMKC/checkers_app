import sys
import math as m

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem

class Piece(QtWidgets.QWidget):
    """Controller for Checkerpiece"""
    selected = QtCore.pyqtSignal(str)
    def __init__(self,row,column):
        self.index = [row,column]
        super().__init__()
        self.setMinimumSize(32, 32)
    
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
        pressed_x = event.pos().x()
        pressed_y = event.pos().y() 
        if self.is_checker_selected(pressed_x,pressed_y):
            self.selected.emit("HALLO WORLD")
            super().mousePressEvent(event)
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

#https://www.pythonguis.com/tutorials/bitmap-graphics/
class Board(QtWidgets.QWidget):
    """this is more of the graphical view and controller
    Generate Board
    Generate pieces
    Click on board
    check if own piece is selected  
    If piece selected allow option to move piece:
        -need to know current location of piece
        -move piece and update location
        -do this by moving a widget from gridlayotu
    """
    def __init__(self):
        super().__init__()
        self.length = 8
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.background = QtGui.QPixmap('checkersboard.jpg')
        self.piece_list = self.generateBoard(self.grid)
        
    def generateBoard(self,layout):
        """initalizes the board and begin game"""
        piece_list = []        
        for i in range(self.length):
            self.grid.setRowStretch(i, 1)
            self.grid.setColumnStretch(i, 1)

        for col in range(self.length):
            (col)
            piece = Piece(1,col)
            self.grid.addWidget(piece, 1, col)
            piece_list.append(piece)
            print(piece_list[col].index)
        return piece_list

    def minimumSizeHint(self):
        return QtCore.QSize(500, 500)

    def sizesHint(self):
        return QtCore.QSize(1280, 720)

    def resizeEvent(self, event):
        """resize checkerboard"""
        self.size = min(self.width(), self.height())
        rect = QtCore.QRect(0, 0, self.size, self.size)
        rect.moveCenter(self.rect().center())
        self.layout().setGeometry(rect)
        self.square_size = self.height()/self.length
        print("board pixel size is:", self.height())
        print("individual pixel square square size is:", self.square_size)
    
    def paintEvent(self, event):
        """resize paint"""
        qp = QtGui.QPainter(self)
        rect = self.layout().geometry()
        qp.drawPixmap(rect, self.background.scaled(rect.size(), 
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.board_size = rect.width()

    def mousePressEvent(self, event) -> None:
        """detect grid location of mouse press event"""
        x = event.pos().x() 
        y = event.pos().y() 
        row_column_index = self.findGridLocation(x,y)
        for i, piece in enumerate(self.piece_list):
            if piece.index == row_column_index:
               new_position = [0,i]
               moved_piece = Piece(new_position[0], new_position[1])
               self.movePiece(moved_piece, new_position)
               self.piece_list.append(moved_piece)
               
               self.piece_list.pop(i)
               self.removePiece(row_column_index)
               print(len(self.piece_list))
               #need to update piece location as well

    def removePiece(self, row_column_index):
        """listen if piece is selected and remove if so"""
        layout = self.grid.itemAtPosition(row_column_index[0], row_column_index[1])
        #check if my checker piece is actually there
        if layout is not None:
            layout.widget().deleteLater()
            self.grid.removeItem(layout)

    def movePiece(self, piece, new_position):
        """listen if piece is selected and move to position desired"""
        self.grid.addWidget(piece, new_position[0], new_position[1])

    def findGridLocation(self,x,y):
        """takes in the location of x and y coordinate of mouse click
        divides it by square size to find row and column
        """
        col_loc = m.floor(x/self.square_size)
        row_loc = m.floor((y/self.square_size))
        #print("column is", col_loc)
        #print("row is", row_loc)
        return [row_loc, col_loc]


    def check_piece_exists():
        """checks within game piece list/dictionary if piece is there
        returns true if it is """
        pass


class CheckersEngine():
    """checks if moves are legal"""
    def possible_moves(self):
        pass

class CheckersApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)
        self.board = Board()
        layout.addWidget(self.board)
        self.table = QtWidgets.QTableWidget(1, 3)
        layout.addWidget(self.table)

if __name__ =='__main__':

    app = QtWidgets.QApplication(sys.argv)
    game = CheckersApp()
    game.show()
    sys.exit(app.exec_())
