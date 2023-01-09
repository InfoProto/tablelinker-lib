import csv
import io
from logging import getLogger

logger = getLogger(__name__)


class InputCollection(object):
    """
    データセット(Array, File)
    """

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def open(self):
        pass

    def close(self):
        pass

    def reset(self):
        pass

    def next(self):
        return None

    def encode(self):
        return []

    @classmethod
    def decode(cls, args):
        pass

    @classmethod
    def key(cls):
        return cls.__name__


class ArrayInputCollection(InputCollection):
    def __init__(self, array):
        self._array = array
        self.reset()

    def reset(self):
        self._current = 0

    def next(self):
        if self._current == len(self._array):
            raise StopIteration()
        value = self._array[self._current]
        self._current += 1
        return value

    def encode(self):
        return [self._array]

    @classmethod
    def decode(cls, args):
        return cls(args[0])


class CsvInputCollection(InputCollection):
    def __init__(self, filepath):
        self.filepath = filepath
        self._file = None

    def file(self):
        return self._file

    def open(self):
        """
        ファイルを開き、そのハンドルを返す。
        もし既にファイルが開いている場合は開きなおす。
        """
        if self._file is not None:
            self._file.close()

        self._file = open(self.filepath, "rb")
        self._reader = csv.reader(
            io.TextIOWrapper(
                buffer=self._file,
                encoding='utf-8',
                newline=''))

        return self._file

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None

    def reset(self):
        self.close()
        return self.open()

    def next(self):
        return self._reader.__next__()

    def encode(self):
        return [self.filepath]

    @classmethod
    def decode(cls, args):
        return cls(args[0])


INPUTS = [ArrayInputCollection, CsvInputCollection]

INPUTS_DICT = {}
for i in INPUTS:
    INPUTS_DICT[i.key()] = i


def registry_input(input_class):
    INPUTS.append(input_class)
    INPUTS_DICT[input_class.key()] = input_class


def input_find_by(name):
    return INPUTS_DICT.get(name)


def encode_input(input):
    return [input.key(), input.encode()]


def decode_input(input):
    return input_find_by(input[0]).decode(input[1])
