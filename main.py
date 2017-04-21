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
#
# Contact information:
# Pablo Moleri pmoleri@gmail.com
# ceibalJAM http://ceibaljam.org

"""Main module of the game.

This is the main module of the game, it can be executed as a standalone game
or imported as a sugar activity.
"""

import pygame
import olpcgames
import olpcgames.pausescreen
import logging

from gui.board import Board
from logic.game import GameState
#import logic.Mesh

import os

log = logging.getLogger('quinteti')
log.setLevel(logging.DEBUG)

MAX_FPS = 20            # Max frames per second
SLEEP_TIMEOUT = 30      # Seconds until the PauseScreen if no events show up

def main():
    """Main function of the game.
    
    This function initializes the game and enters the PyGame main loop.
    """
    
    # Inits PyGame module
    pygame.init()
    
    # Loads Sugar standard cursor
    a, b, c, d = pygame.cursors.load_xbm("gui/standardcursor.xbm", "gui/standardcursor_mask.xbm")
    pygame.mouse.set_cursor(a, b, c, d)

    internal_size = (1200, 825)     # The game is designed to work in this size (xo display size)
    target_size = (900, 619)        # The game will be sown in this size, useful for testing in regular PCs with less resolution than xo
    
    flags = 0
    if olpcgames.ACTIVITY:
        # Running as Activity
        target_size = olpcgames.ACTIVITY.game_size
        #logic.Mesh.init_mesh(log)   # Mesh isn't ready in this version
    else:
        pass
        # Uncomment this if want to execute fullscreen on regular PCs
        # flags = pygame.FULLSCREEN
    
    real_screen = pygame.display.set_mode(target_size, flags)
    
    # The scale factor beetween internal and target
    if internal_size == target_size:
        scale = None
        internal_screen = real_screen   # The game works directly on the real screen
    else:
        # Running on regular PC, the screen its scaled to te target_size
        internal_screen = pygame.Surface(internal_size)
        scale = (internal_size[0] / float(target_size[0]), internal_size[1] / float(target_size[1]) )
    
    # Creates a new logic game, player names aren't used without mesh
    game = GameState("Jugador1", "Jugador2") 
    board = Board(internal_screen, game)
    board.paint_board_elements()
    
    pygame.display.update()
    
    # This clock is used to keep the game at the desired FPS.
    clock = pygame.time.Clock()
    
    # Main loop
    update = True       # The first time the screen need to be updated
    running = True
    while running:
        
        # Waits for events, if none the game pauses:
        # http://wiki.laptop.org/go/Game_development_HOWTO#Reducing_CPU_Load
        milliseconds = clock.tick(MAX_FPS)                              # waits if the game is running faster than MAX_FPS
        events = olpcgames.pausescreen.get_events(SLEEP_TIMEOUT)        # Event-management loop with support for pausing after X seconds (20 here)
        
        if events:
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if scale:
                        x = event.pos[0] * scale[0]     # Multiplies the real coordinates by the scale factor
                        y = event.pos[1] * scale[1]     # to get the internal coordinates
                    else:
                        (x, y) = event.pos
                    
                    update = board.processXY(x, y)
                
                if event.type == pygame.USEREVENT:
                    if event.code == olpcgames.FILE_READ_REQUEST:
                        game = _read_file(event.filename)
                        log.debug("Loaded:" + game.serialization())
                        board = Board(internal_screen, game)
                        update = True
                    elif event.code == olpcgames.FILE_WRITE_REQUEST:
                        _save_file(event.filename, game)
                
                if event.type > pygame.USEREVENT and event.type <= pygame.USEREVENT + 10:
                    log.debug("New user event")
                    board.user_event(event)
                    update = True
                
            if update == True:
                board.paint_board_elements()
                if scale:
                    pygame.transform.scale(internal_screen, target_size, real_screen)
                update = False
            
        pygame.display.flip()
        
    # Una vez que sale del loop manda la senal de quit para que cierre la ventana
    pygame.quit()

def _save_file(file, game):
    """Saves the game to the given file."""
    string = game.serialization()
    fsock = open(file, 'w')
    fsock.write(string)
    fsock.close()

def _read_file(file):
    """Loads the game from the given file."""
    fsock = open(file, "r")
    string = fsock.read()
    fsock.close()
    return GameState.fromString(string)

if __name__ == "__main__":
    """Standalone code."""
    
    logging.basicConfig()
    main()
