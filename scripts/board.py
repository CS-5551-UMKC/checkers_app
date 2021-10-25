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
        self.color = color
        self.setAcceptHoverEvents(True)
        self.playerorAI = player_or_opp #string if it is a player or opponenet
        self.position = [None,None] 
    
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
        super(CheckerPiece,self).mousePressEvent(event)
        location = self.getRowCol(self.pos().x(), self.pos().y())
        self.emitLocation(location)
        self.emitPieceType()

    def emitLocation(self,location):
        self.scene().pieceSelected.emit(location)

    def emitPieceType(self):
        self.scene().pieceType.emit(self.playerorAI)

class BoardView(QGraphicsScene):
    pieceSelected = pyqtSignal(object)
    pieceType = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.grid_lines = []

    def drawBoard(self) -> None:
        """function is too long need to import initial settings
        allow change of fill color parameters"""
        pen = QPen(QColor(0,0,0), 3, Qt.SolidLine)
        red_fill = QColor(255,0,0)
        black_fill = QColor(0,0,0)
        fill_color = cycle([black_fill, red_fill])
        grid_loc = []
        for x in range(0,Settings.NUM_BLOCKS_X): 
            """xo and yo are origin coordinates to draw each rectangle"""
            xo = x * Settings.WIDTH 
            color = next(fill_color)
            for y in range(0,Settings.NUM_BLOCKS_Y):
                color = next(fill_color)
                yo = y * Settings.WIDTH
                self.grid_lines.append(self.addRect(xo,yo,Settings.WIDTH,Settings.WIDTH,pen, color))
                coords = [xo,yo]
                grid_loc.append(coords)

        return grid_loc

    def set_visible(self,visible=True) -> None:
        for line in self.grid_lines:
            line.setVisible(visible)

    def set_opacity(self,opacity) -> None:
        for line in self.grid_lines:
            line.setOpacity(opacity)

    def drawPieces(self, player_or_opp):
        """draw checker pieces based on whether it is a player or opponent """
        checker_piece_list = []
        if player_or_opp == "Opponent":
            color = QColor(0,0,255)
            init_range = 0
            final_range = 3
        else: 
            color = QColor(255,0,0)
            init_range = 5
            final_range = 8
  
        for x in range(init_range, final_range): 
            xo = x * Settings.WIDTH 
            if (x % 2) != 0:
                for y in range(0,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(color, player_or_opp)
                    checkerPiece.setPos(yo,xo)
                    self.addItem(checkerPiece)
                    checkerPiece.position = checkerPiece.getRowCol(yo,xo)
                    checker_piece_list.append(checkerPiece)  
            else:
                for y in range(1,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(color, player_or_opp)
                    checkerPiece.setPos(yo,xo)
                    self.addItem(checkerPiece)
                    checkerPiece.position = checkerPiece.getRowCol(yo,xo)
                    checker_piece_list.append(checkerPiece)  

        return checker_piece_list

    def drawLegalMoves(self, legal_moves):
        """paint a circle to show possible legal moves in scene of board"""
        pen = QPen(QColor(0,0,0), 3, Qt.SolidLine)
        fill = QColor(0,255,0)
        for moves in legal_moves:
            #print("moves", moves)
            xo = moves[1] * Settings.WIDTH #pixel location
            yo = moves[0] * Settings.WIDTH #pixel location
            (self.addEllipse(xo,yo,Settings.WIDTH,Settings.WIDTH,pen,fill))

    def hideLegalmoves(self, legal_moves):
        """remove the shown legal moves if piece is selected again"""

                        
class BoardController(QGraphicsView):
    """
    Board controller recieves the graphical scene of the board and pieces
    not sure if I should inherit this
    Scene inherits from View --> this is kind of dumb but we can change it 
    """
    def __init__(self):
        super().__init__()
        #self.set_opacity(0.3)
        self.curr_piece = None
        self.curr_loc = None

        self.size = min(self.width(), self.height())
        self.visualizeBoard()
        self.visualizePiece()
        self.main()

    def visualizeBoard(self):
        """set up and show board display using the Scene"""
        self.mapToScene(QRect(0, 0, self.size, self.size))
        self.boardView = BoardView()
        self.setScene(self.boardView)
        self.grid_loc = self.boardView.drawBoard()

    def visualizePiece(self):
        """draw and recieve the piece locations"""
        self.opp_pieces = self.boardView.drawPieces("Opponent")
        self.player_pieces = self.boardView.drawPieces("Player")

        self.boardView.pieceSelected.connect(self.selectedPiece)
        self.boardView.pieceType.connect(self.getPieceType)
        
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
        self.boardView.drawLegalMoves(legal_moves)
    
    def selectedPiece(self,location):
        self.curr_loc = location
        print("location", self.curr_loc)
        
        return self.curr_loc

    def returnPieceType(self,piece_type):
        self.curr_piece = self.getPieceType(piece_type=piece_type)
        return self.curr_piece

    def getPieceType(self, piece_type):
        self.curr_piece = piece_type
        return self.curr_piece

    def isTurn(self):
        """verifies if piece selected corresponds to respective
        player or opponents turn return true if it is"""

    def main(self):
        print(self.curr_loc)
        

class CheckersAPP(QMainWindow):
    def __init__(self):
        super().__init__()
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        self.board = BoardController()
        layout.addWidget(self.board)
        self.table = QTableWidget(1, 3)
        layout.addWidget(self.table)

if __name__ =='__main__':
    app = QApplication(sys.argv)
    game = CheckersAPP()
    game.show()
    sys.exit(app.exec_())
