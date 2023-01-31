import datetime
import re

from jeraconv import jeraconv

from ..core import filters, params
from ..core.date_extractor import get_datetime


class DatetimeExtractFilter(filters.InputOutputFilter):
    """
    概要
        文字列から日時を抽出します。

    コンバータ名
        "datetime_extract"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_name": 結果を出力する列名
        * "output_attr_idx": 分割した結果を出力する列番号または列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "format": 日時フォーマット ["%Y-%m-%d %H:%M:%S"]
        * "default": 日時が抽出できなかった場合の値 [""]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈（コンバータ固有）
        - ``format`` は `strftime() と strptime() の書式コード <https://docs.python.org/ja/3/library/datetime.html#strftime-and-strptime-format-codes>`_
          のコードで記述してください。
        - ``format`` で指定した項目が抽出できない場合（たとえば ``%Y`` が
          含まれているけれど列の値が "1月1日" で年が分からないなど）、
          ``default`` の値が出力されます。

    サンプル
        「開催期間」列から開催開始日を抽出します。

        .. code-block :: json

            {
                "convertor": "datetime_extract",
                "params": {
                    "input_attr_idx": "開催期間",
                    "output_attr_name": "開催年月日",
                    "overwrite": false
                }
            }

    """

    class Meta:
        key = "datetime_extract"
        name = "日時抽出"
        description = """
        日時表現を抽出します。
        """
        help_text = None
        params = params.ParamSet(
            params.StringParam(
                "format",
                label="日時フォーマット",
                required=False,
                default_value="%Y-%m-%d %H:%M:%S",
                help_text="日時フォーマット"),
            params.StringParam(
                "default",
                label="デフォルト値",
                required=False,
                default_value="",
                help_text="日時が抽出できない場合の値。"),
        )

    def initial_context(self, context):
        super().initial_context(context)

        self.format = context.get_param("format")
        self.default = context.get_param("default")

    def process_filter(self, record, context):
        extracted = get_datetime(record[self.input_attr_idx])
        if len(extracted["datetime"]) == 0:
            return self.default

        format = self.format
        result = self.default
        for dt in extracted["datetime"]:
            try:
                if dt[0] is None:  # 年が空欄
                    dt[0] = 1
                    for p in ("%y", "%Y", ):
                        if p in format:
                            raise ValueError("年が必要です。")

                if dt[1] is None:  # 月が空欄
                    dt[1] = 1
                    for p in ("%b", "%B", "%m",):
                        if p in format:
                            raise ValueError("月が必要です。")

                if dt[2] is None:  # 日が空欄
                    dt[2] = 1
                    for p in ("%a", "%A", "%w", "%d",):
                        if p in format:
                            raise ValueError("日が必要です。")

                if dt[3] is None:  # 時が空欄
                    dt[3] = 0
                    for p in ("%H", "%I", "%p",):
                        if p in format:
                            raise ValueError("時が必要です。")

                if dt[4] is None:  # 分が空欄
                    dt[4] = 0
                    for p in ("%M",):
                        if p in format:
                            raise ValueError("分が必要です。")

                if dt[5] is None:  # 秒が空欄
                    dt[5] = 0
                    for p in ("%S",):
                        if p in format:
                            raise ValueError("秒が必要です。")

                result = datetime.datetime(
                    year=dt[0],
                    month=dt[1],
                    day=dt[2],
                    hour=dt[3],
                    minute=dt[4],
                    second=dt[5]).strftime(format)

            except ValueError:
                pass

            if result != self.default:
                break

        return result


class DateExtractFilter(filters.InputOutputFilter):
    """
    概要
        文字列から日付を抽出します。

    コンバータ名
        "date_extract"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_name": 結果を出力する列名
        * "output_attr_idx": 分割した結果を出力する列番号または列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "format": 日時フォーマット ["%Y-%m-%d"]
        * "default": 日時が抽出できなかった場合の値 [""]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈（コンバータ固有）
        - ``format`` は `strftime() と strptime() の書式コード <https://docs.python.org/ja/3/library/datetime.html#strftime-and-strptime-format-codes>`_
          のコードで記述してください。
        - ``format`` 時分秒を指定すると常に 0 になります。
        - ``format`` で指定した項目が抽出できない場合（たとえば ``%Y`` が
          含まれているけれど列の値が "1月1日" で年が分からないなど）、
          ``default`` の値が出力されます。

    サンプル
        「開催期間」列から開催開始日を抽出します。

        .. code-block :: json

            {
                "convertor": "date_extract",
                "params": {
                    "input_attr_idx": "開催期間",
                    "output_attr_name": "開催年月日",
                    "overwrite": false
                }
            }

    """

    class Meta:
        key = "date_extract"
        name = "日付抽出"
        description = """
        日付を抽出します。
        """
        help_text = None
        params = params.ParamSet(
            params.StringParam(
                "format",
                label="日付フォーマット",
                required=False,
                default_value="%Y-%m-%d",
                help_text="日付フォーマット"),
            params.StringParam(
                "default",
                label="デフォルト値",
                required=False,
                default_value="",
                help_text="日付が抽出できない場合の値。"),
        )

    def initial_context(self, context):
        super().initial_context(context)

        self.format = context.get_param("format")
        self.default = context.get_param("default")

    def process_filter(self, record, context):
        extracted = get_datetime(record[self.input_attr_idx])
        if len(extracted["datetime"]) == 0:
            return self.default

        format = self.format
        result = self.default
        for dt in extracted["datetime"]:
            try:
                if dt[0] is None:  # 年が空欄
                    dt[0] = 1
                    for p in ("%y", "%Y", ):
                        if p in format:
                            raise ValueError("年が必要です。")

                if dt[1] is None:  # 月が空欄
                    dt[1] = 1
                    for p in ("%b", "%B", "%m",):
                        if p in format:
                            raise ValueError("月が必要です。")

                if dt[2] is None:  # 日が空欄
                    dt[2] = 1
                    for p in ("%a", "%A", "%w", "%d",):
                        if p in format:
                            raise ValueError("日が必要です。")

                result = datetime.date(
                    year=dt[0],
                    month=dt[1],
                    day=dt[2]).strftime(format)

            except ValueError:
                pass

            if result != self.default:
                break

        return result
