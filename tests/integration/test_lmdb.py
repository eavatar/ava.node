# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import time
import random
import unittest
import lmdb
import tempfile
import shutil


class TestLMDB(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp()
        self.lmdb = lmdb.Environment(self.path,
                                     map_size=2000000000,
                                     max_dbs=16)

    def tearDown(self):
        self.lmdb.close()
        shutil.rmtree(self.path)

    def test_info(self):
        print(self.lmdb.info())
        print("Max key size: ", self.lmdb.max_key_size())

    def test_crud(self):
        with self.lmdb.begin(write=True) as txn:
            txn.put("k1", "value1")

            v1 = txn.get("k1")
            self.assertEqual(v1, "value1")

            txn.put("k1", "value2")
            v2 = txn.get("k1")
            self.assertEqual(v2, "value2")

            txn.delete("k1")

            v3 = txn.get("k1")
            self.assertTrue(v3 is None)

    def test_subdb(self):
        db = self.lmdb.open_db("test", create=True)

        self.assertIsNotNone(db, "db should not be none.")

        with self.lmdb.begin(db=db, write=False) as txn:
            cur = txn.cursor()
            for k, v in iter(cur):
                print("Found db: ", k)

    def test_duplicate_keys(self):
        db = self.lmdb.open_db("test2", create=True, dupsort=True)
        self.assertIsNotNone(db, "db should not be none.")
        with self.lmdb.begin(db=db, write=True) as txn:
            for i in xrange(100000):
                txn.put(b'1', str(random.randint(1, 100000)) + b'000000', dupdata=True)

        with self.lmdb.begin(db=db, write=False) as txn:
            cur = txn.cursor()
            self.assertTrue(cur.set_key(b'1'))
            prev_value = b'0'
            for item in cur.iternext_dup(keys=True, values=True):
                self.assertTrue(prev_value <= item[1])
                prev_value = item[1]

    @unittest.skip(True)
    def test_write_large_data(self):
        data = os.urandom(8192)
        db = self.lmdb.open_db("test3", create=True, dupsort=False)
        self.assertIsNotNone(db, "db should not be none.")
        t0 = time.time()
        for i in xrange(100):
            with self.lmdb.begin(db=db, write=True) as txn:
                txn.put(str(i), data)
        t1 = time.time()
        print("Data write takes %f seconds." % (t1 - t0))