import csv
from logging import getLogger
import os
import tempfile

import pandas as pd
from pandas.core.frame import DataFrame

from .convertors import core

logger = getLogger(__name__)


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
            is_tempfile: bool = False):
        """
        初期化。

        Parameters
        ----------
        csv_path: os.PathLike
            入力 CSV ファイルのパス
        is_tempfile: bool
            この CSV ファイルが一時ファイルかどうか

        Notes
        -----
        is_tempfile が True の場合、オブジェクト削除時に
        csv_path にあるファイルも削除する。
        """
        self.csv_in = csv_path
        self.is_tempfile = is_tempfile

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
            table = Table(f.name, is_tempfile=True)

        return table

    def toPandas(self) -> DataFrame:
        """
        Table オブジェクトから Pandas DataFrame を作成する

        Returns
        -------
        pandas.core.frame.DataFrame
        """
        with tempfile.NamedTemporaryFile(
                mode="w", newline="", delete=True) as f:
            writer = csv.writer(f)
            with core.CsvInputCollection(self.csv_in) as input:
                for row in input:
                    writer.writerow(row)

            df = pd.read_csv(f.name)

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
        if self.csv_in is not None and \
                os.path.exists(self.csv_in):
            with open(csv_path, mode="w", newline="", encoding=encoding) as f:
                writer = csv.writer(f)
                with core.CsvInputCollection(self.csv_in) as input:
                    for row in input:
                        writer.writerow(row)

    def write(self, file):
        """
        入力 CSV ファイルを指定したファイルオブジェクトに出力する。

        Parameters
        ----------
        file: File object
            出力先のファイルオブジェクト
        """
        if self.csv_in is not None and \
                os.path.exists(self.csv_in):
            writer = csv.writer(file)
            with core.CsvInputCollection(self.csv_in) as input:
                for row in input:
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
        input = core.CsvInputCollection(self.csv_in)
        output = core.CsvOutputCollection(csv_out)
        filter = core.filter_find_by(convertor)

        if filter is None:
            raise ValueError("コンバータ '{}' は未登録です".format(
                convertor))

        with core.core.Context(
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
                new_table = Table(csv_out, True)
                return new_table
            except RuntimeError as e:
                os.remove(csv_out)
                logger.debug((
                    "ファイル '{}' にコンバータ '{}' を適用中、"
                    "エラーのため一時ファイル '{}' を削除しました。").format(
                    self.csv_in, convertor, csv_out))

                raise e
