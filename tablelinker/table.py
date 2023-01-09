from logging import getLogger
import os
import shutil
import tempfile

from .convertors import core
from .convertors import basics

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

    def save(self, csv_path: os.PathLike):
        """
        入力 CSV ファイルを指定したファイル名で保存する。

        Paramters
        ---------
        csv_path: os.PathLike
            保存する CSV ファイルのパス
        """
        if self.csv_in is not None and \
                os.path.exists(self.csv_in):
            shutil.copyfile(self.csv_in, csv_path)
            logger.debug("一時ファイル '{}' を '{}' に保存しました".format(
                self.csv_in, csv_path))

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
            with open(self.csv_in, 'r') as f:
                while True:
                    buf = f.read(1024)
                    if buf is None or len(buf) == 0:
                        break

                    file.write(buf)

    def convert(
            self,
            filter_name: str,
            filter_params: dict) -> 'Table':
        """
        表形式データにフィルタを適用して変換する。

        Parameters
        ----------
        filter_name: str
            フィルタ名
            定義済みフィルタの Meta.key (例: 'rename_col')
        filter_params: dict
            フィルタに渡すパラメータ名・値の辞書
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
        filter = core.filter_find_by(filter_name)

        with core.core.Context(
                filter=filter,
                filter_params=filter_params,
                input=input,
                output=output) as context:
            try:
                filter().process(context)
                logger.debug((
                    "ファイル '{}' にフィルタ '{}' を適用し"
                    "一時ファイル '{}' に出力しました。").format(
                    self.csv_in, filter_name, csv_out))
                new_table = Table(csv_out, True)
                return new_table
            except RuntimeError as e:
                os.remove(csv_out)
                logger.debug((
                    "ファイル '{}' にフィルタ '{}' を適用中、"
                    "エラーのため一時ファイル '{}' を削除しました。").format(
                    self.csv_in, filter_name, csv_out))

                raise e
