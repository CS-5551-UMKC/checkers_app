#!/usr/bin/python3

"""
ZetCode PyQt5 tutorial

This is a Tetris game clone.

Author: Jan Bodnar
Website: zetcode.com
"""

import random
import sys

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor,QPen
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication


class Checkers(QMainWindow):
    """spawn game mode size and derive rules from game engine"""

    def init_board(self):
        """Generates the initial game/board"""
        pass

    def draw_board(self):
        """draws components of board"""

    def check_legal_moves(self):
        """check if moves are legal"""
        pass

class Board(QFrame):

    BoardWidth = 7
    BoardHeight = 7

    def __init__(self, parent):
        super().__init__(parent)

        self.init_board()

    def init_board(self):
        """Generates the initial game/board"""
        self.setFocusPolicy(Qt.StrongFocus)

    def draw_board(self):
        """draws components of board"""
        self.set

    def check_legal_moves(self):
        """check if moves are legal"""
        pass

