#!/usr/bin/env python

import sys
import math as m
import numpy as np

class CheckerPieceTest():
    def __init__(self,color, player_or_opp, row_indx, col_indx):
        self.color = color #string red or black
        self.player_or_opp = player_or_opp
        self.loc = [row_indx, col_indx] #[row,col]

class BoardTest():
    def __init__(self, row_size, col_size):
        self.board = self.drawBoard(row_size, col_size)

    def drawBoard(self, row_size,col_size):
        """return board"""
        if self.isBoardSizeValid(row_size, col_size):
            board = np.zeros((row_size,col_size))
            return board

    def isBoardSizeValid(self,row_size,col_size):
        """returns false if board has a negative value or is greather than 7"""
        if (row_size<0 or row_size>7) or (col_size<0 or col_size>7):
            return False
        else:
            return True 

    def placePiece(self, row_loc, col_loc):
        piece = CheckerPieceTest("black", "Opponent", row_loc, col_loc)
        self.board[row_loc, col_loc] = 1
        print(self.board)
        return piece

    def findMoves(self,current_loc, player_or_opp):
        """indicate the possible legal moves the checkerpiece can make
        based on its location, check if black or red
        current_loc = int [row, col] --> [y,x] location on board
        player_or_opp = string input of Opponent or Player
        """
        
        """
        make sure moves are diagonal - X
        make sure moves are not out of bounds -X 
        make sure moves are within bounds - X
        make sure moves are not horizontal or vertical -X
        if king you can go backwards or forwards diagonlly, if regular only forward
        """
        #show all moves
        #then move any that are not legal
        #then show on board
        #if opponent row goes down so we add  
        if player_or_opp == "Opponent":
            leg_move_1 = [current_loc[0] + 1, current_loc[1]-1] #move left
            leg_move_2 = [current_loc[0] + 1, current_loc[1]+1] #move right
            moves_list = [leg_move_1, leg_move_2]
            #legal_moves = [lst for lst in moves if (lst[moves]<=0 or lst[moves]>=7) in lst]
            for index, moves in enumerate(moves_list):
                if (moves[0] <= -1) or (moves[0]>=8) or (moves[1] <= -1) or (moves[1]>=8):
                    moves_list.pop(index)
        #other wise it is a player
        else:
            leg_move_1 = [current_loc[0] - 1, current_loc[1]-1] #move left subtract instead
            leg_move_2 = [current_loc[0] - 1, current_loc[1]+1] #move right
            moves_list = [leg_move_1, leg_move_2]
            for index, moves in enumerate(moves_list):
                if (moves[0] <= -1) or (moves[0]>=8) or (moves[1] <= -1) or (moves[1]>=8):
                    print("removing", moves)
                    moves_list.pop(index)
        
        legal_moves = moves_list
        print("moves are",legal_moves)
        return legal_moves

if __name__ =='__main__':
    boardTest = BoardTest(7,7)
    opponent_pieceTest = boardTest.placePiece(2,1)
    legal_moves = boardTest.findMoves(opponent_pieceTest.loc, opponent_pieceTest.player_or_opp)
    print(legal_moves)