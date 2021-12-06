from copy import deepcopy

class CheckersGame():
    """this class drives the rules of the game"""
    def __init__(self):
        self.grid_size = 8
        self.rank = '12345678'
        self.reverse_rank = '87654321'
        self.file = 'abcdefgh'
        self.reverse_file = 'hgfedcba' 
        self.getMapping()

        self.checkers_position = {}

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

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

    def getCheckersPosition(self):
        """accessor"""
        return self.checkers_position

    def getAllPiecesType(self, player_or_opp):
        """loop through list and get all pieces based on player_or_opp type"""
        piece_list = []
        for key, checker in self.checkers_position.items():
            if checker.getPlayerorOpp() == player_or_opp:
                piece_list.append(checker)
        
        return piece_list

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
            #print("Piece type is", piece.getPlayerorOpp())
            if piece.getPlayerorOpp() ==  opposition:
                #print("still have opposition of", opposition)
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
        returns a list of of row,col location of the potential kill"""
        kill_moves = []
        killed_opponents = []
        moves_list = self.getMovesList(player_or_opp, is_king)
        
        for move in moves_list:
            possible_move = [row+move[0], col+move[1]]
            current_san_position = self.getSanPosition(row,col)
            new_san_position = self.getSanPosition(possible_move[0], possible_move[1])

            #check for potential kills
            if self.checkPotentialKills(new_san_position, player_or_opp):
                #print("potential kills", new_san_position)
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
        else:
            return False

    def doKills(self, current_san_position, new_san_position, player_or_opp, is_king):
        """return location of the jump kill and the location of the piece that will be killed"""
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