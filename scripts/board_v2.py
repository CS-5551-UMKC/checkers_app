import sys
import math 
from itertools import cycle

from PyQt5.QtCore import ( QRegExp,QFile, QRectF, QSize, QTimer, Qt,QRect, 
                        QPointF,pyqtSignal, pyqtSlot)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QImage, QPixmap)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout, QLabel, QWidget, QGraphicsEllipseItem,
                            QHBoxLayout, QGraphicsScene, QTableWidget,
                             QGraphicsView, QMainWindow, QPushButton,
                             QGraphicsObject, QSizePolicy)

from PyQt5.QtGui import QPen, QBrush

from pprint import pprint


"""
Board Controller - QWidget?
    - handles all the buisiness logic 
    - tells the boardview what to do
    - Detects what is pressed and then applies the game rules
Board View - QFrame 
    - Draws the grid
    - The graphical interface 

"""
class CheckersGame():
    """this class drives the rules of the game"""
    def __init__(self) -> None:
        self.grid_size = 8
        self.rank = '12345678'
        self.reverse_rank = '87654321'
        self.file = 'abcdefgh'
        self.reverse_file = 'hgfedcba' 
        self.checkers_position = {}

        self.getMapping()

    def getMapping(self):
        #is this the buisness logic?
        self.row_col_mapping = self.getRowColKey(self.rank, self.reverse_file)
        self.sans_mapping = self.getSanKey(self.rank, self.reverse_file)

    def getRowColKey(self, rank_order, file_order_reverse):
        """generates a hashtable/dictionary key = row,col
        values are file and rank"""
        grid_location = {}
        for col, file in enumerate(self.file):
            for row,rank in enumerate(self.reverse_rank):
                grid_location[row,col] = file+rank
        
        #pprint(grid_location)
        return grid_location

    def getSanKey(self, rank_order, file_order_reverse):
        """generates a hashtable/dictionary key=sans notation 
        values in are the col, and row"""
        square_to_coords = {}
        for col, file in enumerate(self.file):
            for row,rank in enumerate(self.reverse_rank):
                square_to_coords[file + rank] = (row,col)
        pprint(square_to_coords)
        return square_to_coords

    def getSanPosition(self,row,col):
        """returns san position using the row col mapping"""
        san_position = self.row_col_mapping[row,col]
        return san_position

    def recordPosition(self,piece):
        self.checkers_position[piece] = piece

    def updateCheckerPosition(self, new_checker, old_checker):
        """updates the position of the checkers position by removing the previous location of piece
        and updating the piece """
        self.checkers_position.pop(old_checker.san_position) 
        print("new checker position is", new_checker.san_position)
        self.checkers_position[new_checker.san_position] = new_checker 

    def findLegalMoves(self, row,col, player_or_opp):
        """need to refactor this and check if move is out of bounds"""
        current_loc = [row,col]
        legal_moves = []

        if player_or_opp == "Opponent":
            leg_move_1 = [current_loc[0] + 1, current_loc[1]-1] #move left
            leg_move_2 = [current_loc[0] + 1, current_loc[1]+1] #move right
            moves_list = [leg_move_1, leg_move_2]
        #other wise it is a player
        else:
            """check all possible moves based on what type of piece the checkerpiece is
            check for possible kills: single, multiple, triple, etc.
            if its out of bounds less than 0 or greater then 7 throw the move out - Done
            if the space is occupied by a teammate piece then throw the move out - Done
            """
            leg_move_1 = [current_loc[0] - 1, current_loc[1]-1] #move left subtract instead
            leg_move_2 = [current_loc[0] - 1, current_loc[1]+1] #move right
            moves_list = [leg_move_1, leg_move_2]

        """check if moves are out of bounds"""
        for index, moves in enumerate(moves_list):
            """check if moves are not occupied by a friendly player"""
            #if san_position in self.checkers_position:
            
            if ((moves[0]>= 0) and (moves[0]<=8) and (moves[1]>=0) and (moves[1]<=8)):
                print("move is legal", moves[0], moves[1])
                
                san_position = self.getSanPosition(moves[0], moves[1])
                print("san position", san_position)
                print("checker pieces", self.checkers_position)
                
                if san_position not in self.checkers_position:
                    print("move not in neighboring parts")
                    legal_moves.append((moves[0],moves[1]))
                else:
                    print("yes move", san_position + " is occupied by: ", self.checkers_position)
        
        return legal_moves

    def checkTurn(self):
        pass

    def updateKing(self):
        pass
    
    def checkCheckerExists(self, san_location):
        """check if piece position exists in the dictionary"""
        if (san_location) in self.checkers_position:
            return True
        else:
            False

class Checker(QDialog):

    """might make this custom paint and determine if player or oppponent"""
    def __init__(self, parent, san_position, grid_position, player_or_opp):
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
        
        if self.player_or_opp == "Player":
            self.image = QPixmap('red_checker.png')
        else:
            self.image = QPixmap('black_piece.png')

        self.is_enabled = True
        self.setMouseTracking(True)
        # When label is scaled, also scale image inside the label
        self.show()

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

class BoardController(QFrame, CheckersGame):
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
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)    
        self.setLayout(self.layout)
        self.visualizeBoard()
        self.turn = [None,None]
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
        """need to rename the dictionaries"""
        #this is the GUI
        self.drawBoard(self.rank, self.reverse_file)
        #this is inherited from the Parent class 
        self.checkers_position = self.placeCheckers(self.sans_mapping)

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
        """not sure if should be part of buisiness logic uses the SAN notation for placement"""
        piece_info = {}
        row, col = square_dict['b1']
        piece_label = Checker(self, san_position='b1', grid_position=[row,col], player_or_opp="Player")
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label    

        row, col = square_dict['a4']
        piece_label = Checker(self,san_position='a4', grid_position=[row,col], player_or_opp="Player")
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label
        pprint(piece_info)
        
        return piece_info

    def showMoves(self, moves_row_col, piece, curr_row, curr_col):
        """show legal moves on the GUI where player can select , if they select it then we send a signal
        to update the position of the board and move it respectively"""
        for moves in moves_row_col:
            print("showMoves:", curr_row, curr_col)
            san_position = self.getSanPosition(moves[0], moves[1])
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
                new_san_position = self.getSanPosition(new_row, new_col)
                new_checker = Checker(self, new_san_position, [new_row, new_col], "Player")
                #update position of checker
                self.updateCheckerPosition(new_checker, piece)
                # update the position in the GUI 
                self.layout.addWidget(new_checker, new_row, new_col) 
                
                #set toggle on button to false since we made a move 
                self.toggle_on = False
                
        self.deleteMoves()

    def deleteMoves(self):
        """delete moves button after buttons are set"""
        moves_button = self.findChildren(MovesButton)
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
            #check if piece exists from gamepiece dictionary - Done
            #check if it is the correct type selected - put in checkerpiece class
            san_location = self.row_col_mapping[curr_row,curr_col]

            # show legal moves
            if self.checkCheckerExists(san_location):
                piece = self.checkers_position[san_location]
                moves_row_col = self.findLegalMoves(curr_row,curr_col, piece.player_or_opp)
                if moves_row_col != False:
                    #show legal moves in the game
                    self.showMoves(moves_row_col,piece, curr_row, curr_col)
                    self.toggle_on = True  

                else:
                    print("no possible moves")
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
            san_location = self.row_col_mapping[curr_row,curr_col]

            # show legal moves
            if self.checkCheckerExists(san_location):
                piece = self.checkers_position[san_location]
                moves_row_col = self.findLegalMoves(curr_row,curr_col, piece.player_or_opp)
                self.toggle_on = False
                self.deleteMoves()  
                    

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

