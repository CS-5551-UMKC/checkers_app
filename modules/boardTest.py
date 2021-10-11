#!/usr/bin/env python

import sys
import math as m
from itertools import cycle
from typing import Set

from PyQt5.QtCore import (QRectF, QSize, QTimer, Qt,QRect, QPointF)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QImage)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QWidget, QGraphicsEllipseItem,
                            QHBoxLayout, QGraphicsScene, QTableWidget,
                             QGraphicsView, QMainWindow, QPushButton,
                             QGraphicsItem)

from PyQt5.QtGui import QPen, QBrush

"""settings and params"""
class Settings():
    """need to refactor and change code naming"""
    WIDTH = 75 #squares 
    HEIGHT= 75 #squares
    NUM_BLOCKS_X = 8 #index at 0
    NUM_BLOCKS_Y = 8 #index at 0
    BOARD_SIZE = WIDTH*NUM_BLOCKS_X

class CheckerPiece(QGraphicsItem):
    def __init__(self,color):
        super().__init__(parent = None)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        #self.color = QColor(255,0,0)
        self.color = color
        self.setAcceptHoverEvents(True)

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

    # mouse click event
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        print("original and updated:", orig_cursor_position, updated_cursor_position)

    def mouseMoveEvent(self, event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()
        #print("original and updated:", orig_cursor_position, updated_cursor_position)

        orig_position = self.scenePos()
        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        print('x: {0}, y: {1}'.format(self.pos().x(), self.pos().y()))

class BoardView(QGraphicsView):
    def __init__(self):
        #super(View, self).__init__(parent)
        super().__init__()
        #scene view -> scene -> items
        self.piece_list = [] #checkerpieces
        self.lines = [] #rectangle lines
        self.set_opacity(0.3)
        self.size = min(self.width(), self.height())
        
    def minimumSizeHint(self):
        return QSize(800, 800)

    def sizesHint(self):
        return QSize(1280, 720)

    def resizeEvent(self, event) -> None:
        """resize and draw checkerboard"""
        self.scene = QGraphicsScene()
        self.mapToScene(QRect(0, 0, self.size, self.size))

        self.setScene(self.scene)
        self.drawGrid()
        self.insertPieces()
        
    def insertPieces(self):
        """refactor this """
        opp_color = QColor(0,0,255)  
        for x in range(0,3): 
            xo = x * Settings.WIDTH 
            if (x % 2) != 0:
                for y in range(0,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(opp_color)
                    checkerPiece.setPos(yo,xo)
                    self.scene.addItem(checkerPiece)
                    self.piece_list.append(checkerPiece)  
            else:
                for y in range(1,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(opp_color)
                    checkerPiece.setPos(yo,xo)
                    self.scene.addItem(checkerPiece)
                    self.piece_list.append(checkerPiece)  

        player_color = QColor(255,0,0)
        for x in range(5,8): 
            xo = x * Settings.WIDTH 
            if (x % 2) != 0:
                for y in range(0,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(player_color)
                    checkerPiece.setPos(yo,xo)
                    self.scene.addItem(checkerPiece)
                    self.piece_list.append(checkerPiece)  
            else:
                for y in range(1,Settings.NUM_BLOCKS_Y,2):
                    yo = y * Settings.HEIGHT
                    checkerPiece = CheckerPiece(player_color)
                    checkerPiece.setPos(yo,xo)
                    self.scene.addItem(checkerPiece)
                    self.piece_list.append(checkerPiece)  

    def drawGrid(self) -> None:
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

    def mousePressEvent(self, event) -> None:
        """detect grid location of mouse press event"""
        x = event.pos().x() 
        y = event.pos().y() 
        pass

class BoardController(QWidget):
    def __init__(self):
        super().__init__()
        self.boardview = BoardView()
        self.boardview.draw_grid()

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
