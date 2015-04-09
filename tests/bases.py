# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import unittest

import gevent
from ava.core.agent import Agent


class AgentTest(unittest.TestCase):
    """
    For integration tests with the agent.
    """
    _agent = None

    @classmethod
    def setUpClass(cls):
        AgentTest._agent = Agent()
        server_greenlet = gevent.spawn(AgentTest._agent.run)

        while not AgentTest._agent.running:
            gevent.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        AgentTest._agent.interrupted = True
        while AgentTest._agent.running:
            gevent.sleep(0.5)


