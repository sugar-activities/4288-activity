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

import pygame

"""Button is a PyGame Sprite with a callback function."""

class Button(pygame.sprite.Sprite):
    def __init__(self, initial_position, image_name, callback):

        pygame.sprite.Sprite.__init__(self)
        
        self.selected = False
        
        self.image_name = image_name
        self.set_image(image_name)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position     # Moves the recteangle to its predetermined center
        
        self.callback = callback

    
    def coords_in(self, x, y):
        if self.rect.collidepoint(x, y):
            return True
        return False
    
    def set_image(self, nomImage):
        if nomImage:
            self.image = pygame.image.load(nomImage)
        else:
            self.image = None

    def set_selected(self, selected):
        self.selected = selected
        
        self.set_image(self.image_name)
        
        if selected:    
            rect = self.image.get_rect()
            
            dash = pygame.Rect(rect.left, rect.bottom-3, rect.width, 3)
            black = pygame.Color("0x000000F8")
            self.image.fill(black, dash)
