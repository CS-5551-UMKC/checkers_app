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

    def successful_getSanPosition(self):
        """Justin Nguyen """
        row = 0
        col = 0
        result = self.checkersGame.getSanPosition(row,col)
        msg = "No bueno"
        self.assertEqual(result, "a8", msg)

    def invalid_getSanPosition(self):
        """bad situation"""
        row = 8
        col = 1
        result = self.checkersGame.getSanPosition(row,col)
        msg = "No bueno"
        self.assertEqual(result, None, msg)

if __name__=='__main__':
    unittest.main()