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

from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection

import olpcgames
import logging
import telepathy

SERVICE = "uy.edu.ceibaljam.Quinteti"
IFACE = SERVICE
PATH = "/uy/edu/ceibaljam/Quinteti"

log = None

hellotube = None  # Shared session

initiating = False

conn = None
tubes_chan = None
text_chan = None

def init_mesh(main_log):
    global log
    log = main_log
    
    # get the Presence Service
    pservice = presenceservice.get_instance()
    # Buddy object for you
    owner = pservice.get_owner()
    
    olpcgames.ACTIVITY.connect("shared", _shared_cb)
    olpcgames.ACTIVITY.connect("joined", _joined_cb)
    
    
def _shared_cb(activity):
    log.debug('My activity was shared')
    #self._alert('Shared', 'The activity is shared')
    
    global initiating
    initiating = True
    _sharing_setup()

    log.debug('This is my activity: making a tube...')
    id = tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
        SERVICE, {})

def _sharing_setup():
    if olpcgames.ACTIVITY._shared_activity is None:
        log.error('Failed to share or join activity')
        return

    s_activity = olpcgames.ACTIVITY._shared_activity
    global conn, tubes_chan, text_chan    # Necesario para que escriba sobre las variables globales, en vez de crear locales
    
    conn = s_activity.telepathy_conn
    tubes_chan = s_activity.telepathy_tubes_chan
    text_chan = s_activity.telepathy_text_chan

    tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal('NewTube', _new_tube_cb)

    s_activity.connect('buddy-joined', _buddy_joined_cb)
    s_activity.connect('buddy-left', _buddy_left_cb)

    # Optional - included for example:
    # Find out who's already in the shared activity:
    for buddy in s_activity.get_joined_buddies():
        log.debug('Buddy %s is already in the activity', buddy.props.nick)

def _joined_cb(activity):
    if not olpcgames.ACTIVITY._shared_activity:
        return
    
    s_activity = olpcgames.ACTIVITY._shared_activity
    log.debug('Joined an existing shared activity')
    
    global initiating
    initiating = False
    _sharing_setup()

    log.debug('This is not my activity: waiting for a tube...')
    tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
        reply_handler=list_tubes_reply_cb,
        error_handler=list_tubes_error_cb)
    
def _new_tube_cb(id, initiator, type, service, params, state):
    log.debug('New tube: ID=%d initator=%d type=%d service=%s '
                 'params=%r state=%d', id, initiator, type, service,
                 params, state)
    if (type == telepathy.TUBE_TYPE_DBUS and service == SERVICE):
        if state == telepathy.TUBE_STATE_LOCAL_PENDING:
            tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)
        tube_conn = TubeConnection(conn,
            tubes_chan[telepathy.CHANNEL_TYPE_TUBES],
            id, group_iface=text_chan[telepathy.CHANNEL_INTERFACE_GROUP])
#        hellotube = TextSync(tube_conn, initiating,
#                                  self.entry_text_update_cb,
#                                  self._alert,
#                                  self._get_buddy)

def _buddy_joined_cb(activity, buddy):
    """Called when a buddy joins the shared activity.

    This doesn't do much here as HelloMesh doesn't have much 
    functionality. It's up to you do do interesting things
    with the Buddy...
    """
    log.debug('Buddy %s joined', buddy.props.nick)
    
def _buddy_left_cb (activity, buddy):
    """Called when a buddy leaves the shared activity.

    This doesn't do much here as HelloMesh doesn't have much 
    functionality. It's up to you do do interesting things
    with the Buddy...
    """
    log.debug('Buddy %s left', buddy.props.nick)
    
def _list_tubes_reply_cb(tubes):
    log.debug('list_tubes_reply_cb')
    for tube_info in tubes:
        _new_tube_cb(*tube_info)

def _list_tubes_error_cb(e):
    log.error('ListTubes() failed: %s', e)
