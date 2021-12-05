from abc import abstractproperty
import sys
import math 
from itertools import cycle

from PyQt5.QtCore import (QSize, Qt,QRect)
from PyQt5.QtGui import (QPainter, QPixmap)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout, 
                            QWidget, QHBoxLayout, QTableWidget,
                            QMainWindow, QPushButton,QSizePolicy, QMessageBox)

from pprint import pprint

from checkers_app import CheckersGame

"""
Board Controller - QWidget?
    - handles all the buisiness logic 
    - tells the boardview what to do
    - Detects what is pressed and then applies the game rules
Board View - QFrame 
    - Draws the grid
    - The graphical interface 

"""
    
class Checker(QDialog):

    """might make this custom paint and determine if player or oppponent"""
    def __init__(self, parent, san_position, grid_position, player_or_opp, is_king):
        super().__init__()
        
        # Make label transparent, so square behind piece is visible
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(32, 32)
        #self.setMinimumSize(100, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.board = parent
        self.san_position = san_position
        self.grid_position = grid_position
        self.player_or_opp = player_or_opp #string 'Player' 'Opponent'
        
        self.king = is_king

        """refactor this to case switch"""
        if self.player_or_opp == "Player" and self.king == False:
            self.image = QPixmap('red_checker.png')
        elif self.player_or_opp == "Player" and self.king == True:
            self.image = QPixmap('red_king.png')
        elif self.player_or_opp == "Opponent" and self.king == False:
            self.image = QPixmap('black_piece.png')
        else:
            self.image = QPixmap('black_king.png')

        self.is_enabled = True
        self.setMouseTracking(True)
        # When label is scaled, also scale image inside the label
        self.show()

    def isKing(self):
        """accessor"""
        return self.king

    def getSanPosition(self):
        """accessor"""
        return self.san_position

    def getGridPosition(self):
        """accessor"""
        return self.grid_position

    def getPlayerorOpp(self):
        """return Player or Opponent"""
        return self.player_or_opp

    def enterEvent(self, event):
        if self.is_enabled:
            # Set open hand cursor while hovering over a piece
            QApplication.setOverrideCursor(Qt.OpenHandCursor)

    def leaveEvent(self, event):
        # Set arrow cursor while not hovering over a piece
        QApplication.setOverrideCursor(Qt.ArrowCursor)

    def paintEvent(self, event):
        qp = QPainter(self)
        size = min(self.width(), self.height())
        qp.drawPixmap(0, 0, self.image.scaled(
            size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

class MovesButton(QPushButton):
    def __init__(self, parent, san_position, grid_position) :
        super(MovesButton ,self).__init__()
        self.board = parent
        self.san_position = san_position
        self.grid_position= grid_position
        styleSheet = ("""
                    QPushButton{
                        background-color:  #2B5DD1;
                        padding: 2px;
                    }
                    QPushButton::hover{
                        background-color : lightgreen;
                    }
                    """)

        #self.setStyleSheet('background-color: rgb(255,255,255)')
        self.setStyleSheet(styleSheet)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
class KillMovesButton(QPushButton):
    def __init__(self, parent, san_position, grid_position, victims):
        super(KillMovesButton ,self).__init__()
        self.board = parent
        self.san_position = san_position
        self.grid_position= grid_position
        styleSheet = ("""
                    QPushButton{
                        background-color:  #FF0000;
                        padding: 2px;
                    }
                    QPushButton::hover{
                        background-color : lightred;
                    }
                    """)

        #self.setStyleSheet('background-color: rgb(255,255,255)')
        self.setStyleSheet(styleSheet)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.victims = victims

    def getVictims(self):
        """returns list of victims if kill button is executed"""
        return self.victims
        
class BoardController(QFrame):
    """Define this as ViewController
    need to map row,col to Sans
    map Sans to row,col 
    need to show occupied board 
    is the piece selected?
    if so what is its position
    what is the neighboring positions
    """

    def __init__(self) -> None:
        super(BoardController,self).__init__()
        #define layout of controller
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)    
        
        #Composition create instance of Checkers
        self.checkersGame = CheckersGame()

        #finalize the layout
        self.setLayout(self.layout)
        
        self.visualizeBoard()
        self.playerTurn = True
        self.toggle_on = False

    def minimumSizeHint(self):
        return QSize(800, 800)

    def sizesHint(self):
        return QSize(800, 800)

    def resizeEvent(self, event):
        size = min(self.width(), self.height())
        rect = QRect(0, 0, size, size)
        rect.moveCenter(self.rect().center())
        self.layout.setGeometry(rect)

    def visualizeBoard(self):
        """begin visualing the board"""
        rank_list = self.checkersGame.getRank()
        reverse_file = self.checkersGame.getReverseFile()
        self.drawBoard(rank_list, reverse_file)
        #self.checkersGame.checkers_position = self.placeCheckers(self.checkersGame.getSansMap())
        init_pieces = self.placeCheckers(self.checkersGame.getSansMap())
        self.checkersGame.initCheckers(init_pieces)

    def drawBoard(self, rank_order, file_order_reverse):
        """draw board layout"""
        for row, rank in enumerate(rank_order):
            for col, file in enumerate(file_order_reverse):
                square = QWidget(self)
                square.setObjectName(file + rank)
                square.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                if row % 2 == col % 2:
                    square.setStyleSheet('background-color: rgb(255,247,191)')
                else:
                    square.setStyleSheet('background-color: rgb(181, 136, 99)')
                self.layout.addWidget(square, row, col)

    def getRowColFromPixel(self, x, y):
        """get row and column from clicked mouse pixel location"""
        col = math.floor(x/100) 
        row = math.floor(y/100) 
        
        return (row,col)

    def placeCheckers(self, square_dict):
        """refactor this code put this in the CheckersGameEngine:
        GUI will recieve the information of the CheckersPiece and place it accordingly"""
        """refactor this"""
        piece_info = {}

        row, col = square_dict['a5']
        piece_label = Checker(self, 'a5', [row,col], "Player", False)
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label

        row, col = square_dict['e5']
        piece_label = Checker(self, 'e5', [row,col], "Opponent", False)
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label
        
        row, col = square_dict['b6']
        piece_label = Checker(self, 'b6', [row,col], "Player", False)
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label    

        row, col = square_dict['a7']
        piece_label = Checker(self, 'a7', [row,col], "Player", False)
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label    

        row, col = square_dict['f6']
        piece_label = Checker(self, 'f6', [row,col], "Player", True)
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label

        return piece_info

    def showMoves(self, moves_row_col, piece, curr_row, curr_col):
        """show legal moves on the GUI where player can select , if they select it then we send a signal
        to update the position of the board and move it respectively"""
        for moves in moves_row_col:
            print("moves: ", moves)
            san_position = self.checkersGame.getSanPosition(moves[0], moves[1])
            indicated_move = MovesButton(self, san_position, moves)
            indicated_move.clicked.connect(lambda: self.movePiece(piece, curr_row, curr_col)) 
            self.layout.addWidget(indicated_move, moves[0], moves[1])

    def movePiece(self, piece, curr_row, curr_col):
        """ get the location button selected """
        button = self.sender()
        idx = self.layout.indexOf(button)
        location = self.layout.getItemPosition(idx)
        new_row = location[0]
        new_col = location[1]
        piece_list = self.findChildren(QDialog)
        for piece in piece_list:
            #want to delete the piece from the previous location
            if piece.grid_position == [curr_row, curr_col]:
                piece.setParent(None) # delete the previous position
                was_king = piece.isKing()
                new_san_position = self.checkersGame.getSanPosition(new_row, new_col)
                
                #check if king or not
                if self.checkersGame.checkKing(piece.player_or_opp, new_row) or was_king:
                    new_checker = Checker(self, new_san_position, [new_row, new_col], piece.player_or_opp, True)
                else:
                    new_checker = Checker(self, new_san_position, [new_row, new_col], piece.player_or_opp, False)

                #update position of checker
                self.checkersGame.updateCheckerPosition(new_checker, piece)
                # update the position in the GUI 
                self.layout.addWidget(new_checker, new_row, new_col) 
                
                #set toggle on button to false since we made a move 
                self.toggle_on = False
                self.switchTurns()

        self.deleteMoves(KillMovesButton)        
        self.deleteMoves(MovesButton)

    def showKills(self, kill_moves,opps_locs,piece, curr_row, curr_col):
        """show legal kills the piece can make"""
        for idx,moves in enumerate(kill_moves):
            san_position = self.checkersGame.getSanPosition(moves[0], moves[1])
            indicated_move = KillMovesButton(self, san_position, moves, idx)
            print("victims from the killsmoves button:", indicated_move.getVictims())
            indicated_move.clicked.connect(lambda: self.executeKill(piece, curr_row, curr_col, opps_locs)) 
            self.layout.addWidget(indicated_move, moves[0], moves[1])

    def executeKill(self, piece, curr_row, curr_col, opp_locs):
        """ get the location button selected """
        button = self.sender()
        idx = self.layout.indexOf(button)
        location = self.layout.getItemPosition(idx)
        new_row = location[0]
        new_col = location[1]
        victim_list = []

        print("victim index" , button.getVictims())
        if button.getVictims() == 0:
            victim_list.append(opp_locs[button.getVictims()])
            print("victim list", victim_list)
        else:
            for i in range(-1, button.getVictims()):
                victim_list.append(opp_locs[i])
                print("victim list", victim_list)

        piece_list = self.findChildren(Checker)
        for piece in piece_list:
            #want to delete the piece from the previous location
            if piece.grid_position == [curr_row, curr_col]:
                piece.setParent(None) # delete the previous position
                was_king = piece.isKing()
                new_san_position = self.checkersGame.getSanPosition(new_row, new_col)
                #check if king or not
                if self.checkersGame.checkKing(piece.player_or_opp, new_row) or was_king:
                    new_checker = Checker(self, new_san_position, [new_row, new_col], piece.player_or_opp, True)
                else:
                    new_checker = Checker(self, new_san_position, [new_row, new_col], piece.player_or_opp, False)
                
                #remove the opponent pieces
                self.removePiece(victim_list)
                
                #update position of checker
                self.checkersGame.updateCheckerPosition(new_checker, piece)
                
                # update the position in the GUI 
                self.layout.addWidget(new_checker, new_row, new_col) 
                
                # check gamestate here
                if self.checkersGame.checkWinner(piece.getPlayerorOpp()) == True:
                    print("Winner is :", piece.getPlayerorOpp())
                    self.showWinner(piece.getPlayerorOpp())

                #set toggle on button to false since we made a move 
                self.toggle_on = False
                self.switchTurns()
                
        self.deleteMoves(KillMovesButton)        
        self.deleteMoves(MovesButton)

    def showWinner(self, player_or_opp):
        """Pop up message to notify who the winner is"""
        msg = QMessageBox()
        msg.setWindowTitle("Winner")
        msg.setText("The Winner is %s" % player_or_opp)
        msg.exec_()

    def removePiece(self, piece_removed_list):
        """removed pieces from board based on pieced_removed
        piece_removed is a list of row,col coordinates"""
        piece_list = self.findChildren(Checker)
        for piece in piece_list:
            if piece.grid_position in piece_removed_list:
                #remove from GUI and remove from checkers position game engine
                san_pos = self.checkersGame.getSanPosition(piece.grid_position[0],piece.grid_position[1])
                self.checkersGame.removeCheckerPiece(san_pos)
                piece.setParent(None)
                print("Removed piece")

    def switchTurns(self):
        self.playerTurn = not self.playerTurn
        print("Player turn is", self.playerTurn)

    def deleteMoves(self, button_type):
        """delete moves button after piece is set"""
        moves_button = self.findChildren(button_type)
        for button in moves_button:
            #print("button", button.grid_position)
            button.setParent(None)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.toggle_on==False:
            self.pressPos = event.pos().x()
            x = event.pos().x()
            y = event.pos().y()
            #get row and column
            curr_row,curr_col = self.getRowColFromPixel(x,y)
            #get San Location
            san_location = self.checkersGame.row_col_mapping[curr_row,curr_col]
            
            """Need to refactor this """
            #check if piece exists and it correlates to the correct piece turn type
            if self.checkersGame.checkCheckerExists(san_location):
                piece = self.checkersGame.checkers_position[san_location]
                print("piece position:", piece.san_position)
                #check if correct piece based on turn is selected
                if self.checkersGame.checkCorrectTurn(piece.player_or_opp, self.playerTurn):
                    kill_moves, opponent_locs = self.checkersGame.findPotentialKills(curr_row, curr_col, piece.player_or_opp, piece.isKing())
                    print("opponent locs", opponent_locs)
                    moves_row_col = self.checkersGame.findLegalMoves(curr_row,curr_col, piece.player_or_opp, piece.isKing())
                    if moves_row_col or kill_moves:
                        #show legal moves in the game
                        self.showMoves(moves_row_col,piece, curr_row, curr_col)
                        self.showKills(kill_moves, opponent_locs, piece, curr_row, curr_col)
                        self.toggle_on = True
                    else:
                        print("no possible moves")
                else:
                    print("Incorrect piece selected")
            else:
                print("no piece")
                
        #if event button is pressed again then we turn off the moves 
        else:
            self.pressPos = event.pos().x()
            x = event.pos().x()
            y = event.pos().y()
            #get row and column
            curr_row,curr_col = self.getRowColFromPixel(x,y)
            #check if piece exists from gamepiece dictionary - Done
            #check if it is the correct type selected - put in checkerpiece class
            san_location = self.checkersGame.row_col_mapping[curr_row,curr_col]

            # show legal moves
            if self.checkersGame.checkCheckerExists(san_location):
                piece = self.checkersGame.checkers_position[san_location]
                moves_row_col = self.checkersGame.findLegalMoves(curr_row,curr_col, piece.player_or_opp, piece.isKing())
                self.toggle_on = False
                self.deleteMoves(KillMovesButton)
                self.deleteMoves(MovesButton)  
                    
class CheckersAPP(QMainWindow):
    def __init__(self):
        super().__init__()
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        self.board = BoardController()
        layout.addWidget(self.board)
        self.table = QTableWidget(1, 2)
        layout.addWidget(self.table)


if __name__ =='__main__':
    app = QApplication(sys.argv)
    game = CheckersAPP()
    game.show()
    sys.exit(app.exec_())

