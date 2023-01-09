import csv
from abc import ABC, abstractmethod


class CollectionProxy(ABC):
    """
    データ結合などの際にデータセットを隠蔽するクラス
    - IDMapなどを提供する
    """

    def __init__(self, value):
        self._value = value
        self._idmap = None
        self._headers = None

    @property
    def value(self):
        return self._value

    @property
    @abstractmethod
    def filepath(self):
        pass

    def data_read(self, with_headers=False):
        with open(self.filepath, "r") as file:
            reader = csv.reader(file)
            if with_headers is False:
                reader.__next__()

            for record in reader:
                yield record

    def headers(self):
        return self._headers

    def idmap(self, key_idx):
        if self._idmap is None:
            (self._idmap, self._headers) = self.__get_idmap(key_idx)
        return self._idmap

    def __get_idmap(self, key_idx):
        idmap = {}
        headers = None

        index = 0
        for record in self.data_read(with_headers=True):
            if index == 0:
                headers = record
            else:
                key = record[key_idx]
                idmap[key] = record
            index = index + 1

        return idmap, headers

    def encode(self):
        return [self.value]

    @classmethod
    def key(cls):
        return cls.__name__

    @classmethod
    def decode(cls, args):
        return cls(args[0])


class NoopCollectionProxy(CollectionProxy):
    @property
    def filepath(self):
        return self.value


PROXYES = [NoopCollectionProxy]

PROXYES_DICT = {}
for p in PROXYES:
    PROXYES_DICT[p.key()] = p


def registry_proxy(proxy):
    PROXYES.append(proxy)
    PROXYES_DICT[proxy.key()] = proxy


def proxy_find_by(name):
    return PROXYES_DICT.get(name)


def encode_proxy(proxy):
    return [proxy.key()]


def decode_proxy(proxy):
    return proxy_find_by(proxy[0])
