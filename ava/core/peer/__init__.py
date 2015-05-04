# -*- coding: utf-8 -*-
""" Peer engine provides a distributed hash table and other peer-to-peer
primitives. Each peer uses a UDP port for communication with other peers.
"""
from __future__ import (absolute_import, division, unicode_literals)

import logging

logger = logging.getLogger(__name__)


class PeerEngine(object):
    def __init__(self):
        logger.debug("Peer engine created.")
        self.context = None

    def start(self, ctx):
        logger.debug("Peer engine started.")
        self.context = ctx

    def stop(self, ctx):
        logger.debug("Peer engine stopped.")
