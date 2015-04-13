# -*- coding: utf-8 -*-
"""
Data stores
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from abc import abstractmethod
from .context import instance

_dataengine = instance().get('dataengine')


class IStore(object):
    """ Interface for a data store.
    """
    @abstractmethod
    def put(self, key, value):
        raise NotImplementedError()

    @abstractmethod
    def get(self, key):
        raise NotImplementedError()

    @abstractmethod
    def remove(self, key):
        raise NotImplementedError()

    @abstractmethod
    def cursor(self, readonly=True):
        raise NotImplementedError()


class ICursor(object):
    """ Interface for a cursor which is used to traverse the store.
    """
    @abstractmethod
    def first(self):
        raise NotImplementedError()

    @abstractmethod
    def next(self):
        raise NotImplementedError()

    @abstractmethod
    def prev(self):
        raise NotImplementedError()

    @abstractmethod
    def last(self):
        raise NotImplementedError()

    @abstractmethod
    def iternext(self, keys=True, values=False):
        raise NotImplementedError()

    @abstractmethod
    def iterprev(self, keys=True, values=False):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()

    @abstractmethod
    def value(self):
        """
        Gets raw value of the record.
        :return: record's value.
        """
        raise NotImplementedError()

    @abstractmethod
    def key(self):
        raise NotImplementedError()

    @abstractmethod
    def get(self, key):
        raise NotImplementedError()

    @abstractmethod
    def load(self, key):
        """
        Same as get method, except raising exception if entry not found.
        :param key: item key.
        :return: the value.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete(self):
        """
        Actually deletes document and its revisions if required.
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def remove(self, key):
        """
        Delete the current element and move to the next, returning True on
        success or False if the store was empty
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def seek(self, key):
        """
        Finds the document with the provided ID and moves position to its first revision.

        :param key:
        :return: True if found; False, otherwise.
        """
        raise NotImplementedError()

    @abstractmethod
    def seek_range(self, key):
        """
        Finds the document whose ID is greater than or equal to the provided
        ID and moves position to its first revision.

        :param key:
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def count(self):
        """
        Return the number of values (“duplicates”) for the current key.
        Only meaningful for databases opened with dupsort=True.
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def post(self, value):
        raise NotImplementedError()

    @abstractmethod
    def pop(self):
        """
        Fetch the first document then delete it. Returns None if no value
        existed.
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def put(self, key, value):
        raise NotImplementedError()

    @abstractmethod
    def exists(self, key):
        raise NotImplementedError()


def names():
    """ Gets the store names.

    :return: the store names.
    """
    return _dataengine.store_names()


def create(store_name):
    """ Creates a new data store.

    :param store_name:
    :return:
    """
    return _dataengine.create_store(store_name)


def remove(store_name):
    """ Deletes the named data store.

    :param store_name:
    :return:
    """
    return _dataengine.remove_store(store_name)


def get(store_name):
    """ Gets or creates the named data store.

    :param store_name:
    :return:
    """
    return _dataengine.get_store(store_name)