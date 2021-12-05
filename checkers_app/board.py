from abc import abstractproperty
from copy import deepcopy

import sys
import math 
from itertools import cycle
import pickle
#import cPickle

import CheckersGame

from PyQt5.QtCore import (QSize, Qt,QRect)
from PyQt5.QtGui import (QPainter, QPixmap)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout, 
                            QWidget, QHBoxLayout, QTableWidget,
                            QMainWindow, QPushButton,QSizePolicy, QMessageBox)

from pprint import pprint


            
class CheckerModel():
    """checker model """
    def __init__(self, san_position, grid_position, player_or_opp, is_king):

        self.san_position = san_position
        self.grid_position = grid_position
        self.player_or_opp = player_or_opp #string 'Player' 'Opponent'
        self.king = is_king
      
    def isKing(self):
        """accessor"""
        return self.king

    def setKing(self, bool_statement):
        """set king as true"""
        self.king = bool_statement

    def getSanPosition(self):
        """accessor"""
        return self.san_position

    def getGridPosition(self):
        """accessor"""
        return self.grid_position

    def getPlayerorOpp(self):
        """return Player or Opponent"""
        return self.player_or_opp
    
class CheckerPixMap(QPixmap):
    def __init__(self,image):
        super(CheckerPixMap).__init__()
        self.image = image

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

class Checker(QDialog):
    """might make this custom paint and determine if player or oppponent"""
    def __init__(self, parent, san_position, grid_position, player_or_opp, is_king):
        super().__init__()
        
        # Make label transparent, so square behind piece is visible
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(32, 32)
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
        self.setStyleSheet(styleSheet)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

"""should this classs inherit moves button? only change the stylesheet and have victims"""
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
        
class Opponent():
    """opponent class can be human or opponent"""
    def __init__(self):
        pass

    def evaluate(self, gameEngine):
        """evaluate the game state score"""
        opponents = gameEngine.getAllPiecesType("Opponent")
        players =  gameEngine.getAllPiecesType("Player")
        opponent_kings = self.findKings(opponents)
        player_kings = self.findKings(players) 
        cost = len(opponents) - len(players) + ((len(opponent_kings)*0.5) - (len(player_kings)*0.5))

        return cost

    def findKings(self, piece_list):
        """find how many kings there are"""
        kings = []
        for piece in piece_list:
            if piece.isKing() == True:
                kings.append(piece)
                #print("king pieces", piece.isKing(), piece.getPlayerorOpp(), piece.getSanPosition())
        return kings

    def miniMax(self, gameEngine, depth, max_player, gameController):
        """apply minimax with recursion"""
        if depth == 0 or gameEngine.checkWinner(max_player) == True:
            return self.evaluate(gameEngine), gameEngine

        if max_player:
            max_evaluation = float('-inf')
            print("ai calculating MAX")
            best_move = None
            best_position = None
            old_position = None
            moves, updated_piece, old_piece = self.getAllMoves(gameEngine, "Opponent", gameController)
            for idx, move in enumerate(moves):
                new_board_state = self.miniMax(move, depth-1, False, gameController)
                max_evaluation = max(max_evaluation, new_board_state[0])
                if max_evaluation == new_board_state[0]:
                    best_move = move #board
                    best_position = updated_piece[idx] # position
                    old_position = old_piece[idx]

            print("BEST MAX MOVE IS ", best_position.getSanPosition())
            return max_evaluation, best_move, best_position, old_position
        else: 
            min_evaluation = float('inf')
            print("ai calculating MIN")
            best_move = None
            best_position = None
            moves, updated_piece, old_piece = self.getAllMoves(gameEngine, "Player", gameController)
            for idx, move in enumerate(moves): 
                new_board_state = self.miniMax(move, depth-1, True, gameController)
                min_evaluation = min(min_evaluation, new_board_state[0])
                if min_evaluation == new_board_state[0]:
                    best_move = move #board
                    best_position = updated_piece[idx] #position
                    old_position = old_piece[idx]

            print("BEST MIN MOVE IS ", best_position.getSanPosition())
            return min_evaluation, best_move, best_position, old_piece
            
    def getAllMoves(self, gameEngine, player_or_opp, gameController):
        """get all moves"""
        possible_moves = []
        updated_pieces = []
        prev_pieces = []
        for piece in gameEngine.getAllPiecesType(player_or_opp):
            current_loc = piece.getGridPosition()
            current_san = gameEngine.getSanPosition(current_loc[0], current_loc[1])
            moves_list =  gameEngine.findLegalMoves(current_loc[0], current_loc[1], player_or_opp, piece.isKing())
            #kill_moves, killed_opps = gameEngine.findPotentialKills(current_loc[0], current_loc[1], player_or_opp, piece.isKing())
            for move in moves_list:
                #print(gameEngine.getCheckersPosition())
                temp_board = deepcopy(gameEngine) #deepcopy(gameEngine.getCheckersPosition())
                #print("location of board", temp_board.checkers_position.keys())
                checkers_position = temp_board.getCheckersPosition()
                temp_piece = checkers_position[current_san]
                print("current position is", temp_piece.getSanPosition())
                new_board, new_position = self.simulateMove(temp_piece, move, temp_board, gameController)
                updated_pieces.append(new_position)
                possible_moves.append(new_board)
                prev_pieces.append(temp_piece)

        return possible_moves, updated_pieces, prev_pieces

    def simulateMove(self, temp_piece, move, temp_board, gameController):
            #temp_piece.setParent(None)
            updated_checker, updated_checker_model = gameController.updatePiece(temp_piece, move[0], move[1])
            if updated_checker.isKing() == True:
                print("Have a king", updated_checker_model.getSanPosition())            #print("new potential position: ", updated_checker_model.getSanPosition())
            temp_board.updateCheckerPosition(updated_checker_model, temp_piece)

            return temp_board,  updated_checker_model

class QBoardLayout(QGridLayout):
    def __init__(self):
         super(QBoardLayout,self).__init__()

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

class BoardController(QFrame):
    """Define this as ViewController
    need to map row,col to Sans
    map Sans to row,col 
    need to show occupied board 
    is the piece selected?
    if so what is its position
    what is the neighboring positions
    """

    def __init__(self):
        super(BoardController,self).__init__()
        #define layout of controller
        self.layout = QBoardLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)    
        
        #Composition create instance of Checkers
        self.checkersGame = CheckersGame.CheckersGame()
        #finalize the layout
        self.setLayout(self.layout)
        
        self.visualizeBoard()
        self.playerTurn = True
        self.toggle_on = False
        """need to figure out a better way to format this"""
        self.opponent = Opponent()

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def returnState(self):
        return self

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
        self.board_gui, self.gameboard = self.initBoard()
        self.checkersGame.initCheckers(self.gameboard)

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

    def appendPieces(self, init_row, final_row, gui_board, game_board, player_or_opp):
        """set pieces to board """
        size_list = [0,1,2,3,4,5,6,7]
        for row, row_loc in enumerate(size_list[init_row:final_row]):
            for col, col_loc in enumerate(size_list):
                if (row_loc + col_loc) % 2 == 1:
                    file_rank = self.checkersGame.getSanPosition(row_loc,col_loc)
                    piece_label = Checker(self, file_rank, [row_loc,col_loc], player_or_opp, False)
                    piece_model = CheckerModel(file_rank, [row_loc,col_loc], player_or_opp, False)
                    gui_board[piece_label.san_position] = piece_label
                    game_board[piece_model.san_position] = piece_model
                    self.layout.addWidget(piece_label, row_loc, col_loc)

    def initBoard(self):
        """refactor this code:
        GUI will recieve the information of the CheckersPiece and place it accordingly"""
        gui_board_layout = {}
        game_board = {}
        player_rows = [5,8]
        opponent_rows = [0,3]
        self.appendPieces(player_rows[0], player_rows[1], gui_board_layout, game_board, "Player")
        self.appendPieces(opponent_rows[0], opponent_rows[1], gui_board_layout, game_board, "Opponent")

        return gui_board_layout,game_board

    def showMoves(self, moves_row_col, piece, curr_row, curr_col):
        """show legal moves on the GUI where player can select , if they select it then we send a signal
        to update the position of the board and move it respectively"""
        for moves in moves_row_col:
            print("moves: ", moves)
            san_position = self.checkersGame.getSanPosition(moves[0], moves[1])
            indicated_move = MovesButton(self, san_position, moves)
            indicated_move.clicked.connect(lambda: self.movePiece(piece, curr_row, curr_col)) 
            self.layout.addWidget(indicated_move, moves[0], moves[1])

    def updatePiece(self, piece, new_row, new_col):
        """update checker piece whether it is a king or not king"""
        was_king = piece.isKing()
        new_san_position = self.checkersGame.getSanPosition(new_row, new_col)

        if self.checkersGame.checkKing(piece.player_or_opp, new_row) or was_king:
            print("updating as king", new_san_position, piece.player_or_opp)
            updated_checker = Checker(self, new_san_position, [new_row, new_col], piece.player_or_opp, True)
            updated_checker_model = CheckerModel(new_san_position, [new_row, new_col], piece.player_or_opp, True)
        else:
            updated_checker = Checker(self, new_san_position, [new_row, new_col], piece.player_or_opp, False)
            updated_checker_model = CheckerModel(new_san_position, [new_row, new_col], piece.player_or_opp, False)

        return updated_checker, updated_checker_model

    def aiUpdatePiece(self, old_piece_model, new_piece_model):
        """update board from AI change and also in the GUI"""
        print("old piece model", old_piece_model)
        was_king = old_piece_model.isKing()
        new_row_col_position = self.checkersGame.getRowColPosition(new_piece_model.getSanPosition())
        
        if self.checkersGame.checkKing("Opponent", new_row_col_position[0]) or was_king == True:
            print("setting to king")
            new_piece_model.setKing(True)
        else:
            new_piece_model.setKing(False)
            
        return new_piece_model 

    def aiMove(self,old_piece, new_piece_model):
        """update board from AI change and also in the GUI"""
        print("searching")
        san_position = new_piece_model.getSanPosition()
        new_row_col_position = new_piece_model.getGridPosition()
        piece_list = self.findChildren(QDialog)
        for piece in piece_list:
            print("search pieces for", old_piece.getGridPosition())
            print(piece.grid_position)
            if piece.grid_position == old_piece.getGridPosition():
                print("found it")
                piece.setParent(None)
                print(new_piece_model.isKing())
                updated_checker = Checker(self, san_position, new_row_col_position, "Opponent", new_piece_model.isKing())
                self.checkersGame.updateCheckerPosition(new_piece_model, old_piece)
                # update the position in the GUI 
                self.layout.addWidget(updated_checker, new_row_col_position[0], new_row_col_position[1]) 
                #set toggle on button to false since we made a move 
                self.toggle_on = False  
                self.switchTurns()

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
                updated_checker, updated_checker_model = self.updatePiece(piece, new_row, new_col)
                #update position of checker
                self.checkersGame.updateCheckerPosition(updated_checker_model, piece)
                # update the position in the GUI 
                self.layout.addWidget(updated_checker, new_row, new_col) 
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

    def returnVictims(self, kill_button, opp_locs):
        """return victim list from kill button"""
        victim_list = []
        if kill_button.getVictims() == 0:
            victim_list.append(opp_locs[kill_button.getVictims()])
            print("victim list", victim_list)

        return victim_list

    def executeKill(self, piece, curr_row, curr_col, opp_locs):
        """ get the location button selected """
        kill_button = self.sender()
        idx = self.layout.indexOf(kill_button)
        new_location = self.layout.getItemPosition(idx)
        new_row = new_location[0]
        new_col = new_location[1]
        victim_list = self.returnVictims(kill_button, opp_locs)

        piece_list = self.findChildren(Checker)
        for piece in piece_list:
            #want to delete the piece from the previous location
            if piece.grid_position == [curr_row, curr_col]:
                piece.setParent(None) # delete the previous position
                updated_checker, updated_checker_model = self.updatePiece(piece, new_row, new_col)
                self.removePiece(victim_list)
                self.checkersGame.updateCheckerPosition(updated_checker_model, piece)
                self.layout.addWidget(updated_checker, new_location[0], new_location[1]) 
                # check gamestate here
                if self.checkersGame.checkWinner(piece.getPlayerorOpp()) == True:
                    print("Winner is :", piece.getPlayerorOpp())
                    self.showWinner(piece.getPlayerorOpp())

                self.deleteMoves(KillMovesButton)        
                self.deleteMoves(MovesButton)

                #set toggle on button to false since we made a move 
                kill_moves, opponent_locs = self.checkersGame.findPotentialKills\
                    (new_row, new_col, updated_checker.player_or_opp, updated_checker.isKing())
                if kill_moves:
                    print("potentail kills " ,kill_moves)
                    self.showKills(kill_moves, opponent_locs, updated_checker, new_row, new_col)
                else:
                    self.toggle_on = False
                    self.switchTurns()
                    
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
        print(piece_list)
        for piece in piece_list:
            if piece.grid_position in piece_removed_list:
                #remove from GUI and remove from checkers position game engine
                san_pos = self.checkersGame.getSanPosition(piece.grid_position[0],piece.grid_position[1])
                self.checkersGame.removeCheckerPiece(san_pos)
                piece.setParent(None)
                print("Removed piece")

    def switchTurns(self):
        """switch turns to either opponent or player"""
        self.playerTurn = not self.playerTurn
        print("Player turn is", self.playerTurn)

    def deleteMoves(self, button_type):
        """delete moves button after piece is set"""
        moves_button = self.findChildren(button_type)
        for button in moves_button:
            button.setParent(None)

    def turn_off_shown_moves(self, san_location):
        """toggle off the buttons selected"""
        if self.checkersGame.checkCheckerExists(san_location):
            self.toggle_on = False
            self.deleteMoves(KillMovesButton)
            self.deleteMoves(MovesButton) 

    def mousePressEvent(self, event):
        """this is what happens if the board is selected"""            
        if self.playerTurn == False: 
            updated_board = self.opponent.miniMax(self.checkersGame, 2, "Opponent",self)
            new_piece = updated_board[2]
            old_piece = updated_board[3]
            print("old piece position", old_piece.isKing())
            print("new piece position", new_piece.getSanPosition())
            new_piece_model = self.aiUpdatePiece(old_piece, new_piece)
            self.aiMove(old_piece, new_piece_model)

        if event.button() == Qt.LeftButton and self.toggle_on==False:
            self.pressPos = event.pos().x()
            curr_row,curr_col = self.getRowColFromPixel(event.pos().x(), y = event.pos().y())
            san_location = self.checkersGame.row_col_mapping[curr_row,curr_col]
            """Need to refactor this """
            #check if piece exists and it correlates to the correct piece turn type
            if self.checkersGame.checkCheckerExists(san_location):
                piece = self.checkersGame.checkers_position[san_location]
                print("is it a king?", piece.isKing())
                if self.checkersGame.checkCorrectPiece(piece.player_or_opp, self.playerTurn):
                    """should break this down to a method"""
                    kill_moves, opponent_locs = self.checkersGame.findPotentialKills(curr_row, curr_col, \
                        piece.player_or_opp, piece.isKing())
                    moves_row_col = self.checkersGame.findLegalMoves(curr_row,curr_col,\
                        piece.player_or_opp, piece.isKing())
                    if moves_row_col or kill_moves:
                        #show legal moves in the game
                        self.showMoves(moves_row_col,piece, curr_row, curr_col)
                        self.showKills(kill_moves, opponent_locs, piece, curr_row, curr_col)
                        self.toggle_on = True        
        else:
            self.pressPos = event.pos().x()
            x = event.pos().x()
            y = event.pos().y()
            curr_row,curr_col = self.getRowColFromPixel(x,y)
            san_location = self.checkersGame.row_col_mapping[curr_row,curr_col]
            self.turn_off_shown_moves(san_location)

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

