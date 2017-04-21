#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#
# Copyright 2008, 2009 Pablo Moleri
# This file is part of Quinteti.
#
# Quinteti is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Quinteti is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Quinteti.  If not, see <http://www.gnu.org/licenses/>.

"""GamesState, keeps the state of a game, and encloses game logic."""

import random

class GameState:

    def __init__(self, player_1, player_2, matrix_size=3, target_score=15):
        ''' Creates a new game with the given players. '''
        
        self.player_1_name = player_1
        self.player_2_name = player_2
        self.player_1_score = 0
        self.player_2_score = 0
        self.turn = 1
        self.target_score = target_score
        self.matrix = []
        self.state = []
        for i in range(0, matrix_size):
            self.matrix.append([])
            self.state.append([])
            for j in range(0, matrix_size):
                self.matrix[i].append(0)
                self.state[i].append(None)
        self.numbers = range(1, len(self.matrix[0])*len(self.matrix)+1)
    
    def fromString(string):
        """A static method for loading a new game from a serialized game string."""
        
        dic = eval(string)
        state = dic['state']
        matrix = dic['matrix']
        size = len(matrix)
        game = GameState(dic['player_1_name'], dic['player_2_name'], size, dic['target_score'])
        game.matrix = matrix
        game.state = state
        game.player_1_name = dic['player_1_name']
        game.player_2_name = dic['player_2_name']
        game.player_1_score = dic['player_1_score']
        game.player_2_score = dic['player_2_score']
        
        #Saca los numeros jugados:
        for row in game.matrix:
            for number in row:
                if number in game.numbers:
                    game.numbers.remove(number)
        return game
    
    fromString = staticmethod(fromString)    # Maps the function as an static class attribute
    
    def serialization(self):
        """Returns the game in a serialized string format."""
        
        return str(self)
    

    def get_cell(self, row1, col1):
        """Returns the cell state: (number, player) Or None."""
        row, col = row1-1, col1-1
        return (self.matrix[row][col], self.state[row][col])
    
    def get_available_numbers(self): 
        """Returns the list of available numbers (no played)."""
        
        return self.numbers
    
    def make_move(self, row1, col1, number, player):
        """Makes a move with the given number in the given cell.
        
        Returns a boolean if the move is valid and the score difference.
        """
        
        ok, hits, score = self._make_move(row1, col1, number, player, True)
        return ok, hits
    
    def _make_move(self, row1, col1, number, player, real):
        """Makes a move with the given number in the given cell.
        
        Returns a boolean if the move is valid and the score difference.
        """
        
        row, col = (row1-1, col1-1)
        if (self.state[row][col] == None):
            if (self.turn == player):
                if (number in self.numbers):
                    # shadow copy of the given column
                    col_list = [fila[col] for fila in self.matrix]
                    
                    # shadow copy of the given row
                    row_list = self.matrix[row][:]
                    
                    hits = []   # collection of posistions that made points
                    
                    # Test the move
                    col_score = self._check_action(col_list, row, number)                        
                    row_score = self._check_action(row_list, col, number)
                    score = col_score + row_score
                    
                    if col_score:
                        hits.extend(col_list)
                    
                    if row_score:
                        hits.extend(row_list)
                    
                    if real:
                        self.state[row][col] = self.turn
                        self.matrix[row][col] = number
                        self.numbers.remove(number)
                            
                        if self.turn == 1:
                            self.player_1_score += score
                            self.turn = 2
                        else:
                            self.player_2_score += score
                            self.turn = 1
                    return True, hits, score
#                else:
#                    print "invalid number"
#            else:
#                print "invalid player"
#        else:
#            print "invalid cell state"
        
        return False, None, 0
    
    def _check_action(self, list, pos, number):
        """Tests if a move in a row (or column) scores."""
        
        list[pos] = number
        if 0 in list:
            return 0
        if sum(list) == self.target_score:
            return 1
        else:
            return 0
            
    def get_enabled_player(self):
        """Returns the turn (enabled player) or None if the game is over."""
        if len(self.numbers) == 0:
            return None
        else:
            return self.turn
        
    def get_player_score(self, player):
        if player == 1 :
            return self.player_1_score
        else:
            return self.player_2_score
    
    def get_player_name(self, player):
        if player == 1 : 
            return self.player_1_name
        else:
            return self.player_2_name
    
    def get_player_count(self):
        return 2
    
    def __str__( self ):
        dic = {
               'state': self.state,
               'matrix': self.matrix,
               'player_1_name': self.player_1_name,
               'player_2_name': self.player_2_name,
               'player_1_score': self.player_1_score,
               'player_2_score': self.player_2_score,
               'target_score': self.target_score}
        return str(dic)   

    
    def auto_play(self, player):
        '''Returns an automatic play from computer.
        
        The strategy is:
            - Try to make 2 points.
            - Try to make 1 point.
            - Try to make a move that enables two different points (make tha game more interesting).
            - Random move that doesn't enable the other player to make a point.
            - Random move.
        '''
        
        options = [(row, col)
                    for row in range(1, len(self.matrix) + 1)
                    for col in range(1, len(self.matrix) + 1)
                    if self.matrix[row-1][col-1] == 0]
        print options

        # Try two points
        for row, col in options:
            for number in self.numbers:
                ok, hits, score = self._make_move(row, col, number, player, False)
                if score >= 2:
                    return (number, row, col)

        # Try one point
        for row, col in options:
            for number in self.numbers:
                ok, hits, score = self._make_move(row, col, number, player, False)
                if score >= 1:
                    return (number, row, col)
        
        # Random
        row, col = random.choice(options)
        number = random.choice(self.numbers)
        return (number, row, col)


if __name__ == "__main__":
    """Module test function."""
    
    game = GameState("Juan", "Pablo")
    print game.target_score
    
    game.make_move(0, 1, 2, 1)
    game.make_move(1, 1, 7, 2)
    game.make_move(2, 1, 6, 1)
    
    print game
    
    game2 = GameState.fromString( game.serialization() )
    print 'game2 %s' % (game)
    print game2.get_player_name(1)
