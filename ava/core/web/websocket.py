# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import logging
from .webfront import dispatcher
from ws4py.websocket import EchoWebSocket
from ws4py.server.wsgiutils import WebSocketWSGIApplication

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class WebSocketHandler(EchoWebSocket):
    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)


class WebsocketEngine(object):
    def __init__(self):
        logger.debug("Websocket engine created.")

    def start(self, ctx=None):
        dispatcher.mount('/ws', WebSocketWSGIApplication(
            handler_cls=WebSocketHandler))

        logger.debug("Websocket engine started.")

    def stop(self, ctx=None):
        logger.debug("Websocket engine stopped.")