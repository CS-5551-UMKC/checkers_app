from abc import abstractproperty
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
        """helper function"""
        self.row_col_mapping = self.getRowColKey()
        self.sans_mapping = self.getSanKey()

    def getRowColKey(self):
        """generates a hashtable/dictionary key = row,col
        values are file and rank"""
        grid_location = {}
        for col, file in enumerate(self.file):
            for row,rank in enumerate(self.reverse_rank):
                grid_location[row,col] = file+rank
        
        return grid_location

    def getSanKey(self):
        """generates a hashtable/dictionary key=sans notation 
        values in are the col, and row"""
        square_to_coords = {}
        for col, file in enumerate(self.file):
            for row,rank in enumerate(self.reverse_rank):
                square_to_coords[file + rank] = (row,col)
        
        return square_to_coords

    def getSanPosition(self,row,col):
        """returns san position using the row col mapping"""
        if row>=8 or col>=8 or row <= -1 or col<= -1:
            return None
        else:
            san_position = self.row_col_mapping[row,col]
            return san_position

    def getRowColPosition(self,san_position):
        """returns san position using the row col mapping"""
        row_col_position = self.sans_mapping[san_position]
        return row_col_position 

    def initCheckers(self):
        """layout the checker pieces for the initial game"""
        

    def recordPosition(self,piece):
        self.checkers_position[piece] = piece

    def updateCheckerPosition(self, new_checker, old_checker):
        """updates the position of the checkers position by removing the previous location of piece
        and updating the piece """
        old_san_position = old_checker.getSanPosition()
        new_san_position = new_checker.getSanPosition()
        self.checkers_position.pop(old_san_position) 
        print("new checker position is", new_san_position)
        self.checkers_position[new_san_position] = new_checker 

    def findManhattanDistance(self,curr_loc, opponent_loc):
        dx = opponent_loc[0] - curr_loc[0]
        dy = opponent_loc[1] - curr_loc[1]
        return [dx,dy]

    def checkInBounds(self,moves):
        """check if move is within bounds if so return True"""
        if ((moves[0]>= 0) and (moves[0]<=7) and (moves[1]>=0) and (moves[1]<=7)):
            return True

    def checkPotentialJumps(self,new_san_position,player_or_opp):
        if new_san_position in self.checkers_position:
            blocking_piece_type = self.checkers_position[new_san_position].getPlayerorOpp()
            if blocking_piece_type != player_or_opp:
                return True
            else:
                return False

    def doJumps(self, current_san_position, new_san_position, player_or_opp):
        """determines possible jumps and returns it to jump list as row and column index"""
        jump_list = []
        curr_loc = self.getRowColPosition(current_san_position)
        opp_piece_loc = self.checkers_position[new_san_position].getGridPosition()
        manhattan_distance = self.findManhattanDistance(curr_loc, opp_piece_loc)
        jump_loc = [opp_piece_loc[0]+manhattan_distance[0],opp_piece_loc[1]+manhattan_distance[1]]
        jump_list.append((jump_loc))

        opponent_move_list = [[1, -1], #move diag left
                            [1, 1]] #move diag right

        player_move_list = [[-1, -1], #move diag left
                            [-1, 1]]  #move diag right

        if player_or_opp == "Opponent":
            moves_list = opponent_move_list 
        else:
            moves_list = player_move_list

        for move in moves_list:
            possible_move = [jump_loc[0]+move[0], jump_loc[1]+move[1]]
            another_san = self.getSanPosition(jump_loc[0],jump_loc[1])
            another_new_san_position = self.getSanPosition(possible_move[0], possible_move[1])

            if self.checkPotentialJumps(another_new_san_position, player_or_opp):
                jump = self.doJumps(another_san, another_new_san_position, player_or_opp)
                flat_list = [item for sublist in jump for item in sublist]
                jump_list.append(flat_list)
            else:
                print("no jumps at", possible_move)
                continue

        return jump_list

    def getJumps(self, current_san_position, new_san_position, player_or_opp):
        """check if there are any piece types not the same and are diagonal"""
        jump_list = []
        curr_loc = self.getRowColPosition(current_san_position)
        print("current san position", current_san_position)
        blocking_piece_type = self.checkers_position[new_san_position].getPlayerorOpp()
        if blocking_piece_type != player_or_opp:
            opp_piece_loc = self.checkers_position[new_san_position].getGridPosition()
            #print("current location is", curr_loc)
            #print("blocked by opponent", blocking_piece_type, opp_piece_loc)
            manhattan_distance = self.findManhattanDistance(curr_loc, opp_piece_loc)
            #print("manhattan distance is ", manhattan_distance)
            jump_loc = [opp_piece_loc[0]+manhattan_distance[0],opp_piece_loc[1]+manhattan_distance[1]]
            print("jump location", jump_loc)
            san_jump_loc = self.getSanPosition(jump_loc[0], jump_loc[1]) 
            print("san jump location", san_jump_loc)
            moves = self.findLegalMoves(jump_loc[0], jump_loc[1], player_or_opp)
            for move in moves: 
                new_san_jump = self.getSanPosition(move[0], move[1])
                print("new san jump", new_san_jump)
                if self.checkPotentialJumps(new_san_jump, player_or_opp):
                    jump = self.getJumps(san_jump_loc, new_san_jump, player_or_opp)
                    flat_list = [item for sublist in jump for item in sublist]
                    jump_list.append(flat_list)
                else:
                    print("no extra jumps")
            print("san position for jump loc", san_jump_loc)
            jump_list.append((jump_loc))
            #set this as new location and then apply method to check diagonals
            #apply recursion with checkPotentialJumps if there is an opponent player
                    
            #self.checkPotentialJumps(san_jump_loc)
            print(jump_list)
            return jump_list
        else:
            print("blocked", blocking_piece_type)
            return jump_list

    def findLegalMoves(self, row,col, player_or_opp):
        """need to refactor this and check if move is out of bounds"""
        current_loc = [row,col]
        legal_moves = []

        opponent_move_list = [[1, -1], #move diag left
                            [1, 1]] #move diag right

        player_move_list = [[-1, -1], #move diag left
                            [-1, 1]]  #move diag right

        if player_or_opp == "Opponent":
            moves_list = opponent_move_list 
        else:
            moves_list = player_move_list

        for move in moves_list:
            possible_move = [row+move[0], col+move[1]]
            current_san_position = self.getSanPosition(row,col)
            new_san_position = self.getSanPosition(possible_move[0], possible_move[1])

            #check if in bounds
            if not self.checkInBounds(possible_move):
                continue 
            
            #check for potential kills
            if self.checkPotentialJumps(new_san_position, player_or_opp):
                jump = self.doJumps(current_san_position, new_san_position, player_or_opp)
                #unpack list
                #flat_list = [item for sublist in jump for item in sublist]
                #legal_moves.append(jump)
                legal_moves.extend(jump)
                print("jump list", jump)
            #check if new position is blocked
            if new_san_position in self.checkers_position:
                continue
            
            legal_moves.append((possible_move[0],possible_move[1]))
 
        return legal_moves

    def checkCorrectTurn(self, piece_type, is_player_turn):
        """check if piece type is the player turn"""
        if piece_type == "Player" and is_player_turn == True:
            return True
        elif piece_type == "Opponent" and is_player_turn == False:
            return True
        else:
            return False

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

    def getSanPosition(self):
        """accessor"""
        return self.san_position

    def getGridPosition(self):
        """accessor"""
        return self.grid_position

    def updateSanPosition(self, san_position):
        """update san position in string format"""
        self.san_position = san_position
        return self.san_position
    
    def updateGridPosition(self, grid_loc):
        """update grid position with grid_loc [int_x, int_y]"""
        self.grid_position = grid_loc
        return self.grid_position

    def getPlayerorOpp(self):
        """return Player or Opponent"""
        return self.player_or_opp

    def updatePieceType(self):
        """update piece as king"""

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
                        background-color:  #2B5DD1;c
                        padding: 2px;
                    }
                    QPushButton::hover{
                        background-color : lightgreen;
                    }
                    """)

        #self.setStyleSheet('background-color: rgb(255,255,255)')
        self.setStyleSheet(styleSheet)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
        """need to rename the dictionaries"""
        self.drawBoard(self.checkersGame.rank, self.checkersGame.reverse_file)
        self.checkersGame.checkers_position = self.placeCheckers(self.checkersGame.sans_mapping)

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
        piece_info = {}
        row, col = square_dict['a1']
        piece_label = Checker(self, san_position='a1', grid_position=[row,col], player_or_opp="Player")
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label    

        row, col = square_dict['b4']
        piece_label = Checker(self,san_position='b4', grid_position=[row,col], player_or_opp="Player")
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label

        row, col = square_dict['e7']
        piece_label = Checker(self,san_position='e7', grid_position=[row,col], player_or_opp="Opponent")
        self.layout.addWidget(piece_label, row, col)
        piece_info[piece_label.san_position] = piece_label

        row, col = square_dict['c5']
        piece_label = Checker(self,san_position='c5', grid_position=[row,col], player_or_opp="Opponent")
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
                new_san_position = self.checkersGame.getSanPosition(new_row, new_col)
                new_checker = Checker(self, new_san_position, [new_row, new_col], piece.player_or_opp)
                #update position of checker
                self.checkersGame.updateCheckerPosition(new_checker, piece)
                # update the position in the GUI 
                self.layout.addWidget(new_checker, new_row, new_col) 
                
                #set toggle on button to false since we made a move 
                self.toggle_on = False
                self.switchTurns()
                
        self.deleteMoves()

    def switchTurns(self):
        self.playerTurn = not self.playerTurn
        print("Player turn is", self.playerTurn)

    def deleteMoves(self):
        """delete moves button after piece is set"""
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
            #get San Location
            san_location = self.checkersGame.row_col_mapping[curr_row,curr_col]
            
            """Need to refactor this """
            #check if piece exists and it correlates to the correct piece turn type
            if self.checkersGame.checkCheckerExists(san_location):
                piece = self.checkersGame.checkers_position[san_location]
                print("piece position:", piece.san_position)
                #check if correct piece based on turn is selected
                if self.checkersGame.checkCorrectTurn(piece.player_or_opp, self.playerTurn):
                    moves_row_col = self.checkersGame.findLegalMoves(curr_row,curr_col, piece.player_or_opp)
                    print(moves_row_col)
                    if moves_row_col:
                        #show legal moves in the game
                        self.showMoves(moves_row_col,piece, curr_row, curr_col)
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
                moves_row_col = self.checkersGame.findLegalMoves(curr_row,curr_col, piece.player_or_opp)
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

