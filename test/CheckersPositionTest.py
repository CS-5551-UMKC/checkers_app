import sys
sys.path.append("..")
import unittest
from checkers_app.board import CheckersGame

class CheckersPositionTest(unittest.TestCase):
    
    @classmethod
    def setUp(self):
        self.checkersGame = CheckersGame()
        self.checkers_position = self.checkersGame.checkers_position

    @classmethod
    def tearDown(self):
        print("Tearing down testcase")

    def test_valid_playercheckCorrectPiece(self):
        """A.C 5.1"""
        is_player_turn = True 
        piece_type = "Player"
        result = self.checkersGame.checkCorrectPiece(piece_type, is_player_turn)
        self.assertTrue(result, msg="It is the Player's Turn")

    def test_invalid_opponentcheckCorrectPiece(self):
        """A.C 5.2"""
        is_player_turn = False 
        piece_type = "Opponent"
        result = self.checkersGame.checkCorrectPiece(piece_type, is_player_turn)
        self.assertTrue(result, msg="It is the Opponents Turn")

    def test_invalid_playerPiece(self):
        """A.C 5.3"""
        turn = False
        piece_type = "Player"
        result = self.checkersGame.checkCorrectPiece(piece_type, turn)
        self.assertFalse(result, msg="Wrong Piece Selected")

    def test_invalid_opponentPiece(self):
        """A.C 5.4"""
        turn = True
        piece_type = "Opponent"
        result = self.checkersGame.checkCorrectPiece(piece_type, turn)
        self.assertFalse(result, msg="Wrong Piece Selected")

    def test_successful_getSanPosition(self):
        """AC 11.1"""
        row = 0
        col = 0
        result = self.checkersGame.getSanPosition(row,col)
        msg = "bueno"
        self.assertEqual(result, "a8", msg)

    def test_invalid_getSanPosition(self):
        """AC 11.2""" 
        row = 8
        col = 1
        result = self.checkersGame.getSanPosition(row,col)
        msg = "No bueno"
        self.assertEqual(result, None, msg)


if __name__=='__main__':
    unittest.main()