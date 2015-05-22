# -*- coding: utf-8 -*-
"""
Data engine implementation based on lighting memory database
(http://symas.com/mdb/).
The Lmdb is initialized, the access needs to use its binding API, though.
Extension packages may provide higher-level APIs based on this.
"""
from __future__ import (absolute_import, division, unicode_literals)

import os
import logging
import lmdb

from ava.util import time_uuid
from ava.runtime import environ
from ava.spi.errors import DataNotFoundError, DataError
from ava.spi.stores import IStore, ICursor

_DATA_FILE_DIR = b'data'

logger = logging.getLogger(__name__)


class Store(IStore):
    def __init__(self, name, _db, _engine):
        self.name = name
        self._db = _db
        self._engine = _engine

    def __len__(self):
        with self._engine.database.begin() as txn:
            stat = txn.stat(self._db)
            return stat['entries']

    def __getitem__(self, key):
        with self._engine.cursor(self.name) as cur:
            return cur.get(key)

    def __setitem__(self, key, value):
        with self._engine.cursor(self.name, readonly=False) as cur:
            cur.put(key, value)

    def __delitem__(self, key):
        with self._engine.cursor(self.name, readonly=False) as cur:
            cur.remove(key)

    def __iter__(self):
        return self._engine.cursor(self.name).iternext()

    def put(self, key, value):
        with self._engine.cursor(self.name, readonly=False) as cur:
            return cur.put(key, value)

    def get(self, key):
        with self._engine.cursor(self.name, readonly=True) as cur:
            return cur.get(key)

    def remove(self, key):
        with self._engine.cursor(self.name, readonly=False) as cur:
            return cur.remove(key)

    def cursor(self, readonly=True):
        return self._engine.cursor(self.name, readonly=readonly)


class Cursor(ICursor):
    def __init__(self, _txn, _db, _readonly=True):

        self._txn = _txn
        self._db = _db
        self._readonly = _readonly
        self._cursor = lmdb.Cursor(_db, _txn)

    def __enter__(self, *args, **kwargs):
        self._txn.__enter__(*args, **kwargs)
        self._cursor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cursor.__exit__(exc_type, exc_val, exc_tb)
        self._txn.__exit__(exc_type, exc_val, exc_tb)

    def first(self):
        return self._cursor.first()

    def next(self):
        return self._cursor.next()

    def prev(self):
        return self._cursor.prev()

    def last(self):
        return self._cursor.last()

    def iternext(self, keys=True, values=False):
        return self._cursor.iternext(keys=True, values=False)

    def iterprev(self, keys=True, values=False):
        return self._cursor.iterprev(keys=True, values=False)

    def close(self):
        self._cursor.close()

    def value(self):
        """
        Gets raw value of the record.
        :return: record's value.
        """
        return self._cursor.value()

    def key(self):
        return self._cursor.key()

    def get(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        if not self._cursor.set_key(key):
            return None

        return self._cursor.value()

    def load(self, key):
        """
        Same as get method, except raising exception if entry not found.
        :param _key: item key.
        :return: the value.
        """
        ret = self.get(key)
        if ret is None:
            raise DataNotFoundError()
        return ret

    def delete(self):
        """
        Actually deletes document and its revisions if required.
        :return:
        """
        return self._cursor.delete(True)

    def remove(self, key):
        """
        Delete the current element and move to the next, returning True on
        success or False if the store was empty
        :return:
        """
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        if not self._cursor.set_key(key):
            return False

        return self._cursor.delete(True)

    def seek(self, key):
        """
        Finds the document with the provided ID and moves position to its first revision.

        :param key:
        :return: True if found; False, otherwise.
        """
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        return self._cursor.set_key(key)

    def seek_range(self, key):
        """
        Finds the document whose ID is greater than or equal to the provided
        ID and moves position to its first revision.

        :param key:
        :return:
        """
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        return self._cursor.set_range(key)

    def count(self):
        """
        Return the number of values (“duplicates”) for the current key.
        Only meaningful for databases opened with dupsort=True.
        :return:
        """
        return self._cursor.count()

    def post(self, value):
        key = time_uuid.utcnow().hex
        if self._cursor.put(key, value):
            return key
        return None

    def pop(self):
        """
        Fetch the first document then delete it. Returns None if no value
        existed.
        :return:
        """
        if self._cursor.first():
            return self._cursor.pop(self._cursor.key())

    def put(self, key, value):
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        return self._cursor.put(key, value)

    def exists(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')

        if self._cursor.set_key(key):
            return True
        return False


class DataEngine(object):
    def __init__(self):
        logger.debug("Initializing data engine...")
        self.datapath = None
        self.database = None
        self.stores = {}

    def start(self, ctx=None):
        logger.debug("Starting data engine...")

        # register with the context
        ctx.bind('dataengine', self)

        self.datapath = os.path.join(environ.pod_dir(), _DATA_FILE_DIR)
        logger.debug("Data path: %s", self.datapath)

        try:
            self.database = lmdb.Environment(self.datapath,
                                             map_size=2000000000,
                                             max_dbs=1024)
            with self.database.begin(write=False) as txn:
                cur = txn.cursor()
                for k, v in iter(cur):
                    logger.debug("Found existing store: %s", k)
                    _db = self.database.open_db(k, create=False)
                    self.stores[k] = Store(k, _db, self)
        except lmdb.Error:
            logger.exception("Failed to open database.", exc_info=True)
            raise

        logger.debug("Data engine started.")

    def stop(self, ctx=None):
        logger.debug("Stopping data engine...")
        if self.database:
            self.database.close()

        logger.debug("Data engine stopped.")

    def store_names(self):
        return self.stores.keys()

    def create_store(self, name):
        if isinstance(name, unicode):
            name = name.encode('utf-8')

        try:
            _db = self.database.open_db(name, dupsort=False, create=True)
            store = Store(name, _db, self)
            self.stores[name] = store
            return store
        except lmdb.Error as ex:
            logger.exception(ex)
            raise DataError(ex.message)

    def get_store(self, name, create=True):
        result = self.stores.get(name)
        if result is None and create:
            return self.create_store(name)
        return result

    def remove_store(self, name):
        try:
            store = self.stores.get(name)
            if store is not None:
                with self.database.begin(write=True) as txn:
                    txn.drop(store._db)
                del self.stores[name]
        except lmdb.Error as ex:
            logger.exception("Failed to remove store.", ex)
            raise DataError(ex.message)

    def remove_all_stores(self):
        for name in self.stores.keys():
            self.remove_store(name)

    def store_exists(self, name):
        return name in self.stores

    def cursor(self, store_name, readonly=True):
        if isinstance(store_name, unicode):
            store_name = store_name.encode('utf-8')

        _write = True
        if readonly:
            _write = False

        _db = self.database.open_db(store_name, create=False, dupsort=True)
        _txn = self.database.begin(write=_write, buffers=False)
        return Cursor(_txn, _db, _readonly=readonly)

    def stat(self):
        ret = self.database.stat()
        return ret

    def __iter__(self):
        return self.stores.iterkeys()

    def __getitem__(self, store_name):
        return self.get_store(store_name)

    def __delitem__(self, store_name):
        return self.remove_store(store_name)
