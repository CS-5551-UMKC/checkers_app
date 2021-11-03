import sys
sys.path.append("..")
import unittest
from checkers_app.board import CheckersGame

class TestCheckersGame(unittest.TestCase):
    
    @classmethod
    def setUp(self):
        self.checkersGame = CheckersGame()
        self.checkers_position = self.checkersGame.checkers_position

    @classmethod
    def tearDown(self):
        print("Tearing down testcase")

    def test_getRowColKey(self):
        
        pass

    def test_getRowColKey(self):
        pass

    def test_successful_getSanPosition(self):
        """Justin Nguyen """
        row = 0
        col = 0
        result = self.checkersGame.getSanPosition(row,col)
        msg = "No bueno"
        self.assertEqual(result, "a8", msg)

    def test_invalid_getSanPosition(self):
        """bad situation""" 
        row = 8
        col = 1
        result = self.checkersGame.getSanPosition(row,col)
        msg = "No bueno"
        self.assertEqual(result, None, msg)

    def test_valid_playercheckCorrectTurn(self):
        is_player_turn = True 
        piece_type = "Player"
        result = self.checkersGame.checkCorrectTurn(piece_type, is_player_turn)
        self.assertTrue(result, msg="It is the Opponents Turn")

    def test_invalid_opponentcheckCorrectTurn(self):
        is_player_turn = False 
        piece_type = "Opponent"
        result = self.checkersGame.checkCorrectTurn(piece_type, is_player_turn)
        self.assertTrue(result, msg="It is the Opponents Turn")

    def test_invalid_playercheckCorrectTurn(self):
        """it is the opponents Turn but player piece is selected"""
        turn = False
        piece_type = "Player"
        result = self.checkersGame.checkCorrectTurn(piece_type, turn)
        self.assertFalse(result, msg="It is the Opponents Turn")

if __name__=='__main__':
    unittest.main()