import sys
sys.path.append("..")
import unittest
from checkers_app.board import CheckersGame

class CheckersPiece():
    def __init__(self, grid_position, player_or_opp):
        self.grid_position = grid_position
        self.player_or_opp = player_or_opp
    
    def getPlayerorOpp(self):
        return self.player_or_opp

    def getPos(self):
        return self.grid_position
        
    def isKing(self):
        return self.king

    def updatePos(self, row, col):
        self.grid_position = [row, col]

class TestGameState(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.checkersGame = CheckersGame()
        self.checkers_position = self.checkersGame.checkers_position
    
    #AC 7.1 Game ends with Red/Player Win | Assert player win is true and opp win is None
    def test_player_win(self):
        checkersGame = CheckersGame()
        new_checker = CheckersPiece([0, 7], "Player")
        checkersGame.checkers_position = {
            "1": new_checker
        }

        self.assertEqual(checkersGame.checkWinner("Player"), True)
        self.assertEqual(checkersGame.checkWinner("Opponent"), None)

    #AC 7.2 Game ends with red/player win | Assert player win is true and opp win is None
    def test_opponent_win(self):
        checkersGame = CheckersGame()
        new_checker = CheckersPiece([1, 1], "Opponent")
        checkersGame.checkers_position = {
            "1": new_checker
        }

        self.assertEqual(checkersGame.checkWinner("Opponent"), True)
        self.assertEqual(checkersGame.checkWinner("Player"), None)

    #Extra test for reassurance: No winner yet | Assert None for player win and opp win 
    def test_no_win(self):
        checkersGame = CheckersGame()
        new_checker1 = CheckersPiece([1, 1], "Player")
        new_checker2 = CheckersPiece([1, 2], "Opponent")
        checkersGame.checkers_position = {
            "1": new_checker1,
            "2": new_checker2
        }

        self.assertEqual(checkersGame.checkWinner("Player"), None)
        self.assertEqual(checkersGame.checkWinner("Opponent"), None)


    #AC 12.1 Player/red piece becomes king | Assert checkKing is True for player piece
    def test_check_king_player(self):
        checkersGame = CheckersGame()
        new_checker = CheckersPiece([1, 7], "Player")
        checkersGame.checkers_position = {
            "1": new_checker
        }
        #Not at end of board yet
        self.assertEqual(checkersGame.checkKing(new_checker.getPlayerorOpp(), new_checker.getPos()[0]), False)
        #Move to end of board
        new_checker.updatePos(0, 7) 
        #Now checkKing should return true
        self.assertEqual(checkersGame.checkKing(new_checker.getPlayerorOpp(), new_checker.getPos()[0]), True)
    
    #AC 12.2 Opponent/black piece becomes king | Assert checkKing is True for opponent piece
    def test_check_king_opp(self):
        checkersGame = CheckersGame()
        new_checker = CheckersPiece([6, 0], "Opponent")
        checkersGame.checkers_position = {
            "1": new_checker
        }
        #Not at end of board yet
        self.assertEqual(checkersGame.checkKing(new_checker.getPlayerorOpp(), new_checker.getPos()[0]), False)
        #Move to end of board
        new_checker.updatePos(7, 0) 
        #Now checkKing should return true
        self.assertEqual(checkersGame.checkKing(new_checker.getPlayerorOpp(), new_checker.getPos()[0]), True)
      
    @classmethod
    def tearDown(self):
        print("Tearing down testcase")

    