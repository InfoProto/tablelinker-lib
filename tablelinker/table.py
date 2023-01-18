import csv
from logging import getLogger
import os
import sys
import tempfile

import pandas as pd
from pandas.core.frame import DataFrame

from .convertors import core
from .convertors import basics as basic_convertors


logger = getLogger(__name__)
basic_convertors.register()


class Table(object):
    """
    表形式データを表すクラス。

    Attributes
    ----------
    csv_in: PathLike
        このテーブルの入力 CSV ファイルのパス
    is_tempfile: bool
        入力 CSV ファイルが一時ファイルかどうかを表すフラグ
    """

    def __init__(
            self,
            csv_path: os.PathLike,
            is_tempfile: bool = False,
            need_cleaning: bool = True):
        """
        初期化。

        Parameters
        ----------
        csv_path: os.PathLike
            入力 CSV ファイルのパス。
        is_tempfile: bool [False]
            参照している CSV ファイルが一時ファイルかどうか。
            True の場合、オブジェクト消滅時に CSV ファイルも
            削除します。
        need_cleaning: bool [True]
            参照している CSV ファイルに対してクリーニングを
            行うかどうか。
            True の場合、一度全体を読み込んでクリーニングを
            行うため、余分なメモリと処理時間が必要になります。

        Notes
        -----
        is_tempfile が True の場合、オブジェクト削除時に
        csv_path にあるファイルも削除する。
        """
        self.csv_in = csv_path
        self.is_tempfile = is_tempfile
        self.need_cleaning = need_cleaning
        self._reader = None

    def __del__(self):
        """
        変換済みの CSV ファイルが利用されずに残っている場合、
        このオブジェクトの削除と同時にファイルも消去する。
        """
        if self.is_tempfile is True and \
                os.path.exists(self.csv_in):
            os.remove(self.csv_in)
            logger.debug("一時ファイル '{}' を削除しました".format(
                self.csv_in))

    def open(self):
        """
        入力 CSV を開き、 csv.reader オブジェクトを返す。
        """
        self._reader = core.CsvInputCollection(
            self.csv_in,
            need_cleaning=self.need_cleaning).open()
        return self._reader

    @classmethod
    def useExtraConvertors(cls) -> None:
        from .convertors import extras as extra_convertors
        extra_convertors.register()
        logger.debug("拡張コンバータを登録しました。")

    @classmethod
    def fromPandas(cls, df: DataFrame) -> "Table":
        """
        Pandas DataFrame から Table オブジェクトを作成する

        Parameters
        ----------
        df: pandas.core.frame.DataFrame
            Pandas DataFrame オブジェクト

        Returns
        -------
        Table
            新しい Table オブジェクト
        """
        table = None
        with tempfile.NamedTemporaryFile(
                mode="w+b", delete=False) as f:
            df.to_csv(f, index=False)
            table = Table(
                f.name,
                is_tempfile=True,
                need_cleaning=False)

        return table

    def toPandas(self) -> DataFrame:
        """
        Table オブジェクトから Pandas DataFrame を作成する

        Returns
        -------
        pandas.core.frame.DataFrame
        """
        with tempfile.TemporaryDirectory() as td:
            fname = os.path.join(td, 'topandas.csv')
            with open(
                    fname,
                    mode="w",
                    newline="") as f:
                writer = csv.writer(f)
                input = self.open()
                for row in input:
                    writer.writerow(row)

            df = pd.read_csv(fname)

        return df

    def save(self, csv_path: os.PathLike, encoding="utf-8"):
        """
        入力 CSV ファイルを指定したファイル名で保存する。

        Paramters
        ---------
        csv_path: os.PathLike
            保存する CSV ファイルのパス
        encoding: str
            テキストエンコーディング
        """
        if self.csv_in is not None:
            with open(csv_path, mode="w", newline="", encoding=encoding) as f:
                writer = csv.writer(f)
                input = self.open()
                for row in input:
                    writer.writerow(row)

    def write(self, lines: int = -1, file=None):
        """
        入力 CSV ファイルを指定したファイルオブジェクトに出力する。

        Parameters
        ----------
        lines: int [-1]
            出力する最大行数。負の場合は全ての行を出力する。
        file: File object [sys.stdout]
            出力先のファイルオブジェクト。
        """
        if file is None:
            file = sys.stdout

        if self.csv_in is not None:
            writer = csv.writer(file)
            input = self.open()
            for n, row in enumerate(input):
                if n == lines:
                    break

                writer.writerow(row)

    def convert(
            self,
            convertor: str,
            params: dict) -> 'Table':
        """
        表形式データにフィルタを適用して変換する。

        Parameters
        ----------
        convertor: str
            コンバータ名
            定義済みコンバータの Meta.key (例: 'rename_col')
        params: dict
            コンバータに渡すパラメータ名・値の辞書
            例: {"input_attr_idx": 1, "new_col_name": "番号"}

        Returns
        -------
        Table
            csv_in パラメータに変換済み CSV ファイルのパスを持つ
            Table オブジェクト
        """
        csv_out = tempfile.NamedTemporaryFile(delete=False).name
        input = core.CsvInputCollection(
            self.csv_in, need_cleaning=self.need_cleaning)
        output = core.CsvOutputCollection(csv_out)
        filter = core.filter_find_by(convertor)

        if filter is None:
            raise ValueError("コンバータ '{}' は未登録です".format(
                convertor))

        with core.Context(
                filter=filter,
                filter_params=params,
                input=input,
                output=output) as context:
            try:
                filter().process(context)
                logger.debug((
                    "ファイル '{}' にコンバータ '{}' を適用し"
                    "一時ファイル '{}' に出力しました。").format(
                    self.csv_in, convertor, csv_out))
                new_table = Table(
                    csv_out,
                    is_tempfile=True,
                    need_cleaning=False)
                return new_table

            except RuntimeError as e:
                os.remove(csv_out)
                logger.debug((
                    "ファイル '{}' にコンバータ '{}' を適用中、"
                    "エラーのため一時ファイル '{}' を削除しました。").format(
                    self.csv_in, convertor, csv_out))

                raise e
