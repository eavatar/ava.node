# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import unittest
import gevent
import shutil
import tempfile

from ava.spi.defines import AVA_USER_XID, AVA_AGENT_SECRET
from ava.util import base_path


def prepare_agent_test_env():
    """
    Constructs the skeleton of directories if it not there already.
    :return:
    """
    pod_folder = tempfile.mkdtemp()
    os.environ.setdefault('AVA_POD', pod_folder)

    base_dir = base_path()

    src_dir = os.path.join(base_dir, 'pod')

    # copy files from base_dir to user_dir
    subdirs = os.listdir(src_dir)
    for d in subdirs:
        src_path = os.path.join(src_dir, d)
        dst_path = os.path.join(pod_folder, d)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

prepare_agent_test_env()


class AgentTest(unittest.TestCase):
    """
    For functional tests which require a running agent.
    """
    agent = None
    user_xid = b'AYPwK3c3VK7ZdBvKfcbV5EmmCZ8zSb9viZ288gKFBFuE92jE'
    user_key = b'Kd2xqKsjTnhhqXjY64eeSEyS1i9kSGTHt9S57sqeK51bkPRh'
    user_secret = b'SVQh1mgbdvuFoZihYH8urZyBGpfZ4PJnn8af2R9MuqZyktHa'

    agent_secret = b'SYNmgyQqhAnVwKLrmSmYzahkzH3V51qdShL41JFPnmsZob96'
    pod_folder = None

    @classmethod
    def setUpClass(cls):
        from ava.runtime import settings
        from ava.core.agent import Agent

        settings['debug'] = True
        os.environ.setdefault(AVA_USER_XID, cls.user_xid)
        os.environ.setdefault(AVA_AGENT_SECRET, cls.agent_secret)
        AgentTest.agent = Agent()
        agent_greenlet = gevent.spawn(AgentTest.agent.run)
        while not AgentTest.agent.running:
            gevent.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        AgentTest.agent.interrupted = True
        while AgentTest.agent.running:
            gevent.sleep(0.5)

        # shutil.rmtree(cls.pod_folder)

