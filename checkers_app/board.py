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
        self.getMapping()

        self.checkers_position = {}

    def getMapping(self):
        """helper function"""
        self.row_col_mapping = self.getRowColKey()
        self.sans_mapping = self.getSanKey()

    def getSansMap(self):
        """accessor"""
        return self.sans_mapping

    def getRank(self):
        """accessor"""
        return self.rank 

    def getReverseFile(self):
        """accessor"""
        return self.reverse_file

    def getCheckersLayout(self):
        """accessor"""
        return self.checkers_position

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
        position = [row,col]
        if self.checkInBounds(position):
            san_position = self.row_col_mapping[row,col]
            return san_position
        else:
            return None

    def getRowColPosition(self,san_position):
        """returns san position using the row col mapping"""
        row_col_position = self.sans_mapping[san_position]
        return row_col_position 

    def initCheckers(self, initial_layout):
        """layout the checker pieces for the initial game"""
        self.checkers_position = initial_layout

    def checkWinner(self, player_or_opp):
        """figure out winner by checker pieces known, 
        if opposition is not found return True"""
        print("checking winner")
        if player_or_opp == "Player":
            opposition = "Opponent"
        else:
            opposition = "Player"
        
        piece_list = list(self.checkers_position.values())
        for piece in piece_list:
            print("Piece type is", piece.getPlayerorOpp())
            if piece.getPlayerorOpp() ==  opposition:
                print("still have opposition of", opposition)
                break
        else:
            return True

    def updateCheckerPosition(self, new_checker, old_checker):
        """updates the position of the checkers position by removing the previous location of piece
        and updating the piece """
        old_san_position = old_checker.getSanPosition()
        new_san_position = new_checker.getSanPosition()
        #self.checkers_position.pop(old_san_position)
        self.removeCheckerPiece(old_san_position) 
        self.checkers_position[new_san_position] = new_checker 

    def removeCheckerPiece(self, san_position):
        self.checkers_position.pop(san_position)

    def findManhattanDistance(self,curr_loc, opponent_loc):
        """find the manhattan distance and get direction for jumps"""
        dx = opponent_loc[0] - curr_loc[0]
        dy = opponent_loc[1] - curr_loc[1]
        
        return [dx,dy]

    def getMovesList(self,player_or_opp, is_king):
        """return moves possible based on type of piece"""
        basic_opponent_move_list = [[1, -1], #move diag left
                                    [1, 1]] #move diag right

        basic_player_move_list = [[-1, -1], #move diag left
                                [-1, 1]]  #move diag right
        
        """combination of the opponent and player moves"""
        king_move_list = [[-1, -1], 
                        [-1, 1], 
                        [1, -1],
                        [1, 1]] 

        """refactor this as a case switch or maybe put in Piece Class"""
        if player_or_opp == "Opponent" and is_king == False:
            moves_list = basic_opponent_move_list 
        elif player_or_opp == "Opponent" and is_king == True:
            moves_list = king_move_list
        elif player_or_opp == "Player" and is_king == False:
            moves_list = basic_player_move_list
        else:
            moves_list = king_move_list
        
        return moves_list

    def checkInBounds(self,moves):
        """check if move is within bounds if so return True"""
        if ((moves[0]>= 0) and (moves[0]<=7) and (moves[1]>=0) and (moves[1]<=7)):
            return True

    def findPotentialKills(self, row,col, player_or_opp, is_king):
        """find potential kill based on row and location fo player
        returns a list of of row,col locations of potential kill
        uses recursion"""
        kill_moves = []
        killed_opponents = []
        moves_list = self.getMovesList(player_or_opp, is_king)
        print("is it a king?", is_king)
        for move in moves_list:
            possible_move = [row+move[0], col+move[1]]
            current_san_position = self.getSanPosition(row,col)
            new_san_position = self.getSanPosition(possible_move[0], possible_move[1])

            #check for potential kills
            if self.checkPotentialKills(new_san_position, player_or_opp):
                kills, killed_opps= self.doKills(current_san_position, new_san_position, player_or_opp, is_king)
                kill_moves.extend(kills)
                killed_opponents.extend(killed_opps)

        return kill_moves, killed_opponents

    def checkPotentialKills(self,new_san_position,player_or_opp):
        """check new position contains a checker piece
        if checker piece is not the same as the player or opp report
        as potential kill bool True"""
        if new_san_position in self.checkers_position:
            blocking_piece_type = self.checkers_position[new_san_position].getPlayerorOpp()
            if blocking_piece_type != player_or_opp:
                return True

    def doKills(self, current_san_position, new_san_position, player_or_opp, is_king):
        """determines possible jumps and returns it to kill list as row and column index 
        using recursion"""
        kill_moves = []
        killed_opponents = []
        curr_loc = self.getRowColPosition(current_san_position)
        opp_piece_loc = self.checkers_position[new_san_position].getGridPosition()
        manhattan_distance = self.findManhattanDistance(curr_loc, opp_piece_loc)
        jump_loc = [opp_piece_loc[0]+manhattan_distance[0],opp_piece_loc[1]+manhattan_distance[1]]
        
        """check if we are blocked at this jumped location """
        if self.getSanPosition(jump_loc[0], jump_loc[1]) in self.checkers_position:
            return kill_moves, killed_opponents

        """check if the jump will get us out of bounds"""
        if not self.checkInBounds(jump_loc):
            return kill_moves, killed_opponents
 
        #append to initial kill and location of piece
        kill_moves.append((jump_loc))
        killed_opponents.append(opp_piece_loc)

        """recursion"""
        moves_list = self.getMovesList(player_or_opp, is_king)
        for move in moves_list:
            possible_move = [jump_loc[0]+move[0], jump_loc[1]+move[1]]
            another_san = self.getSanPosition(jump_loc[0],jump_loc[1])
            another_new_san_position = self.getSanPosition(possible_move[0], possible_move[1])

            if self.checkPotentialKills(another_new_san_position, player_or_opp):
                kills,opponents = self.doKills(another_san, another_new_san_position, player_or_opp, is_king)
                kill_moves.extend(kills)
                killed_opponents.extend(opponents)
            else:
                print("no jumps at", possible_move)
                continue

        return kill_moves,killed_opponents

    def findLegalMoves(self, row,col, player_or_opp, is_king):
        """find legal moves that are not kills"""
        legal_moves = []
        moves_list = self.getMovesList(player_or_opp, is_king)
        for move in moves_list:
            possible_move = [row+move[0], col+move[1]]
            new_san_position = self.getSanPosition(possible_move[0], possible_move[1])
            #check if in bounds
            if not self.checkInBounds(possible_move):
                continue 
            #check if new position is blocked
            if new_san_position in self.checkers_position:
                continue

            legal_moves.append((possible_move[0],possible_move[1]))
 
        return legal_moves 

    def checkCorrectPiece(self, piece_type, is_player_turn):
        """check if piece type is the player turn"""
        if piece_type == "Player" and is_player_turn == True:
            return True
        elif piece_type == "Opponent" and is_player_turn == False:
            return True
        else:
            return False

    def checkCheckerExists(self, san_location):
        """check if piece position exists in the dictionary"""
        if (san_location) in self.checkers_position:
            return True

    def checkKing(self, player_or_opp, row):
        """if piece reaches opposing board then the checker piece will become king
        so black piece reaches row 7, or rank is 1, red piece is vice versa"""
        if player_or_opp == "Player":
            if row == 0:
                return True
            else:
                return False
        else:
            if row == 7:
                return True
            else:
                return False
    
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
    def __init__(self, parent, san_position, grid_position, victims) :
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
        sans_map = self.checkersGame.getSansMap()
        self.drawBoard(rank_list, reverse_file)
        #self.checkersGame.checkers_position = self.placeCheckers(self.checkersGame.getSansMap())
        init_pieces = self.placeCheckers(sans_map, rank_list, reverse_file)
        pprint(init_pieces)
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

    def placeCheckers(self, sans_map, rank_order, file_order_reverse):
        """refactor this code put this in the CheckersGameEngine:
        GUI will recieve the information of the CheckersPiece and place it accordingly"""
        """refactor this"""
        board_layout = {}
        row_list = [0,1,2,3,4,5,6,7]
        col_list = [0,1,2,3,4,5,6,7]

        for row, row_loc in enumerate(row_list[5:8]):
            for col, col_loc in enumerate(col_list):
                if (row_loc + col_loc) % 2 == 1:
                    file_rank = self.checkersGame.getSanPosition(row_loc,col_loc)
                    piece_label = Checker(self, file_rank, [row_loc,col_loc], "Player", False)
                    board_layout[piece_label.san_position] = piece_label    
                    self.layout.addWidget(piece_label, row_loc, col_loc)

        for row, row_loc in enumerate(row_list[0:3]):
            for col, col_loc in enumerate(col_list):
                if (row_loc + col_loc) % 2 == 1:
                    file_rank = self.checkersGame.getSanPosition(row_loc,col_loc)
                    piece_label = Checker(self, file_rank, [row_loc,col_loc], "Opponent", False)
                    board_layout[piece_label.san_position] = piece_label    
                    self.layout.addWidget(piece_label, row_loc, col_loc)

        return board_layout

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
                if self.checkersGame.checkCorrectPiece(piece.player_or_opp, self.playerTurn):
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

