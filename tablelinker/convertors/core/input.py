import csv
from logging import getLogger

from .csv_cleaner import CSVCleaner

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

    def __init__(self, file_or_path, skip_cleaning=False):
        # file_or_path パラメータが File-like か PathLike か判別
        if all(hasattr(file_or_path, attr)
               for attr in ('seek', 'close', 'read')):
            # File-like オブジェクトの場合
            self.fp = file_or_path
            self.path = None
            logger.debug("Detect file-like object.")
        else:
            self.fp = None
            self.path = file_or_path
            logger.debug("Detect path-like object.")

        self.skip_cleaning = skip_cleaning
        self._reader = None

    def open(self, as_dict: bool = False, **kwargs):
        """
        ファイルを開く。
        skip_cleaning が False の場合、コンテンツを読み込み
        CSVCleaner で整形したバッファを開く。
        """
        reader = csv.reader
        if as_dict is True:
            reader = csv.DictReader

        if self.skip_cleaning:
            # ファイルをそのまま開く
            if self.path is not None:
                if self.fp is not None:
                    self.fp.close()

                self.fp = open(self.path, "r", newline="")
                self._reader = reader(self.fp, **kwargs)
            else:
                self.fp.seek(0)
                top = self.fp.read(1)
                self.fp.seek(0)
                if isinstance(top, bytes):
                    # バイトストリーム
                    stream = io.TextIOWrapper(
                        self.fp, encoding="utf-8")
                    self._reader = reader(stream, **kwargs)
                else:
                    # テキストストリーム
                    self._reader = reader(self.fp, **kwargs)
        else:
            # ファイルの内容を読み込んでクリーニングする
            if self.path is not None:
                with open(self.path, "rb") as fb:
                    content = fb.read()
            else:
                self.fp.seek(0)
                content = self.fp.read()

            # クリーニング
            self._reader = CSVCleaner(data=content)
            self._reader.open(as_dict=as_dict, **kwargs)

        return self

    def reset(self):
        self.open()

    def next(self):
        return self._reader.__next__()

    def encode(self):
        return [self.filepath]

    @classmethod
    def decode(cls, args):
        return cls(args[0])

    def __exit(self, type_, value, traceback):
        if self.path is not None and self.fp is not None:
            self.fp.close()

        if self._reader is not None:
            self._reader.__exit__()


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
