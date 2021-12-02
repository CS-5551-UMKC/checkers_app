import sys
sys.path.append("..")
import unittest
from checkers_app.board import CheckersGame

class CheckersPiece():
    """testing if winner"""
    def __init__(self) -> None:
        pass
    
    def get_piece_type(self):
        pass

    def isKing(self):
        pass

class TestCheckersPosition(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.checkersGame = CheckersGame()
        self.checkers_position = self.checkersGame.checkers_position

    @classmethod
    def tearDown(self):
        print("Tearing down testcase")

    def test_winner(self):
        """build a hashtable of checkerpieces with attribute of opponent or player"""

    