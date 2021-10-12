#!/usr/bin/env python

import sys
import math as m
from itertools import cycle

from PyQt5.QtCore import (QRectF, QSize, QTimer, Qt,QRect, QPointF,pyqtSignal, pyqtSlot)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QImage)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QWidget, QGraphicsEllipseItem,
                            QHBoxLayout, QGraphicsScene, QTableWidget,
                             QGraphicsView, QMainWindow, QPushButton,
                             QGraphicsObject)

from PyQt5.QtGui import QPen, QBrush

"""Board and Piece implmentation 
Justin Nguyen
"""

"""settings and params"""
class Settings():
    """need to refactor and change code naming"""
    WIDTH = 75 #squares 
    HEIGHT= 75 #squares
    NUM_BLOCKS_X = 8 #index at 0
    NUM_BLOCKS_Y = 8 #index at 0
    BOARD_SIZE = WIDTH*NUM_BLOCKS_X

class CheckerPiece(QGraphicsObject):
    def __init__(self,color, player_or_opp):
        super().__init__(parent = None)
        self.setFlag(QGraphicsObject.ItemIsSelectable, True)
        #self.color = QColor(255,0,0)
        self.color = color
        self.setAcceptHoverEvents(True)
        self.playerorAI = player_or_opp #string if it is a player or opponenet 
    
    # mouse hover event
    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    def paint(self, painter, options, widget):
        painter.setPen(QPen(QColor(0,0,0), 3, Qt.SolidLine))
        painter.setBrush(QBrush(self.color, Qt.SolidPattern))
        painter.drawEllipse(0, 0, Settings.WIDTH, Settings.WIDTH)

    def boundingRect(self):
        return QRectF(0, 0, Settings.WIDTH, Settings.WIDTH)

    def getRowCol(self, x, y):
        """returns location of checkerpiece from pixel location
        keep in mind x pixel is the column location and y pixel is the row position"""
        self.col = m.floor(x/Settings.WIDTH)
        self.row = m.floor(y/Settings.WIDTH) 
        return [self.row, self.col]

    # mouse click event
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        location = self.getRowCol(self.pos().x(), self.pos().y())
        self.scene().pieceSelected.emit(location, self.playerorAI)
        
class GraphicsScene(QGraphicsScene):
    pieceSelected = pyqtSignal(object,object)

class BoardView(QGraphicsView):
    def __init__(self):
        #super(View, self).__init__(parent)
        super().__init__()
        #scene view -> scene -> items
        self.setParams()
        self.initBoard()
        self.scene.pieceSelected.connect(self.findMoves)

    def setParams(self):
        self.piece_list = [] #checkerpieces
        self.lines = [] #rectangle lines
        self.set_opacity(0.3)
        self.size = min(self.width(), self.height())
        self.scene = GraphicsScene()

    def initBoard(self):
        self.mapToScene(QRect(0, 0, self.size, self.size))
        self.setScene(self.scene)
        self.drawBoard()
        self.insertPieces()

    def findMoves(self,current_loc, player_or_opp):
        """indicate the possible legal moves the checkerpiece can make
        based on its location, check if black or red
        current_loc = int [row, col] --> [y,x] location on board
        player_or_opp = string input of Opponent or Player
        """
        

        """
        make sure moves are diagonal - X
        make sure moves are not out of bounds -X 
        make sure moves are within bounds - X
        make sure moves are not horizontal or vertical -X
        if king you can go backwards or forwards diagonlly, if regular only forward
        """
        #show all moves
        #then move any that are not legal
        #then show on board
        #if opponent row goes down so we add  
        if player_or_opp == "Opponent":
            leg_move_1 = [current_loc[0] + 1, current_loc[1]-1] #move left
            leg_move_2 = [current_loc[0] + 1, current_loc[1]+1] #move right
            moves_list = [leg_move_1, leg_move_2]
            #legal_moves = [lst for lst in moves if (lst[moves]<=0 or lst[moves]>=7) in lst]
            for index, moves in enumerate(moves_list):
                print(moves[0])
                if (moves[0] <= -1) or (moves[0]>=8) or (moves[1] <= -1) or (moves[1]>=8):
                    print("removing", moves)
                    moves_list.pop(index)
        #other wise it is a player
        else:
            leg_move_1 = [current_loc[0] - 1, current_loc[1]-1] #move left subtract instead
            leg_move_2 = [current_loc[0] - 1, current_loc[1]+1] #move right
            moves_list = [leg_move_1, leg_move_2]
            for index, moves in enumerate(moves_list):
                if (moves[0] <= -1) or (moves[0]>=8) or (moves[1] <= -1) or (moves[1]>=8):
                    print("removing", moves)
                    moves_list.pop(index)
        
        legal_moves = moves_list
        self.showLegalMoves(legal_moves)

    def showLegalMoves(self, legal_moves):
        """paint a circle to show possible legal moves in scene of board"""
        pen = QPen(QColor(0,0,0), 3, Qt.SolidLine)
        fill = QColor(0,255,0)
        for moves in legal_moves:
            #print("moves", moves)
            xo = moves[1] * Settings.WIDTH #pixel location
            yo = moves[0] * Settings.WIDTH #pixel location
            (self.scene.addEllipse(xo,yo,Settings.WIDTH,Settings.WIDTH,pen,fill))
        
    def resizeEvent(self, event) -> None:
        """resize and draw checkerboard"""
        print("updating")
        self.scene.update(0, 0, self.size, self.size)

    def minimumSizeHint(self):
        return QSize(800, 800)

    def sizesHint(self):
        return QSize(Settings.BOARD_SIZE, Settings.BOARD_SIZE)

    def insertPieces(self):
        """refactor this """
        opp_color = QColor(0,0,255)  
        for x in range(0,3): 
            xo = x * Settings.WIDTH 
            if (x % 2) != 0:
                for y in range(0,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(opp_color, "Opponent")
                    checkerPiece.setPos(yo,xo)
                    self.scene.addItem(checkerPiece)
                    self.piece_list.append(checkerPiece)  
            else:
                for y in range(1,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(opp_color, "Opponent")
                    checkerPiece.setPos(yo,xo)
                    self.scene.addItem(checkerPiece)
                    self.piece_list.append(checkerPiece)  

        player_color = QColor(255,0,0)
        for x in range(5,8): 
            xo = x * Settings.WIDTH 
            print(xo)
            if (x % 2) != 0:
                for y in range(0,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(player_color, "Player")
                    checkerPiece.setPos(yo,xo)
                    self.scene.addItem(checkerPiece)
                    self.piece_list.append(checkerPiece)  
            else:
                for y in range(1,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(player_color, "Player")
                    checkerPiece.setPos(yo,xo)
                    self.scene.addItem(checkerPiece)
                    self.piece_list.append(checkerPiece)  
                    
    def drawBoard(self) -> None:
        """function is too long need to import initial settings
        allow change of fill color parameters"""
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        pen = QPen(QColor(0,0,0), 3, Qt.SolidLine)
        red_fill = QColor(255,0,0)
        black_fill = QColor(0,0,0)
        fill_color = cycle([black_fill, red_fill])

        for x in range(0,Settings.NUM_BLOCKS_X): 
            """xo and yo are origin coordinates to draw each rectangle"""
            xo = x * Settings.WIDTH 
            color = next(fill_color)
            for y in range(0,Settings.NUM_BLOCKS_Y):
                color = next(fill_color)
                yo = y * Settings.WIDTH
                self.lines.append(self.scene.addRect(xo,yo,Settings.WIDTH,Settings.WIDTH,pen, color))
            
    def set_visible(self,visible=True) -> None:
        for line in self.lines:
            line.setVisible(visible)

    def set_opacity(self,opacity) -> None:
        for line in self.lines:
            line.setOpacity(opacity)

class CheckersAPP(QMainWindow):
    def __init__(self):
        super().__init__()
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        self.board = BoardView()
        layout.addWidget(self.board)
        self.table = QTableWidget(1, 3)
        layout.addWidget(self.table)

if __name__ =='__main__':
    app = QApplication(sys.argv)
    game = CheckersAPP()
    game.show()
    sys.exit(app.exec_())
