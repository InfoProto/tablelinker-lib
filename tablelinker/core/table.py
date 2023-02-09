import codecs
from collections import OrderedDict
import csv
import io
from logging import getLogger
import math
import os
import sys
import tempfile
from typing import List, Optional

import pandas as pd
from pandas.core.frame import DataFrame

from ..convertors import basics as basic_convertors
from .context import Context
from .convertors import convertor_find_by
from .input import CsvInputCollection
from .mapping import ItemsPair
from .output import CsvOutputCollection
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
    表形式データを管理するクラスです。

    Parameters
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
        True を指定した場合、 file で指定したファイルは
        文字エンコーディングが UTF-8（BOM無し）、区切り文字はカンマ、
        先頭部分に説明などの余計な行が含まれていない
        CSV ファイルである必要があります。

    Attributes
    ----------
    file: File-like, Path-like
        パラメータ参照。
    sheet: str, optional
        パラメータ参照。
    is_tempfile: bool
        パラメータ参照。
    skip_cleaning: bool
        パラメータ参照。
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
    - Excel ファイルのシートを開きたい場合、
      ``sheet`` オプションでシート名を指定します。 ::

          table = Table(ファイル名, sheet=シート名)

    - ``is_tempfile`` に True を指定した場合、
      オブジェクト削除時に ``file`` が指すファイルも削除されます。
    - CSV データが UTF-8、カンマ区切りの CSV であることが
      分かっている場合、 ``skip_cleaning`` に True を指定することで
      クリーニング処理をスキップして高速に処理できます。

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

        Notes
        -----
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
            del self._reader
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
        表データを開きます。既に開いている場合、先頭に戻します。

        Parameters
        ----------
        as_dict: bool [False]
            True が指定された場合、 csv.DictReader
            オブジェクトを返します。
        kwargs: dict
            csv.reader, csv.DictReader に渡すその他のパラメータ。

        Returns
        -------
        Table
            自分自身を返します。
            Table はジェネレータ・イテレータインタフェースを
            備えているので、サンプルのように for 文で行を順番に
            読みだしたり、 with 構文でバインドすることができます。

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
        >>> with table.open(as_dict=True) as dictreader:
        >>>     for row in dictreader:
        >>>         print(",".join([row[x] for x in [
        ...             "観光スポット名称", "所在地", "経度", "緯度"]]))
        ...
        ホタル水路,,139.80102,33.108218
        登龍峠展望,,139.835245,33.113154
        八丈富士,,139.762187,33.139168
        永郷展望,,139.747501,33.153559
        ...

        Notes
        -----
        - CSV、タブ区切りテキスト、 Excel に対応しています。
        - 表データの確認とクリーニングは、このメソッドが
          呼ばれたときに実行されます。
        """
        if not self.skip_cleaning:
            # エクセルファイルとして読み込む
            try:
                df = pd.read_excel(self.file, sheet_name=self.sheet)
                if self.sheet is None:
                    sheets = list(df.keys())
                    df = df[sheets[0]]

                data = df.to_csv(index=False)
                self._reader = CsvInputCollection(
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
        self._reader = CsvInputCollection(
            self.file,
            skip_cleaning=self.skip_cleaning).open(
                as_dict=as_dict, **kwargs)

        self.filetype = "csv"
        return self

    def get_reader(self):
        """
        管理している表データへの reader オブジェクトを取得します。

        Returns
        -------
        csv.reader, csv.DictReader
            reader オブジェクト。ただし ``open()`` を実行する前は
            ``None`` を返します。

        """
        if self._reader is not None:
            return self._reader.get_reader()

        return None

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

        Notes
        -----
        このメソッドは、一度 DataFrame のすべてのデータを
        CSV ファイルに出力します。
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
        >>> table = Table("hachijo_sightseeing.xslx")
        >>> df = table.toPandas()
        >>> df.columns
        Index(['観光スポット名称', '所在地', '緯度', '経度', '座標系',\
          '説明', '八丈町ホームページ記載'], dtype='object')

        """
        with self.open(as_dict=True) as reader:
            df = pd.DataFrame.from_records(reader)

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

        Notes
        -----
        - 結合先ファイルの列の順番に合わせて並べ替えます。
        - 文字エンコーディングも結合先ファイルに合わせます。
        - 見出し行は出力しません。

        """
        # 結合先ファイルの情報をチェック
        if not os.path.exists(path):
            logger.debug((
                "結合先のファイル '{}' が存在しないため、"
                "そのまま保存します。").format(path))
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


    def to_str(self, **kwargs):
        """
        write() を利用して、クリーンな CSV 文字列を返します。

        Parameters
        ----------
        **kwargs: dict
            write() に渡すパラメータを指定します。

        Returns
        -------
        str
            CSV 文字列を含む文字列。

        Notes
        -----
        このメソッドはメモリ上に表データのコピーを作成します。
        """
        buf = io.StringIO()
        self.write(file=buf, **kwargs)

        return buf.getvalue()

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

        Notes
        -----
        convert がコンバータ名とパラメータを指定するのに対し、
        apply はタスクオブジェクトを指定する点が違うだけで
        処理内容は同一です。
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
        output = CsvOutputCollection(csv_out)
        conv = convertor_find_by(convertor)
        if conv is None:
            # 拡張コンバータも読み込み、もう一度確認する
            self.useExtraConvertors()
            conv = convertor_find_by(convertor)

        if conv is None:
            raise ValueError("コンバータ '{}' は未登録です".format(
                convertor))

        with Context(
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

    def mapping(
            self,
            template: "Table",
            threshold: Optional[int] = None) -> dict:
        """
        他のテーブル（テンプレート）に変換するための
        対応表を生成します。

        Parameters
        -----------
        template: Table
            変換対象のテーブルオブジェクト。
        threshold: int, optional
            一致する列と判定する際のしきい値。0-100 で指定し、
            0 の場合が最も緩く、100の場合は完全一致した場合しか
            対応しているとみなしません。

        Returns
        -------
        dict
            キーに変換先テーブルの列名、値にその列に対応すると
            判定された自テーブルの列名を持つ dict を返します。

        Notes
        -----
        結果の dict はコンバータ mapping_cols の column_map
        パラメータにそのまま利用できます。

        .. code-block: python

            map = table.mapping(template)
            mapped_table = table.convert(
                convertor="mapping_cols",
                params={"column_map": map},
            )

        """
        threshold = 20 if threshold is None else threshold  # デフォルトは 20

        # テンプレート CSV の見出し行を取得
        with template.open() as reader:
            template_headers = reader.__next__()

        return self.mapping_with_headers(
            headers=template_headers,
            threshold=threshold)

    def mapping_with_headers(
            self,
            headers: List[str],
            threshold: Optional[int] = None) -> dict:
        """
        テンプレートの見出し列に一致するように変換するための
        対応表を生成します。

        Parameters
        -----------
        headers: List[str]
            テンプレートの見出し列。
        threshold: int, optional
            一致する列と判定する際のしきい値。0-100 で指定し、
            0 の場合が最も緩く、100の場合は完全一致した場合しか
            対応しているとみなしません。

        Returns
        -------
        dict
            キーに変換先テーブルの列名、値にその列に対応すると
            判定された自テーブルの列名を持つ dict を返します。

        Notes
        -----
        結果の dict はコンバータ mapping_cols の column_map
        パラメータにそのまま利用できます。

        .. code-block: python

            map = table.mapping(template)
            mapped_table = table.convert(
                convertor="mapping_cols",
                params={"column_map": map},
            )

        """
        threshold = 20 if threshold is None else threshold  # デフォルトは 20
        logger.debug("しきい値： {}".format(threshold))

        # 自テーブルの見出し行を取得
        with self.open() as reader:
            my_headers = reader.__next__()

        # 項目マッピング
        pair = ItemsPair(headers, my_headers)
        mapping = OrderedDict()
        for result in pair.mapping():
            output, header, score = result
            logger.debug("対象列：{}, 対応列：{}, 一致スコア:{:3d}".format(
                output, header, int(score * 100.0)))
            if output is None:
                # マッピングされなかったカラムは除去
                continue

            if header is None:
                mapping[output] = None
            elif math.ceil(score * 100.0) < threshold:
                mapping[output] = None
            else:
                mapping[output] = header

        return dict(mapping)
