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


logger = getLogger(__name__)
basic_convertors.register()


class Table(object):
    """
    表形式 CSV データを管理するクラス。

    Attributes
    ----------
    file: File-like, Path-like
        このテーブルが管理する入力 CSV ファイルのパス、
        または file-like オブジェクト。
    sheet: str, None
        入力ファイルが Excel の場合など、複数の表データを含む場合に
        対象を指定するためのシート名。省略された場合は最初の表。
    is_tempfile: bool
        入力 CSV ファイルが一時ファイルかどうかを表すフラグ。
        True の場合、オブジェクトが消滅するときに file が
        指すパスにあるファイルも削除する。
    skip_cleaning: bool
        CSV データを読み込む際にクリーニングをスキップするか
        どうかを指定するフラグ。
        True を指定した場合、 UTF-8 でカンマ区切りの CSV ファイルで
        先頭部分に余計な行が含まれていない必要がある。

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
      オブジェクト削除時に ``file`` が指すファイルも削除される。
    - CSV データが UTF-8、カンマ区切りの CSV であることが
      確実な場合、 ``skip_cleaning`` に True を指定することで
      クリーニング処理をスキップして高速に処理できる。
      ``skip_cleaning`` を省略または False を指定した場合、
      一度 CSV データ全体を読み込んでクリーニングを行うため、
      余分なメモリと処理時間が必要になる。

    """

    def __init__(
            self,
            file,
            sheet: Optional[str] = None,
            is_tempfile: bool = False,
            skip_cleaning: bool = False):
        """
        オブジェクトを初期化する。
        ファイルは開かない。

        Parameters
        ----------
        file: os.PathLike
            表形式 CSV データを含むファイルのパス、または
            CSV データを読みだせる file-like オブジェクト。
        sheet: str, optional (default:None)
            入力データに複数のシートが含まれる場合、対象とするシート名。
            省略した場合、最初のシートを利用する。
        is_tempfile: bool (default:False)
            参照しているファイルが一時ファイルかどうかを
            指定するフラグ。
        skip_cleaning: bool (default:False)
            CSV データを読み込む際にクリーニングをスキップするか
            どうかを指定するフラグ。
        """
        self.file = file
        self.sheet = sheet
        self.is_tempfile = is_tempfile
        self.skip_cleaning = skip_cleaning
        self._reader = None

    def __del__(self):
        """
        一時ファイルの CSV ファイルが残っている場合、
        このオブジェクトの削除と同時にファイルも消去する。
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
        表データを開き、 csv.reader オブジェクトを返す。

        Parameters
        ----------
        as_dict: bool [False]
            True が指定された場合、 csv.DictReader
            オブジェクトを返す。
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
          実行される。
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
        return self

    @classmethod
    def useExtraConvertors(cls) -> None:
        """
        拡張コンバータを利用することを宣言する。

        Notes
        -----
        - ``tablelinker.useExtraConvertors()`` と等価。

        """
        import tablelinker
        tablelinker.useExtraConvertors()

    @classmethod
    def fromPandas(cls, df: DataFrame) -> "Table":
        """
        Pandas DataFrame から Table オブジェクトを作成する。

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
        Table オブジェクトから Pandas DataFrame を作成する。

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
        Index(['観光スポット名称', '所在地', '緯度', '経度', '座標系', '説明', '八丈町ホームページ記載'], dtype='object')

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
        入力 CSV データを csv.writer を利用して
        指定したパスのファイルに保存する。

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
                open(path, mode="w", newline="", encoding=encoding) as f:
            writer = csv.writer(f, **fmtparams)
            for row in reader:
                writer.writerow(row)

    def write(self, lines: int = -1, file=None, **fmtparams):
        """
        入力 CSV データを csv.writer を利用して
        指定したファイルオブジェクトに出力する。

        Parameters
        ----------
        lines: int [default:-1]
            出力する最大行数。
            省略された場合、または負の場合は全ての行を出力する。
        file: File-like オブジェクト [default: None]
            出力先のファイルオブジェクト。
            省略された場合または None が指定された場合は標準出力。
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
            for n, row in enumerate(reader):
                if n == lines:
                    break

                writer.writerow(row)

    def convert(
            self,
            convertor: str,
            params: dict) -> 'Table':
        """
        入力 CSV データにフィルタを適用して変換する。
        変換結果を管理する Table オブジェクトを返す。

        Parameters
        ----------
        convertor: str
            適用するコンバータ名 (例: 'rename_col')。
        params: dict
            コンバータに渡すパラメータ名・値の辞書。
            例: {"input_attr_idx": 1, "new_col_name": "番号"}

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
        ...     params={"input_attr_idx":0, "new_col_name":"名称"},
        ... )
        >>> table.write(lines=1)
        名称,所在地,緯度,経度,座標系,説明,八丈町ホームページ記載

        Notes
        -----
        - 変換結果はテンポラリディレクトリ (``/tmp/`` など) の下に
          ``table_`` から始まるファイル名を持つファイルに出力される。
        - このメソッドが返す Table オブジェクトが削除される際に、
          変換結果ファイルも自動的に削除される。
        - ただしエラーや中断により途中で停止した場合には、
          変換結果ファイルが残る場合がある。
        - 利用できるコンバータのリストは自動的に読み込む。
        """
        self.open()
        csv_out = tempfile.NamedTemporaryFile(
            delete=False,
            prefix='table_').name
        input = self._reader
        output = core.CsvOutputCollection(csv_out)
        filter = core.filter_find_by(convertor)
        if filter is None:
            # 拡張コンバータも読み込み、もう一度確認する
            self.useExtraConvertors()
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
