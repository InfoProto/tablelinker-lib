import codecs
import csv
import io
from logging import getLogger
import os
import sys
import tempfile
from typing import Optional

import pandas as pd
from pandas.core.frame import DataFrame

from .convertors import core
from .convertors import basics as basic_convertors
from .task import Task


logger = getLogger(__name__)
basic_convertors.register()


def escape_encoding(exc):
    """
    文字エンコーディングの処理中に UnicodeDecodeError が
    発生した場合のエラーハンドラ。
    https://docs.python.org/ja/3.5/library/codecs.html#codecs.register_error

    変換できなかった文字を '??' に置き換えます。
    """
    logger.warning(str(exc))
    return ('??', exc.end)


class Table(object):
    """
    表形式 CSV データを管理するクラス。

    Attributes
    ----------
    file: File-like, Path-like
        このテーブルが管理する入力表データファイルのパス、
        または file-like オブジェクト。
    sheet: str, None
        入力ファイルが Excel の場合など、複数の表データを含む場合に
        対象を指定するためのシート名。省略された場合は最初の表。
    is_tempfile: bool
        入力表データファイルが一時ファイルかどうかを表すフラグ。
        True の場合、オブジェクトが消滅するときに file が
        指すパスにあるファイルも削除します。
    skip_cleaning: bool
        表データを読み込む際にクリーニングをスキップするか
        どうかを指定するフラグ。
        True を指定した場合、 UTF-8 でカンマ区切りの CSV ファイルで
        先頭部分に余計な行が含まれていない必要があります。
    filetype: str
        入力表データファイルの種別。 CSV の場合は ``csv``、
        Excel の場合は ``excel`` になります。

    Examples
    --------
    >>> from tablelinker import Table
    >>> table = Table("sample/hachijo_sightseeing.csv")
    >>> table.write(lines=2)
    観光スポット名称,所在地,緯度,経度,座標系,説明,八丈町ホームページ記載
    ホタル水路,,33.108218,139.80102,JGD2011,八丈島は伊豆諸島で唯一、水田耕作がなされた島で鴨川に沿って水田が残っています。ホタル水路は、鴨川の砂防とともに平成元年につくられたもので、毎年6月から7月にかけてホタルの光が美しく幻想的です。,http://www.town.hachijo.tokyo.jp/kankou_spot/mitsune.html#01
    >>> import io
    >>> stream = io.StringIO("国名,3文字コード\\nアメリカ合衆国,USA\\n日本,JPN\\n")
    >>> table = Table(stream)
    >>> table.write()
    国名,3文字コード
    アメリカ合衆国,USA
    日本,JPN

    Notes
    -----
    - ``is_tempfile`` に True を指定した場合、
      オブジェクト削除時に ``file`` が指すファイルも削除されます。
    - CSV データが UTF-8、カンマ区切りの CSV であることが
      確実な場合、 ``skip_cleaning`` に True を指定することで
      クリーニング処理をスキップして高速に処理できます。
      ``skip_cleaning`` を省略または False を指定した場合、
      一度 CSV データ全体を読み込んでクリーニングを行うため、
      余分なメモリと処理時間が必要になります。

    """

    codecs.register_error('escape_encoding', escape_encoding)

    def __init__(
            self,
            file,
            sheet: Optional[str] = None,
            is_tempfile: bool = False,
            skip_cleaning: bool = False):
        """
        オブジェクトを初期化します。
        ファイルは開きません。
        """
        self.file = file
        self.sheet = sheet
        self.is_tempfile = is_tempfile
        self.skip_cleaning = skip_cleaning
        self.filetype = "csv"
        self._reader = None

    def __del__(self):
        """
        オブジェクトを削除する前に呼び出されます。

        self.is_tempfile が True で、かつ self.file が指す
        ファイルが残っている場合、先にファイルを消去します。
        """
        if self.is_tempfile is True and \
                os.path.exists(self.file):
            os.remove(self.file)
            logger.debug("一時ファイル '{}' を削除しました".format(
                self.file))

    def __enter__(self):
        if self._reader is None:
            self.open()

        return self

    def __iter__(self):
        return self

    def __next__(self):
        return self._reader.__next__()

    def __exit__(self, exception_type, exception_value, traceback):
        return self._reader.__exit__(
            exception_type, exception_value, traceback)

    def open(
            self,
            as_dict: bool = False,
            **kwargs):
        """
        表データを開き、 csv.reader オブジェクトを返します。

        Parameters
        ----------
        as_dict: bool [False]
            True が指定された場合、 csv.DictReader
            オブジェクトを返します。
        kwargs: dict
            csv.reader, csv.DictReader に渡すその他のパラメータ。

        Returns
        -------
        csv.reader, csv.DictReader
            CSV データを1レコードずつ読み込むリーダー。

        Examples
        --------
        >>> from tablelinker import Table
        >>> table = Table("sample/hachijo_sightseeing.csv")
        >>> reader = table.open()
        >>> for row in reader:
        ...     print(",".join(row[0:4]))
        ...
        観光スポット名称,所在地,緯度,経度
        ホタル水路,,33.108218,139.80102
        登龍峠展望,,33.113154,139.835245
        八丈富士,,33.139168,139.762187
        永郷展望,,33.153559,139.747501
        ...

        Examples
        --------
        >>> from tablelinker import Table
        >>> table = Table("sample/hachijo_sightseeing.csv")
        >>> dictreader = table.open(as_dict=True)
        >>> for row in dictreader:
        ...     print(",".join([row[x] for x in [
        ...         "観光スポット名称", "所在地", "経度", "緯度"]]))
        ...
        ホタル水路,,139.80102,33.108218
        登龍峠展望,,139.835245,33.113154
        八丈富士,,139.762187,33.139168
        永郷展望,,139.747501,33.153559
        ...

        Notes
        -----
        - CSV、タブ区切りテキスト、 Excel に対応。
        - CSV データのクリーニングはこのメソッドが呼ばれたときに
          実行されます。
        """
        if not self.skip_cleaning:
            # エクセルファイルとして読み込む
            try:
                df = pd.read_excel(self.file, sheet_name=self.sheet)
                if self.sheet is None:
                    sheets = list(df.keys())
                    df = df[sheets[0]]

                data = df.to_csv(index=False)
                self._reader = core.CsvInputCollection(
                    file_or_path=io.StringIO(data),
                    skip_cleaning=True).open(
                        as_dict=as_dict, **kwargs)

                self.filetype = "excel"
                return self

            except ValueError as e:
                if str(e).lower().startswith(
                        "excel file format cannot be determined"):
                    # Excel ファイルではない
                    pass
                elif self.sheet is not None:
                    logger.error(
                        "対象にはシート '{}' は含まれていません。".format(
                            self.sheet))
                    raise ValueError("Invalid sheet name.")

        # CSV 読み込み
        self._reader = core.CsvInputCollection(
            self.file,
            skip_cleaning=self.skip_cleaning).open(
                as_dict=as_dict, **kwargs)

        self.filetype = "csv"
        return self

    @classmethod
    def useExtraConvertors(cls) -> None:
        """
        拡張コンバータを利用することを宣言します。

        Notes
        -----
        - ``tablelinker.useExtraConvertors()`` と等価です。

        """
        import tablelinker
        tablelinker.useExtraConvertors()

    @classmethod
    def fromPandas(cls, df: DataFrame) -> "Table":
        """
        Pandas DataFrame から Table オブジェクトを作成します。

        Parameters
        ----------
        df: pandas.core.frame.DataFrame
            CSV データを持つ Pandas DataFrame オブジェクト。

        Returns
        -------
        Table
            新しい Table オブジェクト。

        Examples
        --------
        >>> from tablelinker import Table
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "国名":["アメリカ合衆国","日本","中国"],
        ...     "3文字コード":["USA","JPN","CHN"],
        ... })
        >>> table = Table.fromPandas(df)
        >>> table.write()
        国名,3文字コード
        アメリカ合衆国,USA
        日本,JPN
        中国,CHN

        """
        table = None
        with tempfile.NamedTemporaryFile(
                mode="w+b", delete=False) as f:
            df.to_csv(f, index=False)
            table = Table(
                f.name,
                is_tempfile=True,
                skip_cleaning=True)

        return table

    def toPandas(self) -> DataFrame:
        """
        Table オブジェクトから Pandas DataFrame を作成します。

        Returns
        -------
        pandas.core.frame.DataFrame

        Examples
        --------
        >>> import pandas as pd
        >>> from tablelinker import Table
        >>> table = Table("sample/hachijo_sightseeing.csv")
        >>> df = table.toPandas()
        >>> df.columns
        Index(['観光スポット名称', '所在地', '緯度', '経度', '座標系',\
          '説明', '八丈町ホームページ記載'], dtype='object')

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

    def save(self, path: os.PathLike, encoding="utf-8", **fmtparams):
        """
        Table オブジェクトが管理する表データを csv.writer を利用して
        指定したパスのファイルに保存します。

        Parameters
        ----------
        path: os.PathLike
            保存する CSV ファイルのパス。
        encoding: str ["utf-8"]
            テキストエンコーディング。
        fmtparams: dict
            csv.writer に渡すフォーマットパラメータ。

        Examples
        --------
        >>> import csv
        >>> from tablelinker import Table
        >>> table = Table("sample/hachijo_sightseeing.csv")
        >>> table.save("hachijo_sightseeing_utf8.csv", quoting=csv.QUOTE_ALL)

        """
        with self.open() as reader, \
                open(path, mode="w", newline="",
                     encoding=encoding, errors="escape_encoding") as f:
            writer = csv.writer(f, **fmtparams)
            for row in reader:
                writer.writerow(row)

    def merge(self, path: os.PathLike):
        """
        Table オブジェクトが管理する表データを、
        指定したパスのファイルの後ろに結合 (merge) します。

        Parameters
        ----------
        path: os.PathLike
            保存する CSV ファイルのパス。

        Examples
        --------
        >>> import csv
        >>> from tablelinker import Table
        >>> table = Table("sample/shimabara_tourisum.csv")
        >>> table.merge("sample/katsushika_tourism.csv")

        """
        # 結合先ファイルの情報をチェック
        if not os.path.exists(path):
            logger.debug((
                "結合先のファイル '{}' が存在しないため"
                "そのまま出力します。").format(path))
            return self.save(path)

        target = Table(path, skip_cleaning=False)
        target_delimiter = ","
        target_encoding = "UTF-8"
        with target.open() as target_reader:
            if target.filetype != "csv":
                logger.error(
                    "結合先のファイル '{}' は CSV ではありません。".format(
                        path))
                raise RuntimeError("The merged file must be a CSV.")

            cc = target._reader._reader  # CSVCleaner
            target_delimiter = cc.delimiter
            target_encoding = cc.encoding
            target_header = target_reader.__next__()

        del target  # 結合先ファイルを閉じる

        # 結合先のファイルに列の順番をそろえる
        try:
            reordered = self.convert(
                convertor="reorder_cols",
                params={"column_list": target_header})
        except ValueError as e:
            logger.error(
                "結合先のファイルと列を揃える際にエラー。({})".format(
                    e))
            raise ValueError(e)

        # 結合先のファイルに追加出力
        with reordered.open() as reader, \
                open(path, mode="a", newline="",
                     encoding=target_encoding, errors="escape_encoding") as f:
            writer = csv.writer(f, delimiter=target_delimiter)
            reader.__next__()  # ヘッダ行をスキップ
            for row in reader:
                writer.writerow(row)

    def write(
            self,
            lines: int = -1,
            file=None,
            skip_header: bool = False,
            **fmtparams):
        """
        入力 CSV データを csv.writer を利用して
        指定したファイルオブジェクトに出力します。

        Parameters
        ----------
        lines: int [default:-1]
            出力する最大行数。
            省略された場合、または負の場合は全ての行を出力します。
        file: File-like オブジェクト [default: None]
            出力先のファイルオブジェクト。
            省略された場合または None が指定された場合は標準出力。
        skip_header: bool [default: False]
            見出し行をスキップする場合は True を指定します。
        fmtparams: dict
            csv.writer に渡すフォーマットパラメータ。

        Examples
        --------
        >>> import csv
        >>> from tablelinker import Table
        >>> table = Table("sample/hachijo_sightseeing.csv")
        >>> with open("hachijo_2.csv", "w", newline="") as f:
        ...     table.write(lines=2, file=f, quoting=csv.QUOTE_ALL)
        ...

        """
        if file is None:
            file = sys.stdout

        with self.open() as reader:
            writer = csv.writer(file, **fmtparams)
            if skip_header:
                reader.__next__()

            for n, row in enumerate(reader):
                if n == lines:
                    break

                writer.writerow(row)

    def apply(self, task: Task) -> 'Table':
        """
        テーブルが管理する表データにタスクを適用して変換し、
        変換結果を管理する新しい Table オブジェクトを返します。

        Parameters
        ----------
        task: Task
            適用するタスク。

        Returns
        -------
        Table
            変換結果を管理する Table オブジェクト。

        Examples
        --------
        >>> from tablelinker import Table, Task
        >>> table = Table("sample/hachijo_sightseeing.csv")
        >>> table.write(lines=1)
        観光スポット名称,所在地,緯度,経度,座標系,説明,八丈町ホームページ記載
        >>> task = Task.create({
        ...     "convertor":"rename_col",
        ...     "params":{"input_col_idx":"観光スポット名称", "output_col_name":"名称"},
        ... })
        >>> table = table.apply(task)
        >>> table.write(lines=1)
        名称,所在地,緯度,経度,座標系,説明,八丈町ホームページ記載

        """
        return self.convert(
            convertor=task.convertor,
            params=task.params)

    def convert(
            self,
            convertor: str,
            params: dict) -> 'Table':
        """
        テーブルが管理する表データにコンバータを適用して変換し、
        変換結果を管理する新しい Table オブジェクトを返します。

        Parameters
        ----------
        convertor: str
            適用するコンバータ名 (例: 'rename_col')。
        params: dict
            コンバータに渡すパラメータ名・値の辞書。
            例: {"input_col_idx": 1, "new_col_name": "番号"}

        Returns
        -------
        Table
            変換結果を管理する Table オブジェクト。

        Examples
        --------
        >>> from tablelinker import Table
        >>> table = Table("sample/hachijo_sightseeing.csv")
        >>> table.write(lines=1)
        観光スポット名称,所在地,緯度,経度,座標系,説明,八丈町ホームページ記載
        >>> table = table.convert(
        ...     convertor="rename_col",
        ...     params={"input_col_idx":0, "output_col_name":"名称"},
        ... )
        >>> table.write(lines=1)
        名称,所在地,緯度,経度,座標系,説明,八丈町ホームページ記載

        Notes
        -----
        - 変換結果はテンポラリディレクトリ (``/tmp/`` など) の下に
          ``table_`` から始まるファイル名を持つファイルに出力されます。
        - このメソッドが返す Table オブジェクトが削除される際に、
          変換結果ファイルも自動的に削除されます。
        - ただしエラーや中断により途中で停止した場合には、
          変換結果ファイルが残る場合があります。
        """
        self.open()
        csv_out = tempfile.NamedTemporaryFile(
            delete=False,
            prefix='table_').name
        input = self._reader
        output = core.CsvOutputCollection(csv_out)
        conv = core.convertor_find_by(convertor)
        if conv is None:
            # 拡張コンバータも読み込み、もう一度確認する
            self.useExtraConvertors()
            conv = core.convertor_find_by(convertor)

        if conv is None:
            raise ValueError("コンバータ '{}' は未登録です".format(
                convertor))

        with core.Context(
                convertor=conv,
                convertor_params=params,
                input=input,
                output=output) as context:
            try:
                conv().process(context)
                logger.debug((
                    "ファイル '{}' にコンバータ '{}' を適用し"
                    "一時ファイル '{}' に出力しました。").format(
                    self.file, convertor, csv_out))
                new_table = Table(
                    csv_out,
                    is_tempfile=True,
                    skip_cleaning=True)
                return new_table

            except RuntimeError as e:
                os.remove(csv_out)
                logger.debug((
                    "ファイル '{}' にコンバータ '{}' を適用中、"
                    "エラーのため一時ファイル '{}' を削除しました。").format(
                    self.file, convertor, csv_out))

                raise e
