#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#
# Copyright 2008, 2009 Pablo Moleri, ceibalJAM
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

"""Board represents the game board, and its capable of paint its elements in a given surface."""

import pygame

import os

from logic.game import GameState

from button import Button
from cell import Cell

file_dir = "gui/"

image_fondo = file_dir + "background.png"
image_tablero = file_dir + "tablero.png"
image_null = "nulo.bmp"
image_number = "<N>.png"
image_disabled_number = "<N>selected.png"
image_size = pygame.Rect(0, 0,  97,  97)

new_image_coords = (180,  87)
new_image = "quinteti-new.png"

instructions_coords = (950, 745)
instructions_button = "instructions_button.png"
instructions_image = "instructions.png"

mode_man_man_image = "man-vs-man.png"
mode_man_man_coords = (970, 20)
mode_man_pc_image = "man-vs-computer.png"
mode_man_pc_coords = (800, 20)

player_win_image = "player_win.png"

score_sound_file = file_dir + "jupeee.ogg"

font_name = "DejaVu Serif"  #"DejaVuLGCSerif.ttf"  # None  to load pygame default font
font_size = 24
user_font_color = (255, 255, 255)

"""Class Board keeps all the grafical elements as well as a reference to the logical game state."""
class Board:
    
    # Center of initial number positions
    number_locations = [
        ([756+138*0,  231+138*0]), 
        ([756+138*1,  231+138*0]), 
        ([756+138*2,  231+138*0]), 
        ([756+138*0,  231+138*1]), 
        ([756+138*1,  231+138*1]), 
        ([756+138*2,  231+138*1]), 
        ([756+138*0,  231+138*2]), 
        ([756+138*1,  231+138*2]), 
        ([756+138*2,  231+138*2])]
    
    screen = None
    # Center of board cells
    locations = [
        ([267, 228]),
        ([404, 228]),
        ([541, 228]),
        ([267, 367]),
        ([404, 367]),
        ([541, 367]),
        ([267, 510]),
        ([404, 510]),
        ([541, 510])]

    players_name_midleft_location = [
                             (200,  667), 
                             (200,  752)]
    
    players_score_center_location = [
                             (581,  667), 
                             (581,  752)]

    players_score_box_location = [
                             (173,  628), 
                             (173,  714)]

    def __init__(self, screen, game = None):
        self.font = None
        if font_name:
            self.font = pygame.font.SysFont(font_name, font_size)

        if not self.font:
            self.font = pygame.font.Font(None, font_size)
        
        self.mode = "PC"
        self.screen = screen
        self.game = game
        self.showing_instructions = False
        self.score_sound = pygame.mixer.Sound(score_sound_file)
        self.init_board()

    def init_board (self):
        self.new_button = Button(new_image_coords, file_dir + new_image, self.new_game)
        self.instructions_button = Button(instructions_coords, file_dir + instructions_button,  self._show_instructions)
        self.mode_man_man_button = Button(mode_man_man_coords, file_dir + mode_man_man_image, self.change_to_man_man)
        self.mode_man_pc_button = Button(mode_man_pc_coords, file_dir + mode_man_pc_image, self.change_to_man_pc)
        
        if self.mode == "PC":
            self.mode_man_pc_button.set_selected(True)
        else:
            self.mode_man_man_button.set_selected(True)
        
        self.cells = []
        self.numbers = []
        self.lastSelectedBoardCell = None
        self.lastSelectedNumberCell = None
        
        self.backgroundImage = pygame.image.load(image_fondo)
        
        self._init_cells()
        self._init_numbers()
        
        # Creates a sprite group, with all the board visible elements inside
        self._paint_background()
        self.items = pygame.sprite.Group()
        self.items.add(self.new_button)
        self.items.add(self.instructions_button)
        self.items.add(self.mode_man_man_button)
        self.items.add(self.mode_man_pc_button)
        
        for n in self.numbers:
            self.items.add(n)
            
        self.selected_numbers = []
        
        self.arrange_gui()  # Arranges the gui according to the game state.
        
        self.computer_turn = False

    def new_game(self):
        self.game = GameState("", "")
        self.init_board()

    def change_to_man_man(self):
        self.mode = "MAN"
        self.game = GameState("", "")
        self.init_board()
    
    def change_to_man_pc(self):
        self.mode = "PC"
        self.game = GameState("", "")
        self.init_board()
    
    def _init_cells(self):
        i = 1
        for row in range(1, 4):
            for col in range(1, 4):
                if self.game:
                    number = self.game.get_cell(row, col)[0]
                else:
                    number = None
                location = self.locations[i-1]
                self.cells.append( Cell(location, None, None, i, image_size) )
                i += 1
    
    def _init_numbers(self):
        k = 0
        for location in self.number_locations:
            k += 1
            normal_image = self._get_number(k)
            selected_image = self._get_disabled_number(k)
            self.numbers.append( Cell(location, normal_image, selected_image, k, image_size) )

    def set_players(self, name_player1, name_player2):
        self.game = GameState(name_player1, name_player2)
   
    def _paint_background(self):
        rect = self.backgroundImage.get_rect()
        rect.topleft = (0,  0)
        self.screen.blit(self.backgroundImage, rect)

    def _paint_winner(self,  i):
        image = pygame.image.load(file_dir + player_win_image)
        rect = image.get_rect()
        rect.topleft = self.players_score_box_location[i]
        self.screen.blit(image,  rect)
    
    def _paint_players_status(self):
        player1Name = "" 
        player2Name = ""
    
        if (self.game):
            for i in range(1,3):
                if self.game.get_enabled_player():
                    if self.game.get_enabled_player() == i:
                        self.font.set_bold(True)
                    else:
                        self.font.set_bold(False)
                else:
                    if self.game.get_player_score(i) >= self.game.get_player_score(3-i):
                        self._paint_winner(i-1)
                    
                player_name = self.game.get_player_name(i)
                #str_player = 'Jugador %s: %s' % (i, player_name)
                str_player = 'Jugador %s' % (i)
                name_surface = self.font.render(str_player, 1, user_font_color)
                name_rect = name_surface.get_rect()
                name_rect.midleft = self.players_name_midleft_location[i-1]
                self.screen.blit(name_surface, name_rect)
                
                player_score = self.game.get_player_score(i)
                str_player_score = '%s' % (player_score)
                score_surface = self.font.render(str_player_score, 1, user_font_color)
                score_rect = score_surface.get_rect()
                score_rect.center = self.players_score_center_location[i-1]
                self.screen.blit(score_surface, score_rect)

    def paint_board_elements(self):
        # Using an sprite group all the items are painted:
        
        #self.items.clear(self.screen,  self.backgroundImage)   # If only sprites are cleared, players scores remain
        self._paint_background()                                                  # Instead, the whole background is repainted
        self.items.draw(self.screen)
        self._paint_players_status()
        
        if self.showing_instructions:
            self._paint_instructions()

    def _paint_instructions(self):
        image = pygame.image.load(file_dir + instructions_image)
        rect = image.get_rect()
        rect.center = self.screen.get_rect().center
        self.screen.blit(image, rect)

    def arrange_gui(self):
        """Arranges the numbers according to the game state."""
        
        # First moves all the numbers to its original positions
        i = 0
        for number in self.numbers:
            number.rect.center = self.number_locations[i]
            i += 1
        
        # Then for each occupied cell, moves the number to that cell
        coords = [ (row,col) for row in range(1,4) for col in range(1,4) ]
        i = 0
        for row, col in coords:
            cell = self.game.get_cell(row, col)
            if cell:
                number, player = cell
                if number > 0:
                    gui_number = self.numbers[number-1]
                    gui_cell = self.cells[i]
                    gui_number.rect.center = gui_cell.rect.center
            i += 1
            
        for number in self.numbers:
            if number in self.selected_numbers:
                number.set_selected(True)
            else:
                number.set_selected(False)

    def processXY(self, x, y):
        """Processes the x,y coordinates of a click."""
        
        # If is showing instructions, it disables them
        if self.showing_instructions:
            self.showing_instructions = False
            return
        else:
            if self.instructions_button.coords_in(x, y):
                self.instructions_button.callback()
        
        # Checks if the selected coordinate is a board cell
        isCell = False
        for c in self.cells:
            if c.coords_in(x, y):
                isCell = True
                self.lastSelectedBoardCell = c
                
                if self.lastSelectedNumberCell != None:
                    number = self.lastSelectedNumberCell.id_cell
                    row, col = c.get_pos()
                    self.make_move(number, row, col)
                break
    
        # Checks if the selected coordinate is a number
        if isCell == False:
            for n in self.numbers:
                if n.coords_in(x,y):
                    if self.lastSelectedNumberCell:
                        self.lastSelectedNumberCell.set_selected(False)
                    self.lastSelectedNumberCell = n
                    n.set_selected(True)
                    
        if self.new_button.coords_in(x, y):
            self.new_button.callback()
            
        elif self.mode_man_man_button.coords_in(x, y):
            self.mode_man_man_button.callback()
            
        elif self.mode_man_pc_button.coords_in(x, y):
            self.mode_man_pc_button.callback()
        
        return True

    def make_move(self, number, row, col):
        """ Attempts to make the move of the las selected number to the given position. """
        
        # Find the number
        for n in self.numbers:
            if n.id_cell == number:
                self.lastSelectedNumberCell = n
            
        # Find the cell
        for c in self.cells:
            if (row, col) == c.get_pos():
                self.lastSelectedBoardCell = c
        
        player = self.game.get_enabled_player()
        ok, hits = self.game.make_move(row, col, self.lastSelectedNumberCell.id_cell, player)
        if ok:
            if hits:
                self.score_sound.play()
                # Sets a timer to update blinked cells in one second
                pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
                self.selected_numbers = [number for number in self.numbers if number.id_cell in hits]
                
                # Sets the flag to make the computer play after the timer
                player = self.game.get_enabled_player()
                if player == 2 and self.mode=="PC":
                    self.computer_turn = True
            else:
                # The computer makes an automatic move
                player = self.game.get_enabled_player()
                if player == 2 and self.mode=="PC":
                    (number, row, col) = self.game.auto_play(player)
                    self.make_move(number, row, col)
                
            self.arrange_gui()

    def user_event(self, event):
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        if event.type == pygame.USEREVENT + 1:
            # Deselect all numbers
            self.selected_numbers = []
            self.arrange_gui()
            
            if self.computer_turn:
                player = self.game.get_enabled_player()
                if player == 2:
                    (number, row, col) = self.game.auto_play(player)
                    self.make_move(number, row, col)
    
    def _show_instructions(self):
        self.showing_instructions = True
    
    def _get_number(self, number):
        if (number == None) or (number == 0):
            return None
        else:
            path = os.path.join(file_dir, image_number.replace("<N>", str(number)))
            return pygame.image.load(path)

    def _get_disabled_number(self, number):
        if (number == None) or (number == 0):
            return None
        else:
            path = os.path.join(file_dir, image_disabled_number.replace("<N>", str(number)))
            return pygame.image.load(path)
