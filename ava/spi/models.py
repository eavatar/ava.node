# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from collections import MutableMapping


class Model(MutableMapping):
    """ Base class for model objects. A model object has dict-like methods.
    """
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __getattr__(self, attr):
        return self.store[attr]

    def __setattr__(self, attr, value):
        self.store[attr] = value


class Avatar(Model):
    """ Represents an autonomous entity in the network.
    """
    def __init__(self, *args, **kwargs):
        super(Avatar, self).__init__(*args, **kwargs)

