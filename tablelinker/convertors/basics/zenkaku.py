from logging import getLogger

import jaconv

from ..core import filters, params

logger = getLogger(__name__)


class ToHankakuFilter(filters.InputOutputFilter):
    """
    概要
        全角文字を半角文字に変換します。

    コンバータ名
        "to_hankaku"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_idx": 分割した結果を出力する列番号または
          列名のリスト
        * "output_attr_name": 結果を出力する列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "kana": カナ文字を変換対象に含める [True]
        * "ascii": アルファベットと記号を対象に含める [True]
        * "digit": 数字を対象に含める [True]
        * "ignore_chars": 対象に含めない文字 [""]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈
        - 変換処理は列名には適用されません。

    サンプル
        「説明」列に含まれる全角数字を半角数字に置き換えます。

        .. code-block :: json

            {
                "convertor": "to_hankaku",
                "params": {
                    "input_attr_idx": "説明",
                    "output_attr_idx": "説明",
                    "kana": false,
                    "ascii": false,
                    "digit": true,
                    "overwrite": true
                }
            }

    """

    class Meta:
        key = "to_hankaku"
        name = "全角→半角変換"
        description = """
          全角文字を半角文字に変換します
          """
        help_text = None
        params = params.ParamSet(
            params.BooleanParam(
                "kana",
                label="カナ文字を対象に含める",
                required=False,
                default_value=True,
            ),
            params.BooleanParam(
                "ascii",
                label="アルファベットと記号を対象に含める",
                required=False,
                default_value=True,
            ),
            params.BooleanParam(
                "digit",
                label="数字を対象に含める",
                required=False,
                default_value=True,
            ),
            params.StringParam(
                "ignore_chars",
                label="対象に含めない文字",
                required=False,
                default_value="",
            ),
        )

    def initial_context(self, context):
        super().initial_context(context)
        self.kana = context.get_param("kana")
        self.ascii = context.get_param("ascii")
        self.digit = context.get_param("digit")
        self.ignore_chars = context.get_param("ignore_chars")

    def process_filter(self, record, context):
        return jaconv.z2h(
            record[self.input_attr_idx],
            kana=self.kana,
            ascii=self.ascii,
            digit=self.digit,
            ignore=self.ignore_chars)


class ToZenkakuFilter(filters.InputOutputFilter):
    """
    概要
        半角文字を全角文字に変換します。

    コンバータ名
        "to_zenkaku"

    パラメータ（InputOutputFilter 共通）
        * "input_attr_idx": 対象列の列番号または列名 [必須]
        * "output_attr_idx": 分割した結果を出力する列番号または
          列名のリスト
        * "output_attr_name": 結果を出力する列名
        * "overwrite": 既に値がある場合に上書きするかどうか [False]

    パラメータ（コンバータ固有）
        * "kana": カナ文字を変換対象に含める [True]
        * "ascii": アルファベットと記号を対象に含める [True]
        * "digit": 数字を対象に含める [True]
        * "ignore_chars": 対象に含めない文字 [""]

    注釈（InputOutputFilter 共通）
        - ``output_attr_name`` が省略された場合、
          ``input_attr_idx`` 列の列名が出力列名として利用されます。
        - ``output_attr_idx`` が省略された場合、
          出力列名が存在する列名ならばその列の位置に出力し、
          存在しないならば最後尾に追加します。

    注釈
        - 変換処理は列名には適用されません。

    サンプル
        「所在地」列に含まれる半角文字を全角文字に置き換えます。

        .. code-block :: json

            {
                "convertor": "to_zenkaku",
                "params": {
                    "input_attr_idx": "所在地",
                    "output_attr_idx": "所在地",
                    "kana": true,
                    "ascii": true,
                    "digit": true,
                    "overwrite": true
                }
            }

    """

    class Meta:
        key = "to_zenkaku"
        name = "半角→全角変換"
        description = "半角文字を全角文字に変換します"
        help_text = None
        params = params.ParamSet(
            params.BooleanParam(
                "kana",
                label="カナ文字を対象に含める",
                required=False,
                default_value=True,
            ),
            params.BooleanParam(
                "ascii",
                label="アルファベットと記号を対象に含める",
                required=False,
                default_value=True,
            ),
            params.BooleanParam(
                "digit",
                label="数字を対象に含める",
                required=False,
                default_value=True,
            ),
            params.StringParam(
                "ignore_chars",
                label="対象に含めない文字",
                required=False,
                default_value="",
            ),
        )

    def initial_context(self, context):
        super().initial_context(context)
        self.kana = context.get_param("kana")
        self.ascii = context.get_param("ascii")
        self.digit = context.get_param("digit")
        self.ignore_chars = context.get_param("ignore_chars")

    def process_filter(self, record, context):
        return jaconv.h2z(
            record[self.input_attr_idx],
            kana=self.kana,
            ascii=self.ascii,
            digit=self.digit,
            ignore=self.ignore_chars)
