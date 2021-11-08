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


if __name__=='__main__':
    unittest.main()
